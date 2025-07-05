#!/usr/bin/env python3
"""
Extract complete video format details for MP3 conversion project.
"""
import sys
import os
import json
import re
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import CongressVideoDatabase


def extract_video_formats():
    """Extract complete video format details."""
    print("Extracting Video Formats for MP3 Conversion...")
    
    # Get raw data files
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    
    # Find latest data files
    house_files = [f for f in os.listdir(data_dir) if f.startswith('house_data_')]
    senate_files = [f for f in os.listdir(data_dir) if f.startswith('senate_data_')]
    
    if not house_files or not senate_files:
        print("No data files found!")
        return
    
    latest_house_file = max(house_files)
    latest_senate_file = max(senate_files)
    
    print(f"Analyzing: {latest_house_file} and {latest_senate_file}")
    
    # Load raw data
    with open(os.path.join(data_dir, latest_house_file), 'r') as f:
        house_data = json.load(f)
    
    with open(os.path.join(data_dir, latest_senate_file), 'r') as f:
        senate_data = json.load(f)
    
    all_video_formats = house_data['video_formats'] + senate_data['video_formats']
    all_hearings = house_data['hearings'] + senate_data['hearings']
    all_committees = house_data['committees'] + senate_data['committees']
    
    print(f"\nFound {len(all_video_formats)} video format instances")
    print(f"Found {len(all_hearings)} hearings")
    print(f"Found {len(all_committees)} committees")
    
    # Create lookup tables
    committee_lookup = {c['name']: c for c in all_committees}
    
    # Analyze video formats
    video_format_analysis = []
    
    for i, vf in enumerate(all_video_formats):
        analysis = {
            'index': i + 1,
            'platform': vf.get('platform', 'unknown'),
            'player_type': vf.get('player_type', 'unknown'),
            'video_id': vf.get('video_id', ''),
            'streaming_url': vf.get('streaming_url', ''),
            'embed_code': vf.get('embed_code', ''),
            'hearing_id': vf.get('hearing_id'),
            'technical_details': vf.get('technical_details', ''),
            'accessibility_features': vf.get('accessibility_features', ''),
            'conversion_notes': []
        }
        
        # Add platform-specific analysis
        if analysis['platform'] == 'youtube':
            analysis['conversion_notes'].append('YouTube: Use youtube-dl or yt-dlp for extraction')
            analysis['conversion_notes'].append('Audio format: Usually AAC or Opus')
            analysis['conversion_notes'].append('Quality options: 128kbps, 192kbps, 256kbps available')
            
            # Extract YouTube video ID
            youtube_id = extract_youtube_id(analysis['streaming_url'] or analysis['embed_code'])
            if youtube_id:
                analysis['youtube_id'] = youtube_id
                analysis['direct_url'] = f"https://www.youtube.com/watch?v={youtube_id}"
                analysis['conversion_notes'].append(f'Direct YouTube URL: https://www.youtube.com/watch?v={youtube_id}')
        
        elif analysis['platform'] == 'jwplayer':
            analysis['conversion_notes'].append('JWPlayer: JavaScript-based, requires dynamic extraction')
            analysis['conversion_notes'].append('Audio format: Usually AAC or MP3')
            analysis['conversion_notes'].append('Extraction: May need Selenium or API calls')
            
            # Try to extract JWPlayer config
            jwplayer_config = extract_jwplayer_config(analysis['embed_code'])
            if jwplayer_config:
                analysis['jwplayer_config'] = jwplayer_config
        
        elif analysis['platform'] == 'vimeo':
            analysis['conversion_notes'].append('Vimeo: Use vimeo-dl or similar tools')
            analysis['conversion_notes'].append('Audio format: Usually AAC')
            analysis['conversion_notes'].append('Quality: Multiple bitrates available')
        
        elif analysis['platform'] == 'html5':
            analysis['conversion_notes'].append('HTML5 Video: Direct MP4/WebM files')
            analysis['conversion_notes'].append('Audio extraction: Use ffmpeg directly')
            analysis['conversion_notes'].append('Format: Depends on source (AAC, MP3, Opus)')
        
        elif analysis['platform'] == 'custom':
            analysis['conversion_notes'].append('Custom Player: Requires individual analysis')
            analysis['conversion_notes'].append('Extraction: May need reverse engineering')
            analysis['conversion_notes'].append('Format: Unknown - inspect network traffic')
        
        video_format_analysis.append(analysis)
    
    # Generate comprehensive report
    print("\n" + "="*80)
    print("COMPLETE VIDEO FORMAT ANALYSIS FOR MP3 CONVERSION")
    print("="*80)
    
    # Platform summary
    platform_counts = defaultdict(int)
    for vf in video_format_analysis:
        platform_counts[vf['platform']] += 1
    
    print(f"\nPLATFORM SUMMARY:")
    for platform, count in platform_counts.items():
        print(f"  {platform.upper()}: {count} instances")
    
    # Detailed analysis
    print(f"\nDETAILED VIDEO FORMAT SPECIFICATIONS:")
    print(f"{'='*80}")
    
    for vf in video_format_analysis:
        print(f"\n[{vf['index']}] PLATFORM: {vf['platform'].upper()}")
        print(f"    Player Type: {vf['player_type']}")
        print(f"    Video ID: {vf['video_id'] or 'N/A'}")
        print(f"    Streaming URL: {vf['streaming_url'] or 'N/A'}")
        
        if vf.get('youtube_id'):
            print(f"    YouTube ID: {vf['youtube_id']}")
            print(f"    Direct URL: {vf['direct_url']}")
        
        if vf.get('jwplayer_config'):
            print(f"    JWPlayer Config: {vf['jwplayer_config']}")
        
        if vf['embed_code']:
            print(f"    Embed Code: {vf['embed_code'][:100]}...")
        
        if vf['conversion_notes']:
            print(f"    CONVERSION NOTES:")
            for note in vf['conversion_notes']:
                print(f"      - {note}")
        
        print(f"    " + "-"*60)
    
    # Committee-specific analysis
    print(f"\n" + "="*80)
    print("COMMITTEE-SPECIFIC VIDEO FORMAT ANALYSIS")
    print("="*80)
    
    # Try to associate video formats with committees
    committee_video_map = defaultdict(list)
    
    for hearing in all_hearings:
        hearing_url = hearing.get('hearing_url', '')
        if hearing_url:
            # Try to match hearing URL with committee
            for committee in all_committees:
                committee_url = committee.get('official_url', '')
                if committee_url and hearing_url.startswith(committee_url):
                    committee_video_map[committee['name']].append(hearing)
                    break
    
    print(f"\nCOMMITTEE VIDEO FORMAT USAGE:")
    for committee_name, hearings in committee_video_map.items():
        committee = committee_lookup.get(committee_name)
        if committee:
            print(f"\n{committee_name} ({committee.get('chamber', 'unknown').upper()})")
            print(f"  Official URL: {committee.get('official_url', 'N/A')}")
            print(f"  Hearings found: {len(hearings)}")
            print(f"  Committee Code: {committee.get('committee_code', 'N/A')}")
            
            # Check for video formats in hearings
            for hearing in hearings[:3]:  # Show first 3
                print(f"    - {hearing.get('title', 'No title')[:50]}...")
                print(f"      URL: {hearing.get('hearing_url', 'N/A')}")
    
    # MP3 conversion recommendations
    print(f"\n" + "="*80)
    print("MP3 CONVERSION TOOL RECOMMENDATIONS")
    print("="*80)
    
    print(f"""
EXTRACTION TOOLS BY PLATFORM:

1. YOUTUBE (most common):
   - Tool: yt-dlp (recommended) or youtube-dl
   - Command: yt-dlp -x --audio-format mp3 --audio-quality 192K [URL]
   - Audio formats: AAC, Opus (convert to MP3)
   - Quality: 128kbps, 192kbps, 256kbps available

2. JWPLAYER (JavaScript-based):
   - Tool: Custom scraper + ffmpeg
   - Method: Extract JSON config from JavaScript
   - Requirements: Selenium WebDriver for dynamic content
   - Audio formats: AAC, MP3 (varies by implementation)

3. VIMEO:
   - Tool: vimeo-dl or yt-dlp
   - Command: yt-dlp -x --audio-format mp3 [URL]
   - Audio format: Usually AAC

4. HTML5 VIDEO:
   - Tool: ffmpeg (direct extraction)
   - Command: ffmpeg -i [URL] -vn -acodec mp3 -ab 192k output.mp3
   - Audio formats: AAC, MP3, Opus

5. CUSTOM PLAYERS:
   - Tool: Manual analysis + network inspection
   - Method: Reverse engineer streaming URLs
   - Requirements: Browser developer tools + custom scripts

TECHNICAL ARCHITECTURE FOR YOUR MP3 CONVERTER:

1. URL DETECTION:
   - Parse committee URLs from our database
   - Identify video platform from embed codes
   - Extract video IDs and streaming URLs

2. PLATFORM HANDLERS:
   - YouTube: yt-dlp integration
   - JWPlayer: Selenium + JavaScript execution
   - Vimeo: vimeo-dl integration
   - HTML5: Direct ffmpeg conversion
   - Custom: Manual inspection tools

3. AUDIO EXTRACTION:
   - Target format: MP3 192kbps (good quality/size balance)
   - Fallback: Accept AAC and convert
   - Metadata: Include committee, hearing title, date

4. BATCH PROCESSING:
   - Process all committees systematically
   - Handle rate limiting (respect robots.txt)
   - Error handling for failed extractions
   - Progress tracking and logging

5. OUTPUT ORGANIZATION:
   - Folder structure: /[Chamber]/[Committee]/[Hearing_Date]/
   - Filename format: [Committee]_[Date]_[Title].mp3
   - Metadata file: JSON with hearing details
""")
    
    # Save detailed analysis to file
    output_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'video_formats_for_mp3_conversion.json')
    with open(output_file, 'w') as f:
        json.dump({
            'analysis_date': '2025-01-05',
            'total_formats': len(video_format_analysis),
            'platform_counts': dict(platform_counts),
            'detailed_formats': video_format_analysis,
            'committee_video_map': dict(committee_video_map),
            'conversion_recommendations': {
                'youtube': 'yt-dlp -x --audio-format mp3 --audio-quality 192K',
                'jwplayer': 'Selenium + JavaScript extraction + ffmpeg',
                'vimeo': 'yt-dlp -x --audio-format mp3',
                'html5': 'ffmpeg -i [URL] -vn -acodec mp3 -ab 192k',
                'custom': 'Manual analysis required'
            }
        }, indent=2)
    
    print(f"\nDetailed analysis saved to: {output_file}")
    
    return video_format_analysis


def extract_youtube_id(text):
    """Extract YouTube video ID from URL or embed code."""
    if not text:
        return None
    
    patterns = [
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def extract_jwplayer_config(embed_code):
    """Extract JWPlayer configuration from embed code."""
    if not embed_code:
        return None
    
    # Look for JWPlayer setup calls
    patterns = [
        r'jwplayer\([^)]*\)\.setup\(([^}]+})\)',
        r'playerInstance\.setup\(([^}]+})\)',
        r'setup\(([^}]+})\)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, embed_code)
        if match:
            return match.group(1)[:200]  # Return first 200 chars
    
    return None


if __name__ == '__main__':
    extract_video_formats()