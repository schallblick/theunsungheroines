"""
NWHM (National Women's History Museum) Scraper
Respectful web scraper with caching for the National Women's History Museum.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class NWHMScraper:
    """Scraper for National Women's History Museum biographies."""
    
    BASE_URL = "https://www.womenshistory.org"
    USER_AGENT = "TheUnsungHeroines/2.0 (Educational Project; Contact: your.email@example.com)"
    CACHE_FILE = "nwhm_cache.json"
    
    def __init__(self, use_cache=True):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})
        self.use_cache = use_cache
        self.cache = self.load_cache() if use_cache else {}
    
    def load_cache(self):
        """Load cached data to avoid re-scraping."""
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
        return {}
    
    def save_cache(self):
        """Save cache to file."""
        try:
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def check_robots_txt(self):
        """Check robots.txt for scraping permissions."""
        try:
            response = self.session.get(f"{self.BASE_URL}/robots.txt", timeout=10)
            print("robots.txt content:")
            print(response.text[:500])
            return True
        except Exception as e:
            print(f"Could not fetch robots.txt: {e}")
            return False
    
    def get_biography_list(self):
        """
        Get list of biography URLs from NWHM.
        Note: This is a placeholder - actual implementation would need to
        navigate the site structure or use their search/browse features.
        """
        # This would need to be customized based on NWHM's actual site structure
        # For now, returning empty list as we need to respect their site
        print("Note: NWHM scraping requires manual URL collection or API access.")
        print("Please check robots.txt and site terms before scraping.")
        return []
    
    def scrape_biography(self, url):
        """Scrape a single biography page."""
        # Check cache first
        if url in self.cache:
            print(f"Using cached data for {url}")
            return self.cache[url]
        
        try:
            print(f"Fetching {url}...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data (structure depends on NWHM's HTML)
            # This is a template - actual selectors need to be determined
            name = soup.find('h1')
            name = name.text.strip() if name else "Unknown"
            
            # Look for biography content
            bio_content = soup.find('div', class_='biography-content') or soup.find('article')
            biography = bio_content.get_text(strip=True) if bio_content else ""
            
            # Extract dates if available
            dates = soup.find('span', class_='dates')
            birth_date = ""
            death_date = ""
            if dates:
                date_text = dates.text
                # Parse dates (format varies)
                # This would need custom parsing logic
            
            woman_data = {
                'name': name,
                'biography': biography,
                'birth_date': birth_date,
                'death_date': death_date,
                'sources': [{
                    'name': 'National Women\'s History Museum',
                    'url': url,
                    'accessed': datetime.now().strftime('%Y-%m-%d')
                }],
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Cache the result
            if self.use_cache:
                self.cache[url] = woman_data
                self.save_cache()
            
            return woman_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape(self, urls=None):
        """Scrape multiple biographies."""
        if not urls:
            print("No URLs provided. Please provide a list of biography URLs.")
            print("Example URLs should be collected manually or from a sitemap.")
            return []
        
        women_data = []
        
        for idx, url in enumerate(urls, 1):
            print(f"Processing {idx}/{len(urls)}: {url}")
            
            data = self.scrape_biography(url)
            if data:
                women_data.append(data)
            
            # Respectful delay
            time.sleep(3)
        
        return women_data

def main():
    """Main function - demonstrates usage."""
    scraper = NWHMScraper(use_cache=True)
    
    # Check robots.txt first
    print("Checking robots.txt...")
    scraper.check_robots_txt()
    
    print("\n" + "="*60)
    print("IMPORTANT: NWHM Scraping Guidelines")
    print("="*60)
    print("1. Always check robots.txt before scraping")
    print("2. Use respectful delays (3+ seconds)")
    print("3. Cache results to minimize requests")
    print("4. Consider contacting NWHM for API access or data partnership")
    print("5. Provide proper attribution on your website")
    print("="*60)
    
    # Example usage (with manual URL list):
    # example_urls = [
    #     "https://www.womenshistory.org/education-resources/biographies/ada-lovelace",
    #     # Add more URLs here
    # ]
    # women_data = scraper.scrape(example_urls)
    # 
    # with open('nwhm_heroines.json', 'w', encoding='utf-8') as f:
    #     json.dump(women_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
