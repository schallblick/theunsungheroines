"""
Nobel Prize Scraper for The Unsung Heroines
Uses the official Nobel Prize API (https://api.nobelprize.org/2.1/) to fetch
all female laureates, then enriches each entry with a Wikipedia biography and
portrait image.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Ensure UTF-8 output on Windows so laureate names with special characters print correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


CATEGORY_LABELS = {
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'medicine': 'Medicine & Physiology',
    'literature': 'Literature',
    'peace': 'Peace & Activism',
    'economic sciences': 'Economics',
}


class NobelScraper:
    NOBEL_API = "https://api.nobelprize.org/2.1/laureates"
    WIKI_API = "https://en.wikipedia.org/w/api.php"
    USER_AGENT = "TheUnsungHeroines/2.0 (Educational Project)"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    # ------------------------------------------------------------------
    # Nobel API
    # ------------------------------------------------------------------

    def fetch_female_laureates(self):
        """Return raw laureate dicts for all female Nobel Prize winners."""
        all_laureates = []
        offset = 0
        limit = 100

        while True:
            try:
                resp = self.session.get(
                    self.NOBEL_API,
                    params={"gender": "female", "format": "json",
                            "limit": limit, "offset": offset},
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
                batch = data.get("laureates", [])
                if not batch:
                    break
                all_laureates.extend(batch)
                # If the page was smaller than the limit we've reached the end
                if len(batch) < limit:
                    break
                offset += limit
                time.sleep(0.5)
            except Exception as exc:
                print(f"Error fetching Nobel laureates at offset {offset}: {exc}")
                break

        return all_laureates

    # ------------------------------------------------------------------
    # Wikipedia enrichment
    # ------------------------------------------------------------------

    def get_wikipedia_data(self, wiki_url):
        """Return (extract, thumbnail_url) for a Wikipedia article URL.

        Retries up to 3 times with exponential back-off on HTTP 429.
        """
        if not wiki_url:
            return "", None

        title = wiki_url.rstrip("/").split("/wiki/")[-1]

        for attempt in range(3):
            try:
                resp = self.session.get(
                    self.WIKI_API,
                    params={
                        "action": "query",
                        "format": "json",
                        "prop": "extracts|pageimages",
                        "titles": title,
                        "exintro": True,
                        "explaintext": True,
                        "pithumbsize": 500,
                    },
                    timeout=15,
                )
                if resp.status_code == 429:
                    wait = 5 * (2 ** attempt)
                    print(f"  Rate-limited; waiting {wait}s before retry...")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                page = next(iter(resp.json()["query"]["pages"].values()))
                if page.get("missing"):
                    return "", None
                extract = page.get("extract", "")
                image = page.get("thumbnail", {}).get("source")
                return extract, image
            except requests.exceptions.HTTPError:
                raise
            except Exception as exc:
                print(f"  Warning: Wikipedia fetch failed for {wiki_url}: {exc}")
                return "", None

        print(f"  Giving up on Wikipedia fetch for {wiki_url} after retries.")
        return "", None

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _best_name(self, laureate):
        known = laureate.get("knownName", {}).get("en", "")
        given = laureate.get("givenName", {}).get("en", "")
        family = laureate.get("familyName", {}).get("en", "")
        return known or f"{given} {family}".strip() or "Unknown"

    def parse_laureate(self, laureate):
        name = self._best_name(laureate)
        if name == "Unknown":
            return None

        # Nobel API v2.1 may return dates as plain strings OR nested {"date": "..."} objects
        def _extract_date(val):
            if not val:
                return ""
            if isinstance(val, dict):
                val = val.get("date", "")
            return str(val)[:10]

        birth_date = _extract_date(laureate.get("born"))
        death_date = _extract_date(laureate.get("died"))
        # Nobel API uses "0000-00-00" for living people
        if death_date.startswith("0000"):
            death_date = ""

        prizes = laureate.get("nobelPrizes", [])
        fields = []
        motivations = []
        sources = []

        for prize in prizes:
            category_raw = prize.get("category", {}).get("en", "").lower()
            year = prize.get("awardYear", "")
            motivation = prize.get("motivation", {}).get("en", "")
            category_label = CATEGORY_LABELS.get(category_raw, prize.get("category", {}).get("en", category_raw))

            fields.append(f"{category_label} (Nobel {year})")

            if motivation:
                motivations.append(
                    f"Nobel Prize in {category_label} ({year}): {motivation}"
                )

            # Nobel Prize page link
            prize_links = prize.get("links", [])
            for link in prize_links:
                href = link.get("href", "")
                if "nobelprize.org" in href and "/prizes/" in href:
                    sources.append({
                        "name": f"Nobel Prize in {category_label} ({year})",
                        "url": href,
                        "accessed": datetime.now().strftime("%Y-%m-%d"),
                    })
                    break

        # Wikipedia link
        wiki_url = laureate.get("wikipedia", {}).get("english", "")
        if not wiki_url:
            # Fall back to links array
            for link in laureate.get("links", []):
                if "wikipedia.org" in link.get("href", ""):
                    wiki_url = link["href"]
                    break

        biography = " ".join(motivations)
        image = None
        image_credit = ""

        if wiki_url:
            print(f"  Fetching Wikipedia: {wiki_url}")
            bio_text, img_url = self.get_wikipedia_data(wiki_url)
            if bio_text:
                biography = bio_text
            if img_url:
                image = img_url
                image_credit = "Image: Wikipedia / Wikimedia Commons"
            sources.append({
                "name": "Wikipedia",
                "url": wiki_url,
                "accessed": datetime.now().strftime("%Y-%m-%d"),
            })
            time.sleep(3)  # Respect Wikipedia's rate limit

        # Always list Nobel API as a source
        sources.insert(0, {
            "name": "Nobel Prize API",
            "url": f"https://api.nobelprize.org/2.1/laureate/{laureate.get('id')}",
            "accessed": datetime.now().strftime("%Y-%m-%d"),
        })

        wikidata_id = laureate.get("wikidata", {}).get("id")

        return {
            "name": name,
            "birth_date": birth_date,
            "death_date": death_date,
            "biography": biography,
            "fields": fields,
            "image": image,
            "image_credit": image_credit,
            "sources": sources,
            "wikidata_id": wikidata_id,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def scrape(self):
        print("Fetching female Nobel laureates from Nobel Prize API...")
        raw_laureates = self.fetch_female_laureates()
        print(f"Found {len(raw_laureates)} female laureates.")

        results = []
        for i, laureate in enumerate(raw_laureates, 1):
            display_name = self._best_name(laureate)
            print(f"[{i}/{len(raw_laureates)}] {display_name}")
            entry = self.parse_laureate(laureate)
            if entry:
                results.append(entry)

        print(f"\nNoble scraping complete. {len(results)} entries.")
        return results


def main():
    scraper = NobelScraper()
    data = scraper.scrape()

    output_file = "nobel_heroines.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    images_found = sum(1 for d in data if d.get("image"))
    print(f"Saved {len(data)} laureates to {output_file}")
    print(f"Entries with images: {images_found}/{len(data)}")


if __name__ == "__main__":
    main()
