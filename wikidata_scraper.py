"""
Wikidata SPARQL Scraper for The Unsung Heroines
Queries Wikidata for women in various fields with verifiable sources.
"""

import requests
import json
from datetime import datetime
import time

class WikidataScraper:
    """Scraper for Wikidata using SPARQL queries."""
    
    ENDPOINT = "https://query.wikidata.org/sparql"
    USER_AGENT = "TheUnsungHeroines/2.0 (Educational Project; https://github.com/yourusername/theunsungheroines)"
    
    # Broader SPARQL query: science, arts, activism, politics, literature, music.
    # Only returns entries that have a portrait image (wdt:P18) and an English
    # Wikipedia article, which dramatically improves data quality.
    QUERY_TEMPLATE = """
    SELECT DISTINCT ?person ?personLabel ?birthDate ?deathDate ?occupationLabel
                    ?description ?image ?wikipediaUrl ?wikidataUrl
    WHERE {{
      ?person wdt:P31 wd:Q5 .              # instance of human
      ?person wdt:P21 wd:Q6581072 .        # gender: female
      ?person wdt:P106 ?occupation .       # has occupation
      ?person wdt:P18 ?image .             # must have a portrait image

      # English Wikipedia article required (ensures good biography available)
      ?article schema:about ?person ;
               schema:inLanguage "en" ;
               schema:isPartOf <https://en.wikipedia.org/> .
      BIND(STR(?article) AS ?wikipediaUrl)

      # Occupations: science, medicine, arts, activism, politics, literature, music
      VALUES ?occupation {{
        wd:Q901    wd:Q11063  wd:Q593644  wd:Q169470  wd:Q82955
        wd:Q1650915 wd:Q864503 wd:Q1622272 wd:Q205375
        wd:Q36180  wd:Q482980 wd:Q33999   wd:Q483501  wd:Q36834
        wd:Q177220 wd:Q170790 wd:Q1234099 wd:Q15627169
        wd:Q4220920 wd:Q1281618 wd:Q11569986 wd:Q18939491
      }}

      OPTIONAL {{ ?person wdt:P569 ?birthDate . }}
      OPTIONAL {{ ?person wdt:P570 ?deathDate . }}
      OPTIONAL {{ ?person schema:description ?description .
                  FILTER(LANG(?description) = "en") }}

      BIND(CONCAT("https://www.wikidata.org/wiki/",
                  SUBSTR(STR(?person), 32)) AS ?wikidataUrl)

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    OFFSET {offset}
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})
    
    def query_wikidata(self, limit=100, offset=0):
        """Execute SPARQL query against Wikidata endpoint."""
        query = self.QUERY_TEMPLATE.format(limit=limit, offset=offset)
        
        try:
            response = self.session.get(
                self.ENDPOINT,
                params={'query': query, 'format': 'json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying Wikidata: {e}")
            return None
    
    @staticmethod
    def _thumbnail_url(commons_url, width=400):
        """Convert a Wikimedia Commons FilePath URL to a sized thumbnail URL."""
        if not commons_url:
            return None
        # Already a thumbnail or external image — return as-is
        if 'Special:FilePath' not in commons_url:
            return commons_url
        filename = commons_url.split('Special:FilePath/')[-1]
        return (
            f"https://commons.wikimedia.org/w/index.php"
            f"?title=Special:FilePath/{filename}&width={width}"
        )

    def parse_results(self, results):
        """Parse SPARQL results into structured data."""
        if not results or 'results' not in results:
            return []

        women_data = []
        bindings = results['results']['bindings']

        for binding in bindings:
            try:
                wikidata_uri = binding.get('person', {}).get('value', '')
                wikidata_id = wikidata_uri.split('/')[-1] if wikidata_uri else None

                raw_image = binding.get('image', {}).get('value')
                image_url = self._thumbnail_url(raw_image)

                wikidata_url = binding.get('wikidataUrl', {}).get('value', '')
                wikipedia_url = binding.get('wikipediaUrl', {}).get('value', '')

                sources = [{'name': 'Wikidata', 'url': wikidata_url,
                            'accessed': datetime.now().strftime('%Y-%m-%d')}]
                if wikipedia_url:
                    sources.append({'name': 'Wikipedia', 'url': wikipedia_url,
                                    'accessed': datetime.now().strftime('%Y-%m-%d')})

                woman_data = {
                    'id': wikidata_id,
                    'name': binding.get('personLabel', {}).get('value', 'Unknown'),
                    'birth_date': binding.get('birthDate', {}).get('value', '').split('T')[0],
                    'death_date': binding.get('deathDate', {}).get('value', '').split('T')[0],
                    'description': binding.get('description', {}).get('value', ''),
                    'occupation': binding.get('occupationLabel', {}).get('value', ''),
                    'image': image_url,
                    'image_credit': 'Image: Wikimedia Commons' if image_url else '',
                    'sources': sources,
                    'wikidata_id': wikidata_id,
                    'last_updated': datetime.now().strftime('%Y-%m-%d'),
                }

                women_data.append(woman_data)
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue

        return women_data
    
    def scrape(self, total_limit=500):
        """Scrape women data from Wikidata."""
        all_women = []
        batch_size = 100
        offset = 0
        
        print(f"Starting Wikidata scrape (target: {total_limit} entries)...")
        
        while offset < total_limit:
            print(f"Fetching batch at offset {offset}...")
            results = self.query_wikidata(limit=batch_size, offset=offset)
            
            if not results:
                print("No more results or error occurred.")
                break
            
            women_batch = self.parse_results(results)
            if not women_batch:
                print("No women found in this batch.")
                break
            
            all_women.extend(women_batch)
            print(f"Retrieved {len(women_batch)} entries. Total: {len(all_women)}")
            
            offset += batch_size
            time.sleep(2)  # Respectful delay
        
        print(f"Wikidata scrape complete. Total entries: {len(all_women)}")
        return all_women

def main():
    """Main function to run Wikidata scraper."""
    scraper = WikidataScraper()
    women_data = scraper.scrape(total_limit=500)
    
    # Save to JSON
    output_file = 'wikidata_heroines.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(women_data, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to {output_file}")
    print(f"Total women scraped: {len(women_data)}")

if __name__ == "__main__":
    main()
