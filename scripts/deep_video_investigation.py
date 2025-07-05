#!/usr/bin/env python3
"""
Deep investigation of specific Senate committees to find actual video formats and endpoints.
"""
import sys
import os
import time
import json
import re
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.helpers import WebScraper


class DeepVideoInvestigator:
    """Deep investigation tool for finding actual video formats and endpoints."""
    
    def __init__(self):
        """Initialize the investigator."""
        self.setup_selenium()
        self.setup_session()
        
    def setup_selenium(self):
        """Set up Selenium with network logging capabilities."""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Enable performance and network logging
        options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        # Enable network domain for intercepting requests
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Enable network tracking
        self.driver.execute_cdp_cmd('Network.enable', {})
        self.driver.execute_cdp_cmd('Page.enable', {})
    
    def setup_session(self):
        """Set up requests session for direct HTTP analysis."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def investigate_committee(self, committee_name, committee_url):
        """Deeply investigate a committee's video infrastructure."""
        print(f"\n{'='*80}")
        print(f"DEEP INVESTIGATION: {committee_name}")
        print(f"URL: {committee_url}")
        print(f"{'='*80}")
        
        results = {
            'committee': committee_name,
            'url': committee_url,
            'investigation_methods': [],
            'video_formats_found': [],
            'streaming_endpoints': [],
            'underlying_formats': [],
            'technical_details': {}
        }
        
        # Method 1: Direct page analysis
        print("\n1. ANALYZING MAIN COMMITTEE PAGE...")
        main_page_analysis = self.analyze_main_page(committee_url)
        results['investigation_methods'].append('main_page_analysis')
        results['technical_details']['main_page'] = main_page_analysis
        
        # Method 2: Look for hearings/video pages
        print("\n2. SEARCHING FOR HEARING PAGES...")
        hearing_pages = self.find_hearing_pages(committee_url)
        results['investigation_methods'].append('hearing_page_discovery')
        results['technical_details']['hearing_pages'] = hearing_pages
        
        # Method 3: Deep network analysis of video pages
        print("\n3. DEEP NETWORK ANALYSIS OF VIDEO CONTENT...")
        for hearing_url in hearing_pages[:3]:  # Analyze first 3 hearing pages
            print(f"   Analyzing: {hearing_url}")
            video_analysis = self.deep_video_analysis(hearing_url)
            if video_analysis:
                results['video_formats_found'].extend(video_analysis.get('formats', []))
                results['streaming_endpoints'].extend(video_analysis.get('endpoints', []))
                results['underlying_formats'].extend(video_analysis.get('underlying_formats', []))
        
        # Method 4: Check for common video paths
        print("\n4. CHECKING COMMON VIDEO PATHS...")
        common_paths = self.check_common_video_paths(committee_url)
        results['investigation_methods'].append('common_path_check')
        results['technical_details']['common_paths'] = common_paths
        
        return results
    
    def analyze_main_page(self, url):
        """Analyze the main committee page for video indicators."""
        try:
            self.driver.get(url)
            time.sleep(5)
            
            page_source = self.driver.page_source
            
            analysis = {
                'video_players_detected': [],
                'javascript_libraries': [],
                'embedded_content': [],
                'streaming_indicators': []
            }
            
            # Look for video player indicators
            video_indicators = [
                'jwplayer', 'videojs', 'plyr', 'youtube', 'vimeo',
                'brightcove', 'kaltura', 'wistia', 'panopto'
            ]
            
            for indicator in video_indicators:
                if indicator.lower() in page_source.lower():
                    analysis['video_players_detected'].append(indicator)
            
            # Look for streaming format indicators
            streaming_indicators = [
                '.m3u8', '.mpd', '.mp4', '.webm', '.mov',
                'hls', 'dash', 'rtmp', 'stream'
            ]
            
            for indicator in streaming_indicators:
                if indicator in page_source.lower():
                    analysis['streaming_indicators'].append(indicator)
            
            # Look for embedded content
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src:
                    analysis['embedded_content'].append(src)
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def find_hearing_pages(self, base_url):
        """Find hearing/video pages from the committee site."""
        hearing_urls = []
        
        try:
            self.driver.get(base_url)
            time.sleep(3)
            
            # Look for links that might lead to hearings
            hearing_keywords = [
                'hearing', 'markup', 'meeting', 'video', 'live',
                'webcast', 'stream', 'watch', 'archive'
            ]
            
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in links:
                href = link.get_attribute('href')
                text = link.text.lower() if link.text else ''
                
                if href and any(keyword in text or keyword in href.lower() for keyword in hearing_keywords):
                    full_url = urljoin(base_url, href)
                    if full_url not in hearing_urls:
                        hearing_urls.append(full_url)
            
            print(f"   Found {len(hearing_urls)} potential hearing pages")
            for url in hearing_urls[:5]:  # Show first 5
                print(f"     - {url}")
            
            return hearing_urls
            
        except Exception as e:
            print(f"   Error finding hearing pages: {e}")
            return []
    
    def deep_video_analysis(self, url):
        """Perform deep analysis of a specific video page."""
        try:
            print(f"     Loading page: {url}")
            
            # Clear previous logs
            self.driver.get('about:blank')
            time.sleep(1)
            
            # Start fresh network monitoring
            self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            
            # Load the target page
            self.driver.get(url)
            
            # Wait for page to fully load
            time.sleep(10)
            
            analysis = {
                'formats': [],
                'endpoints': [],
                'underlying_formats': [],
                'network_requests': []
            }
            
            # Get performance logs to see network requests
            logs = self.driver.get_log('performance')
            
            video_requests = []
            audio_requests = []
            manifest_requests = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        request_url = response['url']
                        mime_type = response.get('mimeType', '').lower()
                        
                        # Categorize requests
                        if any(ext in request_url.lower() for ext in ['.mp4', '.webm', '.mov', '.avi']):
                            video_requests.append({
                                'url': request_url,
                                'mime_type': mime_type,
                                'type': 'video_file'
                            })
                        
                        elif any(ext in request_url.lower() for ext in ['.mp3', '.aac', '.wav', '.m4a']):
                            audio_requests.append({
                                'url': request_url,
                                'mime_type': mime_type,
                                'type': 'audio_file'
                            })
                        
                        elif any(ext in request_url.lower() for ext in ['.m3u8', '.mpd', '.f4m']):
                            manifest_requests.append({
                                'url': request_url,
                                'mime_type': mime_type,
                                'type': 'manifest'
                            })
                        
                        elif 'video' in mime_type or 'audio' in mime_type:
                            video_requests.append({
                                'url': request_url,
                                'mime_type': mime_type,
                                'type': 'media_stream'
                            })
                
                except:
                    continue
            
            # Analyze found requests
            analysis['network_requests'] = {
                'video_requests': video_requests,
                'audio_requests': audio_requests,
                'manifest_requests': manifest_requests
            }
            
            # Determine underlying formats
            for request in video_requests + audio_requests + manifest_requests:
                url = request['url']
                
                if '.m3u8' in url:
                    analysis['underlying_formats'].append('HLS (HTTP Live Streaming)')
                    analysis['endpoints'].append(url)
                    analysis['formats'].append({
                        'format': 'HLS',
                        'url': url,
                        'description': 'HTTP Live Streaming - Apple standard'
                    })
                
                elif '.mpd' in url:
                    analysis['underlying_formats'].append('DASH (Dynamic Adaptive Streaming)')
                    analysis['endpoints'].append(url)
                    analysis['formats'].append({
                        'format': 'DASH',
                        'url': url,
                        'description': 'MPEG-DASH adaptive streaming'
                    })
                
                elif '.mp4' in url:
                    analysis['underlying_formats'].append('MP4 Progressive Download')
                    analysis['endpoints'].append(url)
                    analysis['formats'].append({
                        'format': 'MP4',
                        'url': url,
                        'description': 'MP4 video file - direct download'
                    })
                
                elif '.mp3' in url or '.aac' in url:
                    analysis['underlying_formats'].append('Direct Audio Stream')
                    analysis['endpoints'].append(url)
                    analysis['formats'].append({
                        'format': 'Audio',
                        'url': url,
                        'description': 'Direct audio stream'
                    })
            
            # Also check DOM for video elements with sources
            try:
                video_elements = self.driver.find_elements(By.TAG_NAME, 'video')
                for video in video_elements:
                    src = video.get_attribute('src')
                    if src:
                        analysis['endpoints'].append(src)
                        analysis['formats'].append({
                            'format': 'HTML5 Video',
                            'url': src,
                            'description': 'Native HTML5 video element'
                        })
            except:
                pass
            
            return analysis if analysis['endpoints'] else None
            
        except Exception as e:
            print(f"     Error in deep analysis: {e}")
            return None
    
    def check_common_video_paths(self, base_url):
        """Check common video-related paths on the committee site."""
        common_paths = [
            '/hearings',
            '/meetings',
            '/video',
            '/live',
            '/webcast',
            '/markup',
            '/archive',
            '/media'
        ]
        
        found_paths = []
        
        for path in common_paths:
            test_url = urljoin(base_url, path)
            try:
                response = self.session.head(test_url, timeout=10)
                if response.status_code == 200:
                    found_paths.append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code
                    })
            except:
                continue
        
        return found_paths
    
    def analyze_video_endpoint(self, endpoint_url):
        """Analyze a specific video endpoint to determine format details."""
        try:
            response = self.session.head(endpoint_url, timeout=10)
            
            analysis = {
                'url': endpoint_url,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': response.headers.get('content-length', 'unknown'),
                'server': response.headers.get('server', 'unknown'),
                'format_details': {}
            }
            
            # Determine format from URL and headers
            if '.m3u8' in endpoint_url:
                analysis['format_details'] = {
                    'format': 'HLS',
                    'streaming_type': 'Adaptive',
                    'protocol': 'HTTP',
                    'apple_standard': True,
                    'conversion_method': 'ffmpeg -i playlist.m3u8 -c copy output.mp4'
                }
            
            elif '.mpd' in endpoint_url:
                analysis['format_details'] = {
                    'format': 'DASH',
                    'streaming_type': 'Adaptive',
                    'protocol': 'HTTP',
                    'mpeg_standard': True,
                    'conversion_method': 'youtube-dl or custom DASH parser'
                }
            
            elif '.mp4' in endpoint_url:
                analysis['format_details'] = {
                    'format': 'MP4',
                    'streaming_type': 'Progressive',
                    'protocol': 'HTTP',
                    'direct_download': True,
                    'conversion_method': 'ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3'
                }
            
            return analysis
            
        except Exception as e:
            return {'url': endpoint_url, 'error': str(e)}
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    """Main function to investigate specific Senate committees."""
    
    # Target committees as requested
    target_committees = [
        {
            'name': 'Senate Commerce, Science, and Transportation',
            'url': 'http://www.commerce.senate.gov/'
        },
        {
            'name': 'Senate Judiciary', 
            'url': 'http://www.judiciary.senate.gov/'
        },
        {
            'name': 'Senate Banking, Housing, and Urban Affairs',
            'url': 'http://www.banking.senate.gov/public'
        }
    ]
    
    investigator = DeepVideoInvestigator()
    
    all_results = []
    
    try:
        for committee in target_committees:
            results = investigator.investigate_committee(committee['name'], committee['url'])
            all_results.append(results)
            
            # Print immediate findings
            print(f"\nIMMEDIATE FINDINGS for {committee['name']}:")
            print(f"Video formats found: {len(results['video_formats_found'])}")
            print(f"Streaming endpoints: {len(results['streaming_endpoints'])}")
            print(f"Underlying formats: {results['underlying_formats']}")
            
            if results['streaming_endpoints']:
                print(f"Sample endpoints:")
                for endpoint in results['streaming_endpoints'][:3]:
                    print(f"  - {endpoint}")
            
            # Add delay between committees
            time.sleep(5)
        
        # Generate comprehensive report
        print(f"\n{'='*80}")
        print("COMPREHENSIVE VIDEO FORMAT ANALYSIS")
        print(f"{'='*80}")
        
        for results in all_results:
            committee_name = results['committee']
            
            print(f"\n{committee_name}:")
            print(f"  URL: {results['url']}")
            
            if results['video_formats_found']:
                print(f"  VIDEO FORMATS DETECTED:")
                for fmt in results['video_formats_found']:
                    print(f"    - {fmt.get('format', 'Unknown')}: {fmt.get('description', 'No description')}")
                    if fmt.get('url'):
                        print(f"      Endpoint: {fmt['url']}")
            
            if results['underlying_formats']:
                print(f"  UNDERLYING FORMATS:")
                for fmt in set(results['underlying_formats']):
                    print(f"    - {fmt}")
            
            if results['streaming_endpoints']:
                print(f"  STREAMING ENDPOINTS ({len(results['streaming_endpoints'])}):")
                for endpoint in results['streaming_endpoints'][:5]:  # Show first 5
                    print(f"    - {endpoint}")
                    
                    # Analyze each endpoint
                    analysis = investigator.analyze_video_endpoint(endpoint)
                    if 'format_details' in analysis:
                        details = analysis['format_details']
                        print(f"      Format: {details.get('format', 'Unknown')}")
                        print(f"      Type: {details.get('streaming_type', 'Unknown')}")
                        print(f"      Conversion: {details.get('conversion_method', 'Unknown')}")
            
            if not results['video_formats_found'] and not results['streaming_endpoints']:
                print(f"  ❌ No video content detected")
            else:
                print(f"  ✅ Video content found!")
        
        # Save detailed results
        output_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'deep_video_investigation.json')
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\nInvestigation interrupted by user")
    except Exception as e:
        print(f"Investigation error: {e}")
    finally:
        investigator.cleanup()


if __name__ == '__main__':
    main()