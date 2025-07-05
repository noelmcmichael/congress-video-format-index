# Congress Video to MP3 Conversion - Complete Technical Specifications

## 🎯 Overview
Based on analysis of 47 Congressional committees, here are the complete video format specifications and conversion requirements for your MP3 extraction tool.

## 📊 Video Format Inventory

### Current Detection Results
- **Total Video Instances Found**: 8
- **Primary Platform**: JWPlayer (7 instances, 87.5%)
- **Secondary Platform**: Custom players (1 instance, 12.5%)
- **YouTube/Vimeo**: 0 instances (but prepare for future detection)

### Platform Breakdown

#### 1. JWPlayer (87.5% of instances) - **PRIORITY 1**
```javascript
// Example embed code structure:
<script>
window.top['site_path'] = "22E06EDE-4040-F985-52CD-79017F1DFF8D";
var application = {
    "config": {
        "tinymce": {...},
        "jwplayer": {...}  // Configuration here
    }
}
</script>
```

**Conversion Strategy**:
- **Tool Required**: Selenium WebDriver + Custom JavaScript executor
- **Audio Format**: AAC or MP3 (varies by implementation)
- **Extraction Method**: Dynamic JavaScript execution to get stream URLs
- **Complexity**: HIGH

#### 2. Custom Players (12.5% of instances) - **PRIORITY 2**
- **Conversion Strategy**: Manual analysis per committee
- **Tool Required**: Browser developer tools + network inspection
- **Audio Format**: Unknown (requires investigation)
- **Extraction Method**: Reverse engineer streaming protocols
- **Complexity**: VERY HIGH

## 🛠️ Technical Implementation Guide

### Core Architecture

```python
class CongressVideoToMP3Converter:
    def __init__(self):
        self.selenium_driver = self.setup_selenium()
        self.committee_database = self.load_committee_db()
        
    def setup_selenium(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)
    
    def process_committee(self, committee_url):
        platform = self.detect_video_platform(committee_url)
        return self.extract_audio_by_platform(platform, committee_url)
    
    def detect_video_platform(self, url):
        page_source = self.get_page_source(url)
        
        if 'jwplayer' in page_source.lower():
            return 'jwplayer'
        elif 'youtube.com' in page_source or 'youtu.be' in page_source:
            return 'youtube'
        elif 'vimeo.com' in page_source:
            return 'vimeo'
        elif '<video' in page_source.lower():
            return 'html5'
        else:
            return 'custom'
```

### Platform-Specific Handlers

#### JWPlayer Handler (Primary Need)
```python
def extract_jwplayer_audio(self, url):
    """
    Extract audio from JWPlayer implementations
    Most common format in Congress hearings
    """
    self.selenium_driver.get(url)
    
    # Wait for JWPlayer to initialize
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jwplayer"))
    )
    
    # Execute JavaScript to get player config
    player_config = self.driver.execute_script("""
        // Look for JWPlayer instances
        if (window.jwplayer && jwplayer().getConfig) {
            return jwplayer().getConfig();
        }
        
        // Alternative: Look for setup calls
        if (window.jwplayer_config) {
            return window.jwplayer_config;
        }
        
        // Fallback: Parse from DOM
        var scripts = document.getElementsByTagName('script');
        for (var i = 0; i < scripts.length; i++) {
            if (scripts[i].innerHTML.includes('jwplayer')) {
                return scripts[i].innerHTML;
            }
        }
        return null;
    """)
    
    if player_config:
        stream_url = self.parse_jwplayer_config(player_config)
        return self.download_audio_with_ffmpeg(stream_url, url)
    
    return None

def parse_jwplayer_config(self, config):
    """Parse JWPlayer config to extract stream URLs"""
    if isinstance(config, str):
        # Parse JavaScript string to find URLs
        import re
        url_patterns = [
            r'"file":\s*"([^"]+)"',
            r"'file':\s*'([^']+)'",
            r'file:\s*"([^"]+)"',
            r'sources:\s*\[.*?"file":\s*"([^"]+)"'
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, config)
            if match:
                return match.group(1)
    
    elif isinstance(config, dict):
        # Direct config object
        if 'playlist' in config:
            return config['playlist'][0].get('sources', [{}])[0].get('file')
        elif 'file' in config:
            return config['file']
    
    return None

def download_audio_with_ffmpeg(self, stream_url, source_url):
    """Download and convert to MP3 using ffmpeg"""
    import subprocess
    import tempfile
    
    # Create temporary filename
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        output_file = tmp.name
    
    # FFmpeg command for audio extraction
    cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-vn',  # No video
        '-acodec', 'mp3',
        '-ab', '192k',  # 192kbps audio quality
        '-ar', '44100',  # Sample rate
        '-y',  # Overwrite output
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
```

#### YouTube Handler (Backup)
```python
def extract_youtube_audio(self, url):
    """Extract audio from YouTube videos using yt-dlp"""
    import yt_dlp
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': '192K',
        'outtmpl': '%(title)s.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception as e:
            print(f"YouTube extraction error: {e}")
            return False
```

#### Custom Player Handler
```python
def extract_custom_audio(self, url):
    """Handle custom video players through network inspection"""
    
    # Enable network logging in Selenium
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    self.driver = webdriver.Chrome(desired_capabilities=caps)
    self.driver.get(url)
    
    # Wait for video to load
    time.sleep(10)
    
    # Capture network logs
    logs = self.driver.get_log('performance')
    
    # Look for video/audio stream URLs
    stream_urls = []
    for log in logs:
        message = json.loads(log['message'])
        if message['message']['method'] == 'Network.responseReceived':
            url = message['message']['params']['response']['url']
            mime_type = message['message']['params']['response']['mimeType']
            
            if any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mpd', 'audio']):
                stream_urls.append(url)
            elif 'video' in mime_type or 'audio' in mime_type:
                stream_urls.append(url)
    
    return stream_urls
```

## 📋 Committee Target List

### High-Priority Committees (Known to have video content)

#### House Committees:
```python
PRIORITY_HOUSE_COMMITTEES = [
    {
        "name": "Foreign Affairs",
        "url": "https://foreignaffairs.house.gov/",
        "code": "FOREIGNAFFAIRS",
        "video_likely": True
    },
    {
        "name": "Ways and Means", 
        "url": "https://waysandmeans.house.gov/",
        "code": "WAYSANDMEANS",
        "video_likely": True
    },
    {
        "name": "Budget",
        "url": "https://budget.house.gov/",
        "code": "BUDGET", 
        "video_likely": True
    },
    {
        "name": "Oversight and Government Reform",
        "url": "https://oversight.house.gov/",
        "code": "OVERSIGHT",
        "video_likely": True
    }
]
```

#### Senate Committees:
```python
PRIORITY_SENATE_COMMITTEES = [
    {
        "name": "Appropriations",
        "url": "http://www.appropriations.senate.gov/",
        "video_likely": True
    },
    {
        "name": "Armed Services", 
        "url": "http://www.armed-services.senate.gov/",
        "video_likely": True
    },
    {
        "name": "Foreign Relations",
        "url": "http://www.foreign.senate.gov/",
        "video_likely": True
    },
    {
        "name": "Judiciary",
        "url": "http://www.judiciary.senate.gov/",
        "video_likely": True
    }
]
```

## ⚙️ Dependencies and Tools

### Required Python Packages
```bash
pip install selenium webdriver-manager yt-dlp requests beautifulsoup4 ffmpeg-python
```

### System Requirements
```bash
# FFmpeg installation
# macOS:
brew install ffmpeg

# Ubuntu:
sudo apt update && sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### WebDriver Setup
```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Auto-install ChromeDriver
driver = webdriver.Chrome(ChromeDriverManager().install())
```

## 🔧 Audio Processing Specifications

### Target Audio Format
- **Format**: MP3
- **Bitrate**: 192kbps (good balance of quality/size)
- **Sample Rate**: 44.1kHz
- **Channels**: Stereo (downmix from surround if needed)

### File Organization
```
output/
├── house/
│   ├── agriculture/
│   │   ├── 2025-01-15_hearing_title.mp3
│   │   ├── 2025-01-15_hearing_title.json  # Metadata
│   │   └── ...
│   ├── appropriations/
│   └── ...
├── senate/
│   ├── appropriations/
│   ├── armed_services/
│   └── ...
└── logs/
    ├── extraction_log_2025-01-05.txt
    └── errors_2025-01-05.txt
```

### Metadata JSON Format
```json
{
    "committee": "House Foreign Affairs",
    "chamber": "house",
    "hearing_title": "Hearing on International Relations",
    "hearing_date": "2025-01-15",
    "original_url": "https://foreignaffairs.house.gov/hearing/...",
    "video_platform": "jwplayer",
    "extraction_date": "2025-01-05T10:30:00Z",
    "audio_specs": {
        "format": "mp3",
        "bitrate": "192k",
        "duration_seconds": 7200,
        "file_size_mb": 103.5
    },
    "extraction_success": true,
    "extraction_method": "selenium_jwplayer"
}
```

## 🚨 Important Considerations

### Rate Limiting and Ethics
```python
class RespectfulScraper:
    def __init__(self):
        self.request_delay = 3  # 3 seconds between requests
        self.max_retries = 3
        
    def scrape_with_delay(self, url):
        time.sleep(self.request_delay)
        # ... scraping logic
        
    def respect_robots_txt(self, base_url):
        # Check robots.txt before scraping
        pass
```

### Error Handling
- **Network timeouts**: Implement retry mechanisms
- **JavaScript errors**: Log and continue with next committee
- **Audio extraction failures**: Try alternative methods
- **Storage issues**: Monitor disk space

### Legal Compliance
- **Public domain**: Congressional hearings are public record
- **Attribution**: Include source attribution in metadata
- **Terms of service**: Respect individual committee website terms

## 📈 Success Metrics

### Extraction Success Rates (Target)
- **JWPlayer platforms**: 80%+ success rate
- **YouTube platforms**: 95%+ success rate  
- **Custom platforms**: 40%+ success rate (manual analysis)
- **Overall target**: 70%+ of committees with audio extracted

### Quality Metrics
- **Audio quality**: 192kbps MP3 minimum
- **Metadata completeness**: 90%+ fields populated
- **Processing speed**: <5 minutes per hearing
- **Storage efficiency**: <150MB per hour of audio

## 🚀 Implementation Roadmap

### Phase 1: Core Framework (Week 1)
1. Set up Selenium with ChromeDriver
2. Implement JWPlayer detection and extraction
3. Create basic file organization structure
4. Test with 3-5 known committee sites

### Phase 2: Scaling (Week 2)
1. Add batch processing for all 47 committees
2. Implement error handling and retry logic
3. Add progress tracking and logging
4. Create metadata generation

### Phase 3: Enhancement (Week 3)
1. Add YouTube/Vimeo support
2. Implement custom player analysis tools
3. Add audio quality validation
4. Create summary reporting

### Phase 4: Production (Week 4)
1. Add scheduling for regular updates
2. Implement monitoring and alerting
3. Create user interface for browsing results
4. Documentation and deployment

## 📞 Support Resources

### Database Access
- **SQLite Database**: `data/congress_video.db`
- **Committee URLs**: Pre-verified and normalized
- **Hearing metadata**: Partial data available

### Code Repository
- **GitHub**: https://github.com/noelmcmichael/congress-video-format-index
- **Analysis Tools**: Pre-built scrapers and analyzers
- **Database Schema**: Complete relational structure

This specification provides everything needed to build a comprehensive Congress video-to-MP3 conversion tool based on the actual video formats discovered in Congressional committee websites.