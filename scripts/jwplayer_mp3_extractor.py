#!/usr/bin/env python3
"""
JWPlayer MP3 Extractor for Congress Hearings
Specialized tool for extracting audio from JWPlayer implementations (87.5% of Congress video formats)
"""
import sys
import os
import time
import json
import re
import subprocess
import tempfile
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import CongressVideoDatabase


class JWPlayerMP3Extractor:
    """Specialized extractor for JWPlayer-based Congress hearings."""
    
    def __init__(self, headless=True):
        """Initialize the extractor with Selenium WebDriver."""
        self.driver = self.setup_selenium(headless)
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'extracted_audio')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_selenium(self, headless=True):
        """Set up Selenium WebDriver for JavaScript execution."""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Enable performance logging to catch network requests
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        
        caps = options.to_capabilities()
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Error setting up Selenium: {e}")
            print("Make sure ChromeDriver is installed: pip install webdriver-manager")
            return None
    
    def extract_jwplayer_config(self, url, timeout=30):
        """Extract JWPlayer configuration from a webpage."""
        if not self.driver:
            return None
        
        print(f"Loading page: {url}")
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Give additional time for JWPlayer to initialize
            time.sleep(5)
            
            # Try multiple methods to extract JWPlayer config
            config = self.try_extract_methods(url)
            
            return config
            
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            return None
    
    def try_extract_methods(self, url):
        """Try multiple methods to extract JWPlayer stream URLs."""
        methods = [
            self.extract_from_jwplayer_instance,
            self.extract_from_page_source,
            self.extract_from_network_logs,
            self.extract_from_dom_search
        ]
        
        for method in methods:
            try:
                result = method()
                if result:
                    print(f"Success with method: {method.__name__}")
                    return result
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
                continue
        
        return None
    
    def extract_from_jwplayer_instance(self):
        """Extract from active JWPlayer instance via JavaScript."""
        script = """
        // Method 1: Direct JWPlayer instance
        if (typeof jwplayer !== 'undefined' && jwplayer().getConfig) {
            var config = jwplayer().getConfig();
            if (config && config.playlist && config.playlist.length > 0) {
                return {
                    method: 'jwplayer_instance',
                    config: config,
                    sources: config.playlist[0].sources
                };
            }
        }
        
        // Method 2: Multiple player instances
        if (typeof jwplayer !== 'undefined' && jwplayer.api) {
            var players = jwplayer.api.getPlayers();
            for (var i = 0; i < players.length; i++) {
                var config = players[i].getConfig();
                if (config && config.playlist) {
                    return {
                        method: 'jwplayer_api',
                        config: config,
                        sources: config.playlist[0].sources
                    };
                }
            }
        }
        
        return null;
        """
        
        result = self.driver.execute_script(script)
        if result and result.get('sources'):
            return self.parse_sources(result['sources'])
        
        return None
    
    def extract_from_page_source(self):
        """Extract from page source by parsing JavaScript."""
        page_source = self.driver.page_source
        
        # Look for JWPlayer setup calls
        patterns = [
            r'jwplayer\([^)]*\)\.setup\(({[^}]+})\)',
            r'playerInstance\.setup\(({[^}]+})\)',
            r'"sources":\s*(\[[^\]]+\])',
            r"'sources':\s*(\[[^\]]+\])",
            r'file":\s*"([^"]+)"',
            r"file':\s*'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            for match in matches:
                if self.looks_like_stream_url(match):
                    return {'method': 'page_source', 'url': match}
        
        return None
    
    def extract_from_network_logs(self):
        """Extract from browser network logs."""
        logs = self.driver.get_log('performance')
        stream_urls = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response['url']
                    mime_type = response.get('mimeType', '')
                    
                    # Look for video/audio streams
                    if (any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.ts', '.aac', '.mp3']) or
                        'video' in mime_type.lower() or 'audio' in mime_type.lower()):
                        stream_urls.append({
                            'method': 'network_logs',
                            'url': url,
                            'mime_type': mime_type
                        })
            except:
                continue
        
        if stream_urls:
            return stream_urls[0]  # Return first found stream
        
        return None
    
    def extract_from_dom_search(self):
        """Search DOM for video/audio elements and data attributes."""
        script = """
        var results = [];
        
        // Look for video/audio elements
        var videos = document.querySelectorAll('video, audio');
        for (var i = 0; i < videos.length; i++) {
            if (videos[i].src) {
                results.push({
                    method: 'dom_video_element',
                    url: videos[i].src,
                    element: videos[i].tagName
                });
            }
        }
        
        // Look for data attributes that might contain stream URLs
        var elements = document.querySelectorAll('[data-file], [data-src], [data-video], [data-stream]');
        for (var i = 0; i < elements.length; i++) {
            var el = elements[i];
            ['data-file', 'data-src', 'data-video', 'data-stream'].forEach(function(attr) {
                var value = el.getAttribute(attr);
                if (value && (value.includes('.mp4') || value.includes('.m3u8'))) {
                    results.push({
                        method: 'dom_data_attribute',
                        url: value,
                        attribute: attr
                    });
                }
            });
        }
        
        return results.length > 0 ? results[0] : null;
        """
        
        return self.driver.execute_script(script)
    
    def parse_sources(self, sources):
        """Parse JWPlayer sources array to extract stream URLs."""
        if not sources:
            return None
        
        # Handle different source formats
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict) and 'file' in source:
                    return {
                        'method': 'jwplayer_sources',
                        'url': source['file'],
                        'type': source.get('type', 'unknown')
                    }
        
        return None
    
    def looks_like_stream_url(self, text):
        """Check if text looks like a streaming URL."""
        if not isinstance(text, str):
            return False
        
        stream_indicators = [
            '.mp4', '.m3u8', '.ts', '.aac', '.mp3', '.wav',
            'manifest', 'playlist', 'stream'
        ]
        
        return any(indicator in text.lower() for indicator in stream_indicators)
    
    def extract_audio_with_ffmpeg(self, stream_url, output_filename):
        """Extract audio from stream URL using ffmpeg."""
        if not stream_url:
            return None
        
        print(f"Extracting audio from: {stream_url}")
        
        # Create output path
        output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
        
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', stream_url,
            '-vn',  # No video
            '-acodec', 'mp3',
            '-ab', '192k',  # 192kbps bitrate
            '-ar', '44100',  # Sample rate
            '-y',  # Overwrite output
            output_path
        ]
        
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"Successfully extracted audio to: {output_path}")
                return output_path
            else:
                print(f"FFmpeg error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("FFmpeg timeout - file may be too large")
            return None
        except Exception as e:
            print(f"FFmpeg exception: {e}")
            return None
    
    def process_committee_url(self, committee_name, committee_url):
        """Process a single committee URL for video extraction."""
        print(f"\n{'='*60}")
        print(f"Processing: {committee_name}")
        print(f"URL: {committee_url}")
        print(f"{'='*60}")
        
        # Extract JWPlayer config
        config = self.extract_jwplayer_config(committee_url)
        
        if not config:
            print(f"No video streams found for {committee_name}")
            return None
        
        print(f"Found stream with method: {config.get('method', 'unknown')}")
        
        # Extract audio
        stream_url = config.get('url')
        if stream_url:
            # Create safe filename
            safe_name = re.sub(r'[^\w\-_\.]', '_', committee_name)
            output_file = self.extract_audio_with_ffmpeg(stream_url, safe_name)
            
            if output_file:
                # Save metadata
                metadata = {
                    'committee': committee_name,
                    'source_url': committee_url,
                    'stream_url': stream_url,
                    'extraction_method': config.get('method'),
                    'output_file': output_file,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                metadata_file = output_file.replace('.mp3', '_metadata.json')
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return output_file
        
        return None
    
    def process_all_committees(self):
        """Process all committees from the database."""
        # Load committee database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'congress_video.db')
        db = CongressVideoDatabase(db_path)
        
        committees = db.get_committees()
        
        print(f"Processing {len(committees)} committees...")
        
        success_count = 0
        results = []
        
        for committee in committees[:5]:  # Test with first 5 committees
            try:
                result = self.process_committee_url(committee.name, committee.official_url)
                if result:
                    success_count += 1
                    results.append({
                        'committee': committee.name,
                        'chamber': committee.chamber,
                        'success': True,
                        'output_file': result
                    })
                else:
                    results.append({
                        'committee': committee.name,
                        'chamber': committee.chamber,
                        'success': False,
                        'output_file': None
                    })
                
                # Respectful delay between requests
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing {committee.name}: {e}")
                results.append({
                    'committee': committee.name,
                    'chamber': committee.chamber,
                    'success': False,
                    'error': str(e)
                })
        
        print(f"\n{'='*60}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['committee']} ({result['chamber']})")
        
        return results
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()


def main():
    """Main function for testing the extractor."""
    print("JWPlayer MP3 Extractor for Congress Hearings")
    print("=" * 50)
    
    # Test with a specific committee
    extractor = JWPlayerMP3Extractor(headless=False)  # Set to True for production
    
    try:
        # Process all committees
        results = extractor.process_all_committees()
        
        # Summary
        print(f"\nExtraction completed!")
        print(f"Check output directory: {extractor.output_dir}")
        
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user")
    except Exception as e:
        print(f"Extraction error: {e}")
    finally:
        extractor.cleanup()


if __name__ == '__main__':
    main()