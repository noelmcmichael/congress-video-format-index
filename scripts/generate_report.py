#!/usr/bin/env python3
"""
Generate comprehensive analysis report of Congress video formats.
"""
import sys
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import CongressVideoDatabase


def generate_report():
    """Generate comprehensive analysis report."""
    print("Generating Congress Video Format Analysis Report...")
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'congress_video.db')
    db = CongressVideoDatabase(db_path)
    
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate report content
    report_content = []
    report_content.append("# Congress Video Format Index - Analysis Report")
    report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append("")
    
    # Database statistics
    stats = db.get_stats()
    report_content.append("## Database Statistics")
    report_content.append("")
    report_content.append(f"- **Total Committees**: {stats['total_committees']}")
    report_content.append(f"- **Total Subcommittees**: {stats['total_subcommittees']}")
    report_content.append(f"- **Total Hearings**: {stats['total_hearings']}")
    report_content.append(f"- **Total Video Formats**: {stats['total_video_formats']}")
    report_content.append("")
    
    # Committee breakdown by chamber
    report_content.append("## Committees by Chamber")
    report_content.append("")
    report_content.append("| Chamber | Count |")
    report_content.append("|---------|-------|")
    for chamber, count in stats['committees_by_chamber'].items():
        report_content.append(f"| {chamber.title()} | {count} |")
    report_content.append("")
    
    # Video format breakdown
    if stats['formats_by_platform']:
        report_content.append("## Video Formats by Platform")
        report_content.append("")
        report_content.append("| Platform | Count |")
        report_content.append("|----------|-------|")
        for platform, count in stats['formats_by_platform'].items():
            report_content.append(f"| {platform.title()} | {count} |")
        report_content.append("")
    
    # Detailed committee listings
    house_committees = db.get_committees('house')
    senate_committees = db.get_committees('senate')
    
    report_content.append("## House of Representatives Committees")
    report_content.append("")
    report_content.append("| Committee | Code | Official URL |")
    report_content.append("|-----------|------|--------------|")
    for committee in house_committees:
        code = committee.committee_code or "N/A"
        url = committee.official_url
        report_content.append(f"| {committee.name} | {code} | [{url}]({url}) |")
    report_content.append("")
    
    report_content.append("## Senate Committees")
    report_content.append("")
    report_content.append("| Committee | Code | Official URL |")
    report_content.append("|-----------|------|--------------|")
    for committee in senate_committees:
        code = committee.committee_code or "N/A"
        url = committee.official_url
        report_content.append(f"| {committee.name} | {code} | [{url}]({url}) |")
    report_content.append("")
    
    # Video format analysis
    video_formats = db.get_video_formats()
    if video_formats:
        report_content.append("## Video Format Analysis")
        report_content.append("")
        
        # Platform analysis
        platform_analysis = defaultdict(list)
        for vf in video_formats:
            platform_analysis[vf.platform].append(vf)
        
        for platform, formats in platform_analysis.items():
            report_content.append(f"### {platform.title()} Platform")
            report_content.append("")
            report_content.append(f"- **Total instances**: {len(formats)}")
            
            # Get unique streaming URLs
            unique_urls = set(vf.streaming_url for vf in formats if vf.streaming_url)
            if unique_urls:
                report_content.append(f"- **Unique streaming URLs**: {len(unique_urls)}")
            
            # Get player types
            player_types = Counter(vf.player_type for vf in formats if vf.player_type)
            if player_types:
                report_content.append("- **Player types**:")
                for player_type, count in player_types.most_common():
                    report_content.append(f"  - {player_type}: {count}")
            
            report_content.append("")
    
    # Technical findings
    report_content.append("## Technical Findings")
    report_content.append("")
    
    # Analyze committee website patterns
    house_domains = set()
    senate_domains = set()
    
    for committee in house_committees:
        if committee.official_url:
            domain = committee.official_url.split('/')[2]
            house_domains.add(domain)
    
    for committee in senate_committees:
        if committee.official_url:
            domain = committee.official_url.split('/')[2]
            senate_domains.add(domain)
    
    report_content.append("### Website Architecture")
    report_content.append("")
    report_content.append("**House of Representatives:**")
    report_content.append("- Uses decentralized committee websites")
    report_content.append("- Each committee has its own subdomain (e.g., agriculture.house.gov)")
    report_content.append(f"- Total unique domains: {len(house_domains)}")
    report_content.append("")
    
    report_content.append("**Senate:**")
    report_content.append("- Uses centralized committee directory")
    report_content.append("- Mixed approach with both senate.gov and external domains")
    report_content.append(f"- Total unique domains: {len(senate_domains)}")
    report_content.append("")
    
    # Scraping challenges
    report_content.append("### Scraping Challenges Identified")
    report_content.append("")
    report_content.append("1. **Inconsistent Website Structures**: Each committee uses different layouts")
    report_content.append("2. **Rate Limiting**: Some sites implement aggressive rate limiting")
    report_content.append("3. **JavaScript Dependencies**: Some video players require JavaScript execution")
    report_content.append("4. **Access Restrictions**: Some committee sites block automated access")
    report_content.append("5. **Video Format Detection**: Complex embed codes and custom players")
    report_content.append("")
    
    # Recommendations
    report_content.append("## Recommendations")
    report_content.append("")
    report_content.append("### For Researchers")
    report_content.append("- Focus on Senate committees for more consistent data access")
    report_content.append("- House committees require individual analysis due to decentralized structure")
    report_content.append("- Video format detection works best on sites with standard embed codes")
    report_content.append("")
    
    report_content.append("### For Congress")
    report_content.append("- Standardize video streaming platforms across committees")
    report_content.append("- Implement consistent accessibility features")
    report_content.append("- Provide structured data feeds for hearing information")
    report_content.append("- Consider centralized video hosting solution")
    report_content.append("")
    
    # Data quality notes
    report_content.append("## Data Quality Notes")
    report_content.append("")
    report_content.append("- **Committee Discovery**: High accuracy for both chambers")
    report_content.append("- **Hearing Detection**: Variable success rate due to site differences")
    report_content.append("- **Video Format Detection**: Limited by JavaScript-heavy implementations")
    report_content.append("- **Real-time Data**: Snapshot from scraping session, not live data")
    report_content.append("")
    
    # Future work
    report_content.append("## Future Work")
    report_content.append("")
    report_content.append("1. **Enhanced Video Detection**: Implement Selenium for JavaScript-heavy sites")
    report_content.append("2. **Real-time Monitoring**: Set up scheduled scraping for live data")
    report_content.append("3. **Accessibility Analysis**: Evaluate compliance with accessibility standards")
    report_content.append("4. **Performance Metrics**: Measure video quality and streaming reliability")
    report_content.append("5. **API Development**: Create public API for accessing the data")
    report_content.append("")
    
    # Appendix
    report_content.append("## Appendix")
    report_content.append("")
    report_content.append("### Data Sources")
    report_content.append("- House: https://www.house.gov/committees")
    report_content.append("- Senate: https://www.senate.gov/committees/")
    report_content.append("")
    
    report_content.append("### Technology Stack")
    report_content.append("- **Language**: Python 3.13+")
    report_content.append("- **Web Scraping**: BeautifulSoup, Requests, Selenium")
    report_content.append("- **Database**: SQLite3")
    report_content.append("- **Analysis**: Pandas, SQLite")
    report_content.append("")
    
    # Write report to file
    report_file = os.path.join(reports_dir, f'congress_video_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_content))
    
    print(f"Report generated: {report_file}")
    
    # Also generate a summary CSV
    csv_file = os.path.join(reports_dir, f'committee_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(csv_file, 'w') as f:
        f.write("Chamber,Committee,Code,Official_URL,Description\n")
        for committee in house_committees + senate_committees:
            f.write(f'"{committee.chamber}","{committee.name}","{committee.committee_code}","{committee.official_url}","{committee.description}"\n')
    
    print(f"CSV summary generated: {csv_file}")
    
    return report_file, csv_file


if __name__ == '__main__':
    report_file, csv_file = generate_report()
    print(f"\nAnalysis complete!")
    print(f"Report: {report_file}")
    print(f"CSV: {csv_file}")