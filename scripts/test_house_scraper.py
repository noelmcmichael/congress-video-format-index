#!/usr/bin/env python3
"""
Test script to debug House committee scraping.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.helpers import WebScraper
from bs4 import BeautifulSoup

def test_house_committees():
    scraper = WebScraper()
    soup = scraper.get_soup("https://www.house.gov/committees")
    
    if not soup:
        print("Failed to get page")
        return
    
    print("=== All links with 'house.gov' ===")
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        
        if '.house.gov' in href:
            print(f"Link: {text}")
            print(f"URL: {href}")
            print(f"External: {'(link is external)' in text}")
            print()

if __name__ == '__main__':
    test_house_committees()