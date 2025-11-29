"""
Enhanced Scraper for The Unsung Heroines
Main orchestrator that combines data from multiple sources.
"""

import json
from datetime import datetime
import sys

# Import our custom modules
from wikidata_scraper import WikidataScraper
from data_merger import DataMerger

# Import enhanced Wikipedia functions
import requests
import time

def get_enhanced_wikipedia_data(page_title):
    """Enhanced Wikipedia scraper with Wikidata ID linking."""
    headers = {
        'User-Agent': 'TheUnsungHeroines/2.0 (Educational Project)'
    }
    
    # Get page data including Wikidata ID
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts|pageimages|info|pageprops&titles={page_title}&exintro=true&explaintext=true&pithumbsize=300&inprop=url&ppprop=wikibase_item"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        
        if page.get('missing'):
            print(f"Warning: Page '{page_title}' not found.")
            return None
        
        # Extract Wikidata ID if available
        wikidata_id = page.get('pageprops', {}).get('wikibase_item')
        
        return {
            'name': page.get('title'),
            'biography': page.get('extract'),
            'image': page.get('thumbnail', {}).get('source'),
            'sources': [{
                'name': 'Wikipedia',
                'url': page.get('fullurl'),
                'accessed': datetime.now().strftime('%Y-%m-%d')
            }],
            'wikidata_id': wikidata_id,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    except Exception as e:
        print(f"Error fetching Wikipedia data for {page_title}: {e}")
        return None

def get_wikipedia_category_members(category_title):
    """Get list of women from a Wikipedia category."""
    headers = {
        'User-Agent': 'TheUnsungHeroines/2.0 (Educational Project)'
    }
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category:{category_title}&cmlimit=500"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        return [member['title'] for member in data['query']['categorymembers']]
    except Exception as e:
        print(f"Error fetching category {category_title}: {e}")
        return []

def scrape_wikipedia_enhanced(categories, limit_per_category=50):
    """Scrape Wikipedia with enhanced data structure."""
    all_women = []
    
    print(f"Scraping {len(categories)} Wikipedia categories...")
    
    for category in categories:
        print(f"\nProcessing category: {category}")
        titles = get_wikipedia_category_members(category)
        
        if not titles:
            continue
        
        # Limit titles per category
        titles = titles[:limit_per_category]
        
        for idx, title in enumerate(titles, 1):
            # Filter out non-person pages
            if title.startswith(('Category:', 'List of', 'Index of', 'Timeline of', 'Women in')):
                continue
            
            print(f"  [{idx}/{len(titles)}] Fetching: {title}")
            woman_data = get_enhanced_wikipedia_data(title)
            
            if woman_data:
                all_women.append(woman_data)
            
            time.sleep(2)  # Respectful delay
    
    print(f"\nWikipedia scraping complete. Total entries: {len(all_women)}")
    return all_women

def main():
    """Main orchestrator for enhanced scraping."""
    print("="*70)
    print("THE UNSUNG HEROINES - Enhanced Data Collection")
    print("="*70)
    print()
    
    # Configuration
    wikipedia_categories = [
        'Women scientists',
        'Women physicians',
        'Lesbian scientists',
        'Jewish women scientists',
        'Women activists',
        'Women mathematicians'
    ]
    
    wikidata_limit = 500
    wikipedia_limit_per_category = 50
    
    # Step 1: Scrape Wikidata
    print("\n[1/3] Scraping Wikidata...")
    print("-" * 70)
    wikidata_scraper = WikidataScraper()
    wikidata_data = wikidata_scraper.scrape(total_limit=wikidata_limit)
    
    # Save Wikidata results
    with open('wikidata_heroines.json', 'w', encoding='utf-8') as f:
        json.dump(wikidata_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(wikidata_data)} entries to wikidata_heroines.json")
    
    # Step 2: Scrape Wikipedia
    print("\n[2/3] Scraping Wikipedia...")
    print("-" * 70)
    wikipedia_data = scrape_wikipedia_enhanced(
        wikipedia_categories,
        limit_per_category=wikipedia_limit_per_category
    )
    
    # Save Wikipedia results
    with open('wikipedia_heroines.json', 'w', encoding='utf-8') as f:
        json.dump(wikipedia_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(wikipedia_data)} entries to wikipedia_heroines.json")
    
    # Step 3: Merge all data
    print("\n[3/3] Merging data from all sources...")
    print("-" * 70)
    merger = DataMerger()
    merged_data = merger.merge_datasets(wikidata_data, wikipedia_data)
    
    # Save merged results
    merger.save_to_json('unsung_heroines_data.json')
    
    # Print statistics
    print("\n" + "="*70)
    print("SCRAPING COMPLETE - Statistics")
    print("="*70)
    print(f"Wikidata entries:    {len(wikidata_data)}")
    print(f"Wikipedia entries:   {len(wikipedia_data)}")
    print(f"Total raw entries:   {len(wikidata_data) + len(wikipedia_data)}")
    print(f"Merged unique women: {len(merged_data)}")
    print(f"Duplicates removed:  {len(wikidata_data) + len(wikipedia_data) - len(merged_data)}")
    print("="*70)
    
    # Print sample entry with sources
    if merged_data:
        print("\nSample entry with sources:")
        print("-" * 70)
        sample = merged_data[0]
        print(f"Name: {sample.get('name')}")
        print(f"Biography: {sample.get('biography', '')[:200]}...")
        print(f"Sources ({len(sample.get('sources', []))}):")
        for source in sample.get('sources', []):
            print(f"  - {source.get('name')}: {source.get('url')}")
    
    print("\n[OK] All data saved to unsung_heroines_data.json")
    print("\nNote: To add NWHM data, manually collect URLs and run nwhm_scraper.py")

if __name__ == "__main__":
    main()
