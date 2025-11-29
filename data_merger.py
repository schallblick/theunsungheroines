"""
Data Merger for The Unsung Heroines
Combines and deduplicates data from multiple sources (Wikidata, Wikipedia, NWHM).
"""

import json
from datetime import datetime
from difflib import SequenceMatcher

class DataMerger:
    """Merges women's data from multiple sources."""
    
    def __init__(self):
        self.merged_data = {}
    
    def similarity_ratio(self, str1, str2):
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def find_matching_entry(self, woman, existing_women):
        """Find if this woman already exists in our data."""
        name = woman.get('name', '').lower()
        birth_date = woman.get('birth_date', '')
        wikidata_id = woman.get('wikidata_id')
        
        for key, existing in existing_women.items():
            # Match by Wikidata ID (most reliable)
            if wikidata_id and existing.get('wikidata_id') == wikidata_id:
                return key
            
            # Match by name similarity and birth date
            existing_name = existing.get('name', '').lower()
            if self.similarity_ratio(name, existing_name) > 0.85:
                # If names are very similar, check birth date
                if birth_date and existing.get('birth_date') == birth_date:
                    return key
                # Or if no birth date, accept high name similarity
                elif not birth_date or not existing.get('birth_date'):
                    if self.similarity_ratio(name, existing_name) > 0.92:
                        return key
        
        return None
    
    def merge_biography(self, existing_bio, new_bio):
        """Merge biographies, preferring longer/more detailed version."""
        if not existing_bio:
            return new_bio
        if not new_bio:
            return existing_bio
        
        # If one is significantly longer, use that one
        if len(new_bio) > len(existing_bio) * 1.5:
            return new_bio
        elif len(existing_bio) > len(new_bio) * 1.5:
            return existing_bio
        
        # Otherwise, combine them if they're different
        if self.similarity_ratio(existing_bio, new_bio) < 0.7:
            return f"{existing_bio}\n\n{new_bio}"
        
        return existing_bio
    
    def merge_lists(self, existing_list, new_list):
        """Merge two lists, removing duplicates."""
        if not existing_list:
            return new_list or []
        if not new_list:
            return existing_list
        
        # Combine and deduplicate
        combined = existing_list + [item for item in new_list if item not in existing_list]
        return combined
    
    def merge_woman_data(self, existing, new):
        """Merge data for a single woman from multiple sources."""
        merged = existing.copy()
        
        # Update name if new one is more complete
        if len(new.get('name', '')) > len(existing.get('name', '')):
            merged['name'] = new['name']
        
        # Use earliest birth date and latest death date if available
        if new.get('birth_date') and not existing.get('birth_date'):
            merged['birth_date'] = new['birth_date']
        if new.get('death_date') and not existing.get('death_date'):
            merged['death_date'] = new['death_date']
        
        # Merge biographies
        merged['biography'] = self.merge_biography(
            existing.get('biography', ''),
            new.get('biography', new.get('extract', new.get('description', '')))
        )
        
        # Merge accomplishments and fields
        merged['accomplishments'] = self.merge_lists(
            existing.get('accomplishments', []),
            new.get('accomplishments', [])
        )
        
        merged['fields'] = self.merge_lists(
            existing.get('fields', []),
            new.get('fields', [new.get('occupation')] if new.get('occupation') else [])
        )
        
        # Prefer image if existing doesn't have one
        if new.get('image') and not existing.get('image'):
            merged['image'] = new['image']
            merged['image_credit'] = new.get('image_credit', 'Source: ' + new.get('sources', [{}])[0].get('name', 'Unknown'))
        
        # Merge sources (always add new sources)
        merged['sources'] = self.merge_lists(
            existing.get('sources', []),
            new.get('sources', [])
        )
        
        # Keep Wikidata ID if available
        if new.get('wikidata_id') and not existing.get('wikidata_id'):
            merged['wikidata_id'] = new['wikidata_id']
        
        # Update last_updated timestamp
        merged['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        return merged
    
    def add_woman(self, woman_data):
        """Add or merge a woman's data."""
        # Find if this woman already exists
        match_key = self.find_matching_entry(woman_data, self.merged_data)
        
        if match_key:
            # Merge with existing entry
            self.merged_data[match_key] = self.merge_woman_data(
                self.merged_data[match_key],
                woman_data
            )
        else:
            # Add as new entry
            # Generate unique key
            key = woman_data.get('wikidata_id') or woman_data.get('name', '').replace(' ', '_').lower()
            counter = 1
            original_key = key
            while key in self.merged_data:
                key = f"{original_key}_{counter}"
                counter += 1
            
            # Normalize data structure
            normalized = {
                'id': woman_data.get('id') or key,
                'name': woman_data.get('name', woman_data.get('title', 'Unknown')),
                'birth_date': woman_data.get('birth_date', ''),
                'death_date': woman_data.get('death_date', ''),
                'biography': woman_data.get('biography', woman_data.get('extract', woman_data.get('description', ''))),
                'accomplishments': woman_data.get('accomplishments', []),
                'fields': woman_data.get('fields', [woman_data.get('occupation')] if woman_data.get('occupation') else []),
                'image': woman_data.get('image'),
                'image_credit': woman_data.get('image_credit', ''),
                'sources': woman_data.get('sources', []),
                'wikidata_id': woman_data.get('wikidata_id'),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.merged_data[key] = normalized
    
    def merge_datasets(self, *datasets):
        """Merge multiple datasets."""
        total_entries = sum(len(dataset) for dataset in datasets)
        print(f"Merging {len(datasets)} datasets with {total_entries} total entries...")
        
        for dataset_idx, dataset in enumerate(datasets, 1):
            print(f"Processing dataset {dataset_idx}/{len(datasets)} ({len(dataset)} entries)...")
            for woman in dataset:
                self.add_woman(woman)
        
        print(f"Merge complete. {len(self.merged_data)} unique women identified.")
        return list(self.merged_data.values())
    
    def save_to_json(self, filename='merged_heroines.json'):
        """Save merged data to JSON file."""
        data = list(self.merged_data.values())
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} entries to {filename}")

def main():
    """Test the merger with sample data."""
    merger = DataMerger()
    
    # Example: Load and merge data files
    try:
        with open('wikidata_heroines.json', 'r', encoding='utf-8') as f:
            wikidata_data = json.load(f)
    except FileNotFoundError:
        wikidata_data = []
    
    try:
        with open('unsung_heroines_data.json', 'r', encoding='utf-8') as f:
            wikipedia_data = json.load(f)
    except FileNotFoundError:
        wikipedia_data = []
    
    # Merge datasets
    merged = merger.merge_datasets(wikidata_data, wikipedia_data)
    merger.save_to_json('merged_heroines.json')
    
    print(f"Total unique women: {len(merged)}")

if __name__ == "__main__":
    main()
