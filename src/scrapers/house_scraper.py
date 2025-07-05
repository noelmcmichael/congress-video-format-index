"""
Web scraper for US House of Representatives committees and hearings.
"""
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

from src.database.models import Committee, Subcommittee, Hearing, VideoFormat, ScrapeLog
from src.utils.helpers import WebScraper, VideoFormatDetector, URLNormalizer, TextCleaner


class HouseScraper(WebScraper):
    """Scraper for House of Representatives committees and hearings."""
    
    BASE_URL = "https://www.house.gov"
    COMMITTEES_URL = "https://www.house.gov/committees"
    
    def __init__(self, **kwargs):
        """Initialize House scraper."""
        super().__init__(**kwargs)
        self.chamber = "house"
    
    def scrape_committees(self) -> List[Committee]:
        """Scrape all House committees."""
        committees = []
        
        soup = self.get_soup(self.COMMITTEES_URL)
        if not soup:
            return committees
        
        # Find committee links - House website structure
        # House committees are listed as external links (house.gov domain)
        committee_links = soup.find_all('a', href=True)
        
        for link in committee_links:
            href = link.get('href', '')
            text = TextCleaner.clean_text(link.get_text())
            
            # Filter for committee links - House committees are external links to .house.gov domains
            if ('.house.gov' in href and 
                text and 
                len(text) > 3 and
                not any(skip in text.lower() for skip in ['home', 'skip', 'search', 'view', 'house.gov'])):
                
                committee_url = URLNormalizer.normalize_url(href, self.BASE_URL)
                
                # Extract committee name - clean common patterns
                committee_name = text
                if '(link is external)' in committee_name:
                    committee_name = committee_name.replace('(link is external)', '').strip()
                
                # Generate committee code from URL
                committee_code = ""
                if 'house.gov' in href:
                    # Extract subdomain as committee code
                    import re
                    match = re.search(r'https?://([^.]+)\.house\.gov', href)
                    if match:
                        committee_code = match.group(1).upper()
                
                if committee_name:  # Remove the condition that was preventing committees from being added
                    committee = Committee(
                        name=committee_name,
                        chamber=self.chamber,
                        official_url=committee_url,
                        committee_code=committee_code,
                        description=f"House Committee on {committee_name}"
                    )
                    committees.append(committee)
        
        # Remove duplicates based on URL
        unique_committees = {}
        for committee in committees:
            if committee.official_url not in unique_committees:
                unique_committees[committee.official_url] = committee
        
        return list(unique_committees.values())
    
    def scrape_committee_details(self, committee: Committee) -> List[Subcommittee]:
        """Scrape subcommittees for a specific committee."""
        subcommittees = []
        
        soup = self.get_soup(committee.official_url)
        if not soup:
            return subcommittees
        
        # Look for subcommittee links
        subcommittee_links = soup.find_all('a', href=True)
        
        for link in subcommittee_links:
            href = link.get('href', '')
            text = TextCleaner.clean_text(link.get_text())
            
            # Filter for subcommittee links
            if ('subcommittee' in href.lower() or 'subcommittee' in text.lower()) and text:
                subcommittee_url = URLNormalizer.normalize_url(href, self.BASE_URL)
                
                # Clean subcommittee name
                subcommittee_name = text.replace('Subcommittee on ', '').replace('Subcommittee', '').strip()
                
                if subcommittee_name and committee.id:
                    subcommittee = Subcommittee(
                        name=subcommittee_name,
                        parent_committee_id=committee.id,
                        official_url=subcommittee_url,
                        subcommittee_code=TextCleaner.extract_committee_code(text) or "",
                        description=f"House {text}"
                    )
                    subcommittees.append(subcommittee)
        
        return subcommittees
    
    def scrape_hearings(self, committee: Committee, subcommittee: Optional[Subcommittee] = None) -> List[Hearing]:
        """Scrape hearings for a committee or subcommittee."""
        hearings = []
        
        # Determine which URL to scrape
        target_url = subcommittee.official_url if subcommittee else committee.official_url
        
        soup = self.get_soup(target_url)
        if not soup:
            return hearings
        
        # Look for hearing links and information
        hearing_links = soup.find_all('a', href=True)
        
        for link in hearing_links:
            href = link.get('href', '')
            text = TextCleaner.clean_text(link.get_text())
            
            # Filter for hearing links
            if any(keyword in href.lower() for keyword in ['hearing', 'markup', 'meeting']) and text:
                hearing_url = URLNormalizer.normalize_url(href, self.BASE_URL)
                
                # Extract hearing information
                hearing_title = text[:200]  # Truncate long titles
                
                # Try to extract date from text
                dates = TextCleaner.extract_date_patterns(text)
                hearing_date = None
                if dates:
                    try:
                        # Try to parse the first date found
                        date_str = dates[0]
                        hearing_date = datetime.strptime(date_str, '%m/%d/%Y')
                    except:
                        pass
                
                hearing = Hearing(
                    committee_id=committee.id,
                    subcommittee_id=subcommittee.id if subcommittee else None,
                    title=hearing_title,
                    hearing_date=hearing_date,
                    hearing_url=hearing_url,
                    status='scheduled'
                )
                hearings.append(hearing)
        
        return hearings
    
    def scrape_hearing_video(self, hearing: Hearing) -> List[VideoFormat]:
        """Scrape video information for a specific hearing."""
        video_formats = []
        
        soup = self.get_soup(hearing.hearing_url)
        if not soup:
            return video_formats
        
        # Use video format detector to find streaming platforms
        detected_formats = VideoFormatDetector.detect_streaming_platform(soup, hearing.hearing_url)
        
        for format_info in detected_formats:
            video_format = VideoFormat(
                hearing_id=hearing.id,
                platform=format_info.get('platform', 'unknown'),
                video_id=format_info.get('video_id', ''),
                embed_code=format_info.get('embed_code', ''),
                streaming_url=format_info.get('streaming_url', ''),
                player_type=format_info.get('player_type', 'unknown')
            )
            
            # Extract additional technical details
            if format_info.get('platform') == 'youtube':
                video_format.set_technical_details({
                    'embed_url': format_info.get('embed_url', ''),
                    'watch_url': format_info.get('watch_url', ''),
                    'platform_features': ['autoplay', 'controls', 'fullscreen']
                })
            
            video_formats.append(video_format)
        
        return video_formats
    
    def scrape_all_committees_data(self) -> Dict[str, Any]:
        """Scrape all committees, subcommittees, and hearings data."""
        start_time = datetime.now()
        results = {
            'committees': [],
            'subcommittees': [],
            'hearings': [],
            'video_formats': [],
            'scrape_logs': []
        }
        
        try:
            # Scrape committees
            committees = self.scrape_committees()
            results['committees'] = committees
            
            # Log committee scraping
            committee_log = ScrapeLog(
                target_url=self.COMMITTEES_URL,
                scrape_type='committee',
                status='success',
                records_found=len(committees),
                scrape_duration=(datetime.now() - start_time).total_seconds()
            )
            results['scrape_logs'].append(committee_log)
            
            # Scrape subcommittees and hearings for each committee
            for committee in committees:
                committee_start = datetime.now()
                
                try:
                    # Scrape subcommittees
                    subcommittees = self.scrape_committee_details(committee)
                    results['subcommittees'].extend(subcommittees)
                    
                    # Scrape hearings for main committee
                    hearings = self.scrape_hearings(committee)
                    results['hearings'].extend(hearings)
                    
                    # Scrape hearings for subcommittees
                    for subcommittee in subcommittees:
                        sub_hearings = self.scrape_hearings(committee, subcommittee)
                        results['hearings'].extend(sub_hearings)
                    
                    # Log successful committee scraping
                    committee_log = ScrapeLog(
                        target_url=committee.official_url,
                        scrape_type='committee_detail',
                        status='success',
                        records_found=len(subcommittees) + len(hearings),
                        scrape_duration=(datetime.now() - committee_start).total_seconds()
                    )
                    results['scrape_logs'].append(committee_log)
                    
                except Exception as e:
                    # Log failed committee scraping
                    committee_log = ScrapeLog(
                        target_url=committee.official_url,
                        scrape_type='committee_detail',
                        status='failed',
                        error_message=str(e),
                        scrape_duration=(datetime.now() - committee_start).total_seconds()
                    )
                    results['scrape_logs'].append(committee_log)
            
            # Scrape video formats for hearings (sample first 10 to avoid overwhelming)
            for hearing in results['hearings'][:10]:
                hearing_start = datetime.now()
                
                try:
                    video_formats = self.scrape_hearing_video(hearing)
                    results['video_formats'].extend(video_formats)
                    
                    # Log successful hearing video scraping
                    hearing_log = ScrapeLog(
                        target_url=hearing.hearing_url,
                        scrape_type='video',
                        status='success',
                        records_found=len(video_formats),
                        scrape_duration=(datetime.now() - hearing_start).total_seconds()
                    )
                    results['scrape_logs'].append(hearing_log)
                    
                except Exception as e:
                    # Log failed hearing video scraping
                    hearing_log = ScrapeLog(
                        target_url=hearing.hearing_url,
                        scrape_type='video',
                        status='failed',
                        error_message=str(e),
                        scrape_duration=(datetime.now() - hearing_start).total_seconds()
                    )
                    results['scrape_logs'].append(hearing_log)
        
        except Exception as e:
            # Log overall failure
            overall_log = ScrapeLog(
                target_url=self.COMMITTEES_URL,
                scrape_type='full_scrape',
                status='failed',
                error_message=str(e),
                scrape_duration=(datetime.now() - start_time).total_seconds()
            )
            results['scrape_logs'].append(overall_log)
        
        return results