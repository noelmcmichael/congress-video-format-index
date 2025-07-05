#!/usr/bin/env python3
"""
Script to collect all committees, subcommittees, and hearings data from Congress.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import CongressVideoDatabase
from src.scrapers.house_scraper import HouseScraper
from src.scrapers.senate_scraper import SenateScraper


def main():
    """Main function to collect all Congress data."""
    print("Starting Congress Video Format Index data collection...")
    print(f"Timestamp: {datetime.now()}")
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'congress_video.db')
    db = CongressVideoDatabase(db_path)
    
    # Initialize scrapers
    house_scraper = HouseScraper()
    senate_scraper = SenateScraper()
    
    # Collect House data
    print("\n=== Collecting House of Representatives Data ===")
    try:
        house_data = house_scraper.scrape_all_committees_data()
        
        # Save House committees to database
        print(f"Found {len(house_data['committees'])} House committees")
        for committee in house_data['committees']:
            committee_id = db.insert_committee(committee)
            committee.id = committee_id
            
            # Save subcommittees
            committee_subcommittees = [sub for sub in house_data['subcommittees'] 
                                     if sub.parent_committee_id == committee.id]
            for subcommittee in committee_subcommittees:
                subcommittee.parent_committee_id = committee_id
                subcommittee_id = db.insert_subcommittee(subcommittee)
                subcommittee.id = subcommittee_id
        
        # Save House hearings
        print(f"Found {len(house_data['hearings'])} House hearings")
        for hearing in house_data['hearings']:
            # Ensure committee_id is set by finding the committee
            if not hearing.committee_id:
                # Find the committee by name or URL
                for committee in house_data['committees']:
                    if committee.id and hearing.hearing_url.startswith(committee.official_url):
                        hearing.committee_id = committee.id
                        break
            
            if hearing.committee_id:  # Only insert if we have a valid committee_id
                hearing_id = db.insert_hearing(hearing)
                hearing.id = hearing_id
        
        # Save House video formats
        print(f"Found {len(house_data['video_formats'])} House video formats")
        for video_format in house_data['video_formats']:
            if video_format.hearing_id:  # Only insert if we have a valid hearing_id
                db.insert_video_format(video_format)
        
        # Save House scrape logs
        for log in house_data['scrape_logs']:
            db.insert_scrape_log(log)
        
        print("House data collection completed successfully")
        
    except Exception as e:
        print(f"Error collecting House data: {e}")
    
    # Collect Senate data
    print("\n=== Collecting Senate Data ===")
    try:
        senate_data = senate_scraper.scrape_all_committees_data()
        
        # Save Senate committees to database
        print(f"Found {len(senate_data['committees'])} Senate committees")
        for committee in senate_data['committees']:
            committee_id = db.insert_committee(committee)
            committee.id = committee_id
            
            # Save subcommittees
            committee_subcommittees = [sub for sub in senate_data['subcommittees'] 
                                     if sub.parent_committee_id == committee.id]
            for subcommittee in committee_subcommittees:
                subcommittee.parent_committee_id = committee_id
                subcommittee_id = db.insert_subcommittee(subcommittee)
                subcommittee.id = subcommittee_id
        
        # Save Senate hearings
        print(f"Found {len(senate_data['hearings'])} Senate hearings")
        for hearing in senate_data['hearings']:
            # Ensure committee_id is set by finding the committee
            if not hearing.committee_id:
                # Find the committee by name or URL
                for committee in senate_data['committees']:
                    if committee.id and hearing.hearing_url.startswith(committee.official_url):
                        hearing.committee_id = committee.id
                        break
            
            if hearing.committee_id:  # Only insert if we have a valid committee_id
                hearing_id = db.insert_hearing(hearing)
                hearing.id = hearing_id
        
        # Save Senate video formats
        print(f"Found {len(senate_data['video_formats'])} Senate video formats")
        for video_format in senate_data['video_formats']:
            if video_format.hearing_id:  # Only insert if we have a valid hearing_id
                db.insert_video_format(video_format)
        
        # Save Senate scrape logs
        for log in senate_data['scrape_logs']:
            db.insert_scrape_log(log)
        
        print("Senate data collection completed successfully")
        
    except Exception as e:
        print(f"Error collecting Senate data: {e}")
    
    # Generate summary report
    print("\n=== Collection Summary ===")
    stats = db.get_stats()
    print(f"Total committees: {stats['total_committees']}")
    print(f"Total subcommittees: {stats['total_subcommittees']}")
    print(f"Total hearings: {stats['total_hearings']}")
    print(f"Total video formats: {stats['total_video_formats']}")
    
    print("\nCommittees by chamber:")
    for chamber, count in stats['committees_by_chamber'].items():
        print(f"  {chamber}: {count}")
    
    print("\nVideo formats by platform:")
    for platform, count in stats['formats_by_platform'].items():
        print(f"  {platform}: {count}")
    
    # Save raw data to JSON files
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save House data
    house_file = os.path.join(data_dir, f'house_data_{timestamp}.json')
    with open(house_file, 'w') as f:
        # Convert dataclasses to dictionaries for JSON serialization
        json_data = {
            'committees': [c.to_dict() for c in house_data['committees']],
            'subcommittees': [s.to_dict() for s in house_data['subcommittees']],
            'hearings': [h.to_dict() for h in house_data['hearings']],
            'video_formats': [v.to_dict() for v in house_data['video_formats']],
            'scrape_logs': [l.to_dict() for l in house_data['scrape_logs']]
        }
        json.dump(json_data, f, indent=2)
    print(f"House data saved to: {house_file}")
    
    # Save Senate data
    senate_file = os.path.join(data_dir, f'senate_data_{timestamp}.json')
    with open(senate_file, 'w') as f:
        # Convert dataclasses to dictionaries for JSON serialization
        json_data = {
            'committees': [c.to_dict() for c in senate_data['committees']],
            'subcommittees': [s.to_dict() for s in senate_data['subcommittees']],
            'hearings': [h.to_dict() for h in senate_data['hearings']],
            'video_formats': [v.to_dict() for v in senate_data['video_formats']],
            'scrape_logs': [l.to_dict() for l in senate_data['scrape_logs']]
        }
        json.dump(json_data, f, indent=2)
    print(f"Senate data saved to: {senate_file}")
    
    print(f"\nData collection completed: {datetime.now()}")
    print(f"Database saved to: {db_path}")


if __name__ == '__main__':
    main()