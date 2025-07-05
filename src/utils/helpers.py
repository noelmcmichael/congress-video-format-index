"""
Utility functions for web scraping and data processing.
"""
import re
import time
import random
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


class WebScraper:
    """Base web scraper with rate limiting and error handling."""
    
    def __init__(self, delay_range: tuple = (1, 3), max_retries: int = 3):
        """Initialize scraper with rate limiting and retry configuration."""
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get a web page with rate limiting and error handling."""
        try:
            # Rate limiting
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_soup(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """Get a BeautifulSoup object for a web page."""
        response = self.get_page(url, **kwargs)
        if response:
            return BeautifulSoup(response.content, 'html.parser')
        return None


class VideoFormatDetector:
    """Detect video formats and streaming platforms from web pages."""
    
    @staticmethod
    def extract_youtube_info(embed_code: str) -> Optional[Dict[str, Any]]:
        """Extract YouTube video information from embed code."""
        youtube_patterns = [
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, embed_code)
            if match:
                video_id = match.group(1)
                return {
                    'platform': 'youtube',
                    'video_id': video_id,
                    'embed_url': f'https://www.youtube.com/embed/{video_id}',
                    'watch_url': f'https://www.youtube.com/watch?v={video_id}'
                }
        
        return None
    
    @staticmethod
    def extract_vimeo_info(embed_code: str) -> Optional[Dict[str, Any]]:
        """Extract Vimeo video information from embed code."""
        vimeo_patterns = [
            r'vimeo\.com/video/(\d+)',
            r'player\.vimeo\.com/video/(\d+)',
            r'vimeo\.com/(\d+)'
        ]
        
        for pattern in vimeo_patterns:
            match = re.search(pattern, embed_code)
            if match:
                video_id = match.group(1)
                return {
                    'platform': 'vimeo',
                    'video_id': video_id,
                    'embed_url': f'https://player.vimeo.com/video/{video_id}',
                    'watch_url': f'https://vimeo.com/{video_id}'
                }
        
        return None
    
    @staticmethod
    def detect_streaming_platform(soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Detect streaming platforms and video information from a web page."""
        detected_formats = []
        
        # Look for iframe embeds
        iframes = soup.find_all('iframe', src=True)
        for iframe in iframes:
            src = iframe.get('src', '')
            
            # YouTube detection
            youtube_info = VideoFormatDetector.extract_youtube_info(src)
            if youtube_info:
                youtube_info.update({
                    'embed_code': str(iframe),
                    'streaming_url': src,
                    'player_type': 'embedded'
                })
                detected_formats.append(youtube_info)
                continue
            
            # Vimeo detection
            vimeo_info = VideoFormatDetector.extract_vimeo_info(src)
            if vimeo_info:
                vimeo_info.update({
                    'embed_code': str(iframe),
                    'streaming_url': src,
                    'player_type': 'embedded'
                })
                detected_formats.append(vimeo_info)
                continue
            
            # Generic video embed
            if any(domain in src for domain in ['video', 'stream', 'media']):
                detected_formats.append({
                    'platform': 'custom',
                    'embed_code': str(iframe),
                    'streaming_url': src,
                    'player_type': 'embedded'
                })
        
        # Look for video tags
        videos = soup.find_all('video', src=True)
        for video in videos:
            src = video.get('src', '')
            detected_formats.append({
                'platform': 'html5',
                'embed_code': str(video),
                'streaming_url': src,
                'player_type': 'native'
            })
        
        # Look for JavaScript video players
        scripts = soup.find_all('script', string=True)
        for script in scripts:
            script_content = script.string
            if not script_content:
                continue
            
            # JW Player detection
            if 'jwplayer' in script_content.lower():
                detected_formats.append({
                    'platform': 'jwplayer',
                    'embed_code': str(script),
                    'player_type': 'javascript'
                })
            
            # Video.js detection
            elif 'videojs' in script_content.lower():
                detected_formats.append({
                    'platform': 'videojs',
                    'embed_code': str(script),
                    'player_type': 'javascript'
                })
        
        return detected_formats


class URLNormalizer:
    """Normalize and validate URLs."""
    
    @staticmethod
    def normalize_url(url: str, base_url: str = None) -> str:
        """Normalize a URL and make it absolute."""
        if not url:
            return ""
        
        # Handle relative URLs
        if base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        
        # Remove fragments
        parsed = urlparse(url)
        normalized = parsed._replace(fragment='').geturl()
        
        return normalized
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if a URL is valid."""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""


class TextCleaner:
    """Clean and normalize text content."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_committee_code(text: str) -> Optional[str]:
        """Extract committee code from text."""
        # Common patterns for committee codes
        patterns = [
            r'\b([A-Z]{2,6})\b',  # 2-6 uppercase letters
            r'\b([A-Z][A-Z0-9]{1,5})\b',  # Letter followed by letters/numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_date_patterns(text: str) -> List[str]:
        """Extract date patterns from text."""
        date_patterns = [
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{1,2}-\d{1,2}-\d{4})\b',  # MM-DD-YYYY
            r'\b(\w+\s+\d{1,2},\s+\d{4})\b',  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates