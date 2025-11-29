# Enhanced Data Scraper - The Unsung Heroines

## Overview

This enhanced scraper system combines data from multiple feminist-focused sources to create comprehensive, well-sourced biographies of women throughout history.

## Data Sources

1. **Wikidata** - Structured data with verifiable citations
2. **Wikipedia** - Biographical content with Wikidata linking
3. **National Women's History Museum** (NWHM) - Feminist-focused biographies (manual URL collection required)

## Files

- `wikidata_scraper.py` - SPARQL queries to Wikidata
- `enhanced_scraper.py` - Main orchestrator combining all sources
- `data_merger.py` - Intelligent deduplication and data merging
- `nwhm_scraper.py` - Web scraper for NWHM (with caching)
- `scraper.py` - Original Wikipedia scraper (legacy)

## Usage

### Quick Start

Run the enhanced scraper to collect data from Wikidata and Wikipedia:

```bash
python enhanced_scraper.py
```

This will:
1. Query Wikidata for 500 women in various fields
2. Scrape Wikipedia categories for additional women
3. Merge and deduplicate all data
4. Save to `unsung_heroines_data.json` with full source attribution

### Individual Modules

**Wikidata only:**
```bash
python wikidata_scraper.py
```

**NWHM (requires manual URL list):**
```bash
python nwhm_scraper.py
```

## Data Structure

The enhanced JSON format includes:

```json
{
  "id": "unique_identifier",
  "name": "Full Name",
  "birth_date": "YYYY-MM-DD",
  "death_date": "YYYY-MM-DD",
  "biography": "Combined biography from all sources",
  "accomplishments": ["Achievement 1", "Achievement 2"],
  "fields": ["science", "activism"],
  "image": "url",
  "image_credit": "Attribution",
  "sources": [
    {
      "name": "Wikipedia",
      "url": "https://...",
      "accessed": "YYYY-MM-DD"
    }
  ],
  "wikidata_id": "Q12345",
  "last_updated": "YYYY-MM-DD"
}
```

## Ethical Guidelines

### Rate Limiting
- **Wikidata**: 2 second delay between requests
- **Wikipedia**: 2 second delay between requests
- **NWHM**: 3 second delay + caching to minimize requests

### Attribution
- All sources are tracked in the `sources` array
- Website displays source links for each heroine
- Image credits are preserved

### Respect robots.txt
- Check robots.txt before scraping any new site
- Use caching to avoid repeated requests
- Consider contacting sites for API access or partnerships

## Update Schedule

**Recommended**: Run scraper monthly, not daily

```bash
# Monthly update
python enhanced_scraper.py
```

## Website Integration

The website (`index.html`) automatically displays:
- Source attributions for each biography
- Image credits
- Access dates for all sources

Sources appear at the bottom of each heroine's profile with clickable links.

## Dependencies

```bash
pip install requests beautifulsoup4
```

## Configuration

Edit `enhanced_scraper.py` to customize:

```python
# Wikipedia categories to scrape
wikipedia_categories = [
    'Women scientists',
    'Women physicians',
    'Women activists',
    # Add more categories
]

# Number of entries to fetch
wikidata_limit = 500
wikipedia_limit_per_category = 50
```

## Troubleshooting

**"No module named 'requests'"**
```bash
pip install requests
```

**NWHM scraping fails**
- Check robots.txt: https://www.womenshistory.org/robots.txt
- Ensure you have manual URL list
- Consider contacting NWHM for partnership

**Duplicate entries**
- The data merger automatically deduplicates by:
  - Wikidata ID (most reliable)
  - Name similarity + birth date
  - High name similarity (>92%)

## Contributing

To add new data sources:

1. Create a new scraper module (e.g., `newsource_scraper.py`)
2. Return data in the standard format
3. Add to `enhanced_scraper.py` orchestrator
4. Update this README

## License

Educational use. Always provide proper attribution to sources.

## Contact

For questions or partnerships with data sources, contact: [your email]
