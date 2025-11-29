"""
Automated Test Suite for The Unsung Heroines Scraper System
Tests data merging, deduplication, and data structure validation.
"""

import json
import sys
from datetime import datetime

# Test data samples
SAMPLE_WIKIDATA_ENTRY = {
    'id': 'Q7251',
    'name': 'Ada Lovelace',
    'birth_date': '1815-12-10',
    'death_date': '1852-11-27',
    'description': 'English mathematician',
    'occupation': 'mathematician',
    'image': 'https://example.com/ada.jpg',
    'sources': [{
        'name': 'Wikidata',
        'url': 'https://www.wikidata.org/wiki/Q7251',
        'accessed': '2025-11-29'
    }],
    'wikidata_id': 'Q7251',
    'last_updated': '2025-11-29'
}

SAMPLE_WIKIPEDIA_ENTRY = {
    'name': 'Ada Lovelace',
    'biography': 'Augusta Ada King, Countess of Lovelace was an English mathematician...',
    'image': 'https://example.com/ada2.jpg',
    'sources': [{
        'name': 'Wikipedia',
        'url': 'https://en.wikipedia.org/wiki/Ada_Lovelace',
        'accessed': '2025-11-29'
    }],
    'wikidata_id': 'Q7251',
    'last_updated': '2025-11-29'
}

SAMPLE_DIFFERENT_WOMAN = {
    'name': 'Grace Hopper',
    'birth_date': '1906-12-09',
    'biography': 'American computer scientist...',
    'sources': [{
        'name': 'Wikipedia',
        'url': 'https://en.wikipedia.org/wiki/Grace_Hopper',
        'accessed': '2025-11-29'
    }],
    'wikidata_id': 'Q11641',
    'last_updated': '2025-11-29'
}

class TestSuite:
    """Automated test suite for scraper system."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def assert_equal(self, actual, expected, test_name):
        """Assert two values are equal."""
        if actual == expected:
            self.test_passed(test_name)
            return True
        else:
            self.test_failed(test_name, f"Expected {expected}, got {actual}")
            return False
    
    def assert_true(self, condition, test_name, message=""):
        """Assert condition is true."""
        if condition:
            self.test_passed(test_name)
            return True
        else:
            self.test_failed(test_name, message or "Condition was False")
            return False
    
    def assert_in(self, item, container, test_name):
        """Assert item is in container."""
        if item in container:
            self.test_passed(test_name)
            return True
        else:
            self.test_failed(test_name, f"{item} not found in {container}")
            return False
    
    def test_passed(self, test_name):
        """Record a passed test."""
        self.tests_passed += 1
        self.test_results.append(('PASS', test_name))
        print(f"[PASS] {test_name}")
    
    def test_failed(self, test_name, reason):
        """Record a failed test."""
        self.tests_failed += 1
        self.test_results.append(('FAIL', test_name, reason))
        print(f"[FAIL] {test_name}: {reason}")
    
    def test_data_merger(self):
        """Test data merger functionality."""
        print("\n=== Testing Data Merger ===")
        
        try:
            from data_merger import DataMerger
            merger = DataMerger()
            
            # Test 1: Add single entry
            merger.add_woman(SAMPLE_WIKIDATA_ENTRY)
            self.assert_equal(len(merger.merged_data), 1, "Add single entry")
            
            # Test 2: Merge duplicate by Wikidata ID
            merger.add_woman(SAMPLE_WIKIPEDIA_ENTRY)
            self.assert_equal(len(merger.merged_data), 1, "Merge duplicate by Wikidata ID")
            
            # Test 3: Check sources were merged
            merged_entry = list(merger.merged_data.values())[0]
            self.assert_equal(len(merged_entry['sources']), 2, "Sources merged correctly")
            
            # Test 4: Add different woman
            merger.add_woman(SAMPLE_DIFFERENT_WOMAN)
            self.assert_equal(len(merger.merged_data), 2, "Add different woman")
            
            # Test 5: Biography merging
            self.assert_true(
                'mathematician' in merged_entry['biography'].lower() or 
                'english mathematician' in merged_entry.get('description', '').lower(),
                "Biography contains expected content"
            )
            
            # Test 6: Similarity matching
            similar_name_entry = {
                'name': 'Ada King',  # Similar to Ada Lovelace
                'birth_date': '1815-12-10',
                'sources': [{'name': 'Test', 'url': 'test', 'accessed': '2025-11-29'}]
            }
            initial_count = len(merger.merged_data)
            merger.add_woman(similar_name_entry)
            # Should merge due to matching birth date
            self.assert_equal(len(merger.merged_data), initial_count, "Similar name with same birth date merged")
            
        except Exception as e:
            self.test_failed("Data Merger Import", str(e))
    
    def test_data_structure(self):
        """Test that data structure is valid."""
        print("\n=== Testing Data Structure ===")
        
        required_fields = ['name', 'sources', 'last_updated']
        optional_fields = ['birth_date', 'death_date', 'biography', 'image', 'wikidata_id', 'fields']
        
        # Test required fields
        for field in required_fields:
            self.assert_in(field, SAMPLE_WIKIDATA_ENTRY, f"Required field '{field}' present")
        
        # Test sources structure
        if 'sources' in SAMPLE_WIKIDATA_ENTRY:
            source = SAMPLE_WIKIDATA_ENTRY['sources'][0]
            self.assert_in('name', source, "Source has 'name' field")
            self.assert_in('url', source, "Source has 'url' field")
            self.assert_in('accessed', source, "Source has 'accessed' field")
    
    def test_json_validity(self):
        """Test that sample data is valid JSON."""
        print("\n=== Testing JSON Validity ===")
        
        try:
            # Test serialization
            json_str = json.dumps([SAMPLE_WIKIDATA_ENTRY, SAMPLE_WIKIPEDIA_ENTRY])
            self.test_passed("JSON serialization")
            
            # Test deserialization
            data = json.loads(json_str)
            self.assert_equal(len(data), 2, "JSON deserialization")
            
        except Exception as e:
            self.test_failed("JSON operations", str(e))
    
    def test_date_format(self):
        """Test that dates are in correct format."""
        print("\n=== Testing Date Format ===")
        
        date_fields = ['birth_date', 'death_date', 'last_updated']
        
        for field in date_fields:
            if field in SAMPLE_WIKIDATA_ENTRY and SAMPLE_WIKIDATA_ENTRY[field]:
                date_str = SAMPLE_WIKIDATA_ENTRY[field]
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    self.test_passed(f"Date format for '{field}'")
                except ValueError:
                    self.test_failed(f"Date format for '{field}'", f"Invalid format: {date_str}")
    
    def test_existing_data_file(self):
        """Test if existing data file is valid."""
        print("\n=== Testing Existing Data File ===")
        
        try:
            with open('unsung_heroines_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assert_true(isinstance(data, list), "Data is a list")
            self.assert_true(len(data) > 0, "Data contains entries")
            
            # Check first entry structure
            if data:
                entry = data[0]
                self.assert_in('name', entry, "Entry has 'name' field")
                
                # Check for old vs new format
                has_sources = 'sources' in entry
                has_old_format = 'title' in entry or 'extract' in entry
                
                if has_sources:
                    print("  -> Data file uses NEW enhanced format [OK]")
                elif has_old_format:
                    print("  -> Data file uses OLD format (needs update)")
                
        except FileNotFoundError:
            print("  [INFO] No existing data file found (this is OK for first run)")
        except Exception as e:
            self.test_failed("Existing data file", str(e))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("AUTOMATED TEST SUITE - The Unsung Heroines Scraper")
        print("="*70)
        
        self.test_data_structure()
        self.test_json_validity()
        self.test_date_format()
        self.test_data_merger()
        self.test_existing_data_file()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Total Tests:  {self.tests_passed + self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        print("="*70)
        
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result[0] == 'FAIL':
                    print(f"  [FAIL] {result[1]}: {result[2]}")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)
