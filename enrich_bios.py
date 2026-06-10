"""
Bio Enrichment Script — The Unsung Heroines
Finds entries with thin biographies and fills them in from Wikipedia.
Also backfills missing images where possible.
Run this whenever data quality needs a refresh.
"""

import json
import requests
import time
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WIKI_API   = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "TheUnsungHeroines/2.0 (Educational Project)"
MIN_BIO_LEN = 300   # entries shorter than this get re-fetched
SLEEP_SECS  = 2.5   # polite delay between Wikipedia calls

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def current_bio(entry):
    return entry.get("biography") or entry.get("extract") or entry.get("description") or ""


def wikipedia_title_from_sources(entry):
    """Return a Wikipedia article title from the entry's sources list, or None."""
    for src in entry.get("sources", []):
        url = src.get("url", "")
        if "en.wikipedia.org/wiki/" in url:
            raw = url.split("/wiki/")[-1]
            return requests.utils.unquote(raw).replace("_", " ")
    return None


def wikipedia_search(name, retries=3):
    """Search Wikipedia for a person by name. Returns the best-matching page title,
    or None if nothing credible is found."""
    for attempt in range(retries):
        try:
            resp = session.get(
                WIKI_API,
                params={
                    "action":  "query",
                    "format":  "json",
                    "list":    "search",
                    "srsearch": name,
                    "srnamespace": 0,
                    "srlimit": 1,
                },
                timeout=15,
            )
            if resp.status_code == 429:
                wait = 10 * (2 ** attempt)
                print(f"    Rate-limited — waiting {wait}s…")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            hits = resp.json().get("query", {}).get("search", [])
            if not hits:
                return None
            result_title = hits[0]["title"]
            # Accept if names share meaningful overlap (avoids total mismatches)
            name_words  = set(name.lower().split())
            title_words = set(result_title.lower().split())
            if name_words & title_words:
                return result_title
            return None
        except Exception as exc:
            print(f"    Search warning: {exc}")
            return None
    return None


def fetch_wikipedia(title, retries=3):
    """Return (extract, thumbnail_url) for a Wikipedia article title."""
    for attempt in range(retries):
        try:
            resp = session.get(
                WIKI_API,
                params={
                    "action":      "query",
                    "format":      "json",
                    "prop":        "extracts|pageimages",
                    "titles":      title,
                    "exintro":     True,
                    "explaintext": True,
                    "pithumbsize": 500,
                },
                timeout=15,
            )
            if resp.status_code == 429:
                wait = 10 * (2 ** attempt)
                print(f"    Rate-limited — waiting {wait}s…")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            page = next(iter(resp.json()["query"]["pages"].values()))
            if page.get("missing"):
                return None, None
            return page.get("extract") or None, page.get("thumbnail", {}).get("source")
        except Exception as exc:
            print(f"    Warning: {exc}")
            return None, None
    return None, None


def enrich(data):
    need_bio   = [e for e in data if len(current_bio(e)) < MIN_BIO_LEN]
    need_image = [e for e in data if not e.get("image")]

    targets = {id(e): e for e in need_bio}
    for e in need_image:
        targets[id(e)] = e   # also backfill images on image-less entries

    print(f"Entries needing bio enrichment  : {len(need_bio)}")
    print(f"Entries needing image backfill  : {len(need_image)}")
    print(f"Unique entries to process       : {len(targets)}")
    print()

    updated_bio   = 0
    updated_image = 0

    for idx, entry in enumerate(targets.values(), 1):
        name  = entry.get("name", "?")
        title = wikipedia_title_from_sources(entry)

        if not title:
            # Fall back to searching Wikipedia by name
            title = wikipedia_search(name)
            if title:
                print(f"[{idx}/{len(targets)}] Search found '{title}' for: {name}")
            else:
                print(f"[{idx}/{len(targets)}] SKIP (not found on Wikipedia): {name}")
                continue
            time.sleep(SLEEP_SECS)

        bio_short = len(current_bio(entry)) < MIN_BIO_LEN
        img_missing = not entry.get("image")

        if not bio_short and not img_missing:
            continue   # nothing to do

        print(f"[{idx}/{len(targets)}] Fetching: {name}  ({title})")
        extract, image_url = fetch_wikipedia(title)

        if bio_short and extract and len(extract) > len(current_bio(entry)):
            entry["biography"] = extract
            updated_bio += 1
            print(f"    Bio updated: {len(extract)} chars")

        if img_missing and image_url:
            entry["image"]        = image_url
            entry["image_credit"] = "Image: Wikipedia / Wikimedia Commons"
            # Add Wikipedia to sources if not already there
            wiki_url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(title.replace(' ', '_'), safe='/:')}"
            if not any("wikipedia" in s.get("url", "") for s in entry.get("sources", [])):
                entry.setdefault("sources", []).append({
                    "name":     "Wikipedia",
                    "url":      wiki_url,
                    "accessed": datetime.now().strftime("%Y-%m-%d"),
                })
            updated_image += 1
            print(f"    Image backfilled")

        entry["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        time.sleep(SLEEP_SECS)

    return updated_bio, updated_image


def main():
    input_file  = "unsung_heroines_data.json"
    output_file = "unsung_heroines_data.json"

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries from {input_file}")
    print("=" * 60)

    updated_bio, updated_image = enrich(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"Bios updated  : {updated_bio}")
    print(f"Images added  : {updated_image}")
    images_total = sum(1 for e in data if e.get("image"))
    print(f"Total with images: {images_total}/{len(data)}")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
