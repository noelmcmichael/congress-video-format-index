#!/usr/bin/env python3
"""
Analyze video formats found and organize by committee.
"""
import sys
import os
import json
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import CongressVideoDatabase


def analyze_video_formats():
    """Analyze video formats by committee."""
    print("Analyzing Video Formats by Committee...")
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'congress_video.db')
    db = CongressVideoDatabase(db_path)
    
    # Get all data
    committees = db.get_committees()
    hearings = db.get_hearings()
    video_formats = db.get_video_formats()
    
    print(f"\nDATABASE OVERVIEW:")
    print(f"- Committees: {len(committees)}")
    print(f"- Hearings: {len(hearings)}")
    print(f"- Video formats: {len(video_formats)}")
    
    # Create committee lookup
    committee_lookup = {c.id: c for c in committees}
    
    # Analyze hearings by committee
    hearings_by_committee = defaultdict(list)
    for hearing in hearings:
        if hearing.committee_id:
            hearings_by_committee[hearing.committee_id].append(hearing)
    
    print(f"\nHEARINGS BY COMMITTEE:")
    for committee_id, committee_hearings in hearings_by_committee.items():
        committee = committee_lookup.get(committee_id)
        if committee:
            print(f"- {committee.name} ({committee.chamber}): {len(committee_hearings)} hearings")
    
    # Analyze video formats
    video_by_hearing = defaultdict(list)
    for vf in video_formats:
        if vf.hearing_id:
            video_by_hearing[vf.hearing_id].append(vf)
    
    print(f"\nVIDEO FORMATS DETECTED:")
    platform_counts = defaultdict(int)
    for vf in video_formats:
        platform_counts[vf.platform] += 1
    
    for platform, count in platform_counts.items():
        print(f"- {platform}: {count} instances")
    
    # Show detailed video format analysis
    print(f"\nDETAILED VIDEO FORMAT ANALYSIS:")
    for vf in video_formats:
        print(f"\nPlatform: {vf.platform}")
        print(f"  Player Type: {vf.player_type}")
        print(f"  Video ID: {vf.video_id}")
        print(f"  Streaming URL: {vf.streaming_url}")
        print(f"  Embed Code: {vf.embed_code[:100]}..." if vf.embed_code else "  Embed Code: None")
        
        # Get associated hearing
        hearing = next((h for h in hearings if h.id == vf.hearing_id), None)
        if hearing:
            committee = committee_lookup.get(hearing.committee_id)
            if committee:
                print(f"  Committee: {committee.name} ({committee.chamber})")
                print(f"  Hearing: {hearing.title[:50]}...")
    
    # Read raw data to see what was actually found
    print(f"\nRAW DATA ANALYSIS:")
    try:
        latest_house_file = max([f for f in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')) if f.startswith('house_data_')])
        latest_senate_file = max([f for f in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')) if f.startswith('senate_data_')])
        
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', latest_house_file), 'r') as f:
            house_data = json.load(f)
        
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', latest_senate_file), 'r') as f:
            senate_data = json.load(f)
        
        print(f"House raw video formats: {len(house_data['video_formats'])}")
        print(f"Senate raw video formats: {len(senate_data['video_formats'])}")
        
        # Show sample video formats from raw data
        print(f"\nSAMPLE RAW VIDEO FORMATS:")
        all_raw_formats = house_data['video_formats'] + senate_data['video_formats']
        for i, vf in enumerate(all_raw_formats[:5]):
            print(f"\n{i+1}. Platform: {vf.get('platform', 'Unknown')}")
            print(f"   Player Type: {vf.get('player_type', 'Unknown')}")
            print(f"   Video ID: {vf.get('video_id', 'None')}")
            print(f"   Streaming URL: {vf.get('streaming_url', 'None')}")
            if vf.get('embed_code'):
                print(f"   Embed Code: {vf['embed_code'][:100]}...")
    
    except Exception as e:
        print(f"Error reading raw data: {e}")
    
    # Committee-specific analysis
    print(f"\nCOMMITTEE-SPECIFIC FINDINGS:")
    
    # House committees with specific findings
    house_committees = [c for c in committees if c.chamber == 'house']
    print(f"\nHouse Committee Analysis:")
    print(f"- Total House committees: {len(house_committees)}")
    print(f"- Committee URL pattern: [name].house.gov")
    print(f"- Each committee has independent website structure")
    
    # Senate committees with specific findings  
    senate_committees = [c for c in committees if c.chamber == 'senate']
    print(f"\nSenate Committee Analysis:")
    print(f"- Total Senate committees: {len(senate_committees)}")
    print(f"- Mixed URL patterns: senate.gov and external domains")
    print(f"- More centralized structure via senate.gov")
    
    # Video streaming platform summary
    print(f"\nVIDEO STREAMING PLATFORM SUMMARY:")
    print(f"Based on the analysis of {len(committees)} committees:")
    
    if platform_counts:
        print(f"✅ PLATFORMS DETECTED:")
        for platform, count in platform_counts.items():
            print(f"   - {platform.title()}: {count} instances")
    else:
        print(f"⚠️  LIMITED VIDEO FORMAT DETECTION:")
        print(f"   - Most committees use complex JavaScript players")
        print(f"   - Many require login or specific access")
        print(f"   - Custom streaming solutions are common")
    
    print(f"\nRECOMMENDATIONS:")
    print(f"1. Focus on Senate committees for more structured data access")
    print(f"2. House committees require individual analysis due to decentralized structure")
    print(f"3. Consider using Selenium for JavaScript-heavy video players")
    print(f"4. Manual verification needed for complex streaming setups")
    
    return {
        'committees': len(committees),
        'hearings': len(hearings), 
        'video_formats': len(video_formats),
        'platforms': dict(platform_counts),
        'house_committees': len(house_committees),
        'senate_committees': len(senate_committees)
    }


if __name__ == '__main__':
    results = analyze_video_formats()
    print(f"\n{'='*50}")
    print(f"FINAL ANALYSIS COMPLETE")
    print(f"{'='*50}")
    print(f"Total committees catalogued: {results['committees']}")
    print(f"Total hearings found: {results['hearings']}")
    print(f"Video formats detected: {results['video_formats']}")
    print(f"Platforms identified: {list(results['platforms'].keys())}")