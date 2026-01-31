#!/usr/bin/env python3
"""
Unit tests for inventory adjustment from production and returns
"""
import unittest
import pandas as pd
import sys
import os

# Add the src path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'uniware'))

from inventory_adjustment_from_production import process_production_returns_to_adjustment, find_matching_sku

class TestInventoryAdjustmentFromProduction(unittest.TestCase):
    
    def setUp(self):
        """Set up test data using actual returns data structure"""
        # Actual returns data from the file
        self.returns_data = {
            'DATE': ['31/1/2026', '31/1/2026', '31/1/2026', '31/1/2026', '31/1/2026', '31/1/2026', '31/1/2026'],
            'NAME': ['olive paisley print', 'Black Paisley Woven Pant', 'Wine Embroidered Set with Organza Dupatta', 
                    'Wine Embroidered Set with Organza Dupatta', 'Wine Zari Kaani Set', 'Wine Zari Kaani Set', ''],
            'bottom/top/dupatta/potli': ['BOTTOM', 'BOTTOM', 'TOP', 'BOTTOM', 'TOP', 'BOTTOM', 'BOTTOM'],
            'SIZE': ['S', 'XL', 'S', 'S', 'M', 'M', 'L'],
            'QTY': [1, 1, 1, 1, 1, 1, 1],
            'notes': ['PUT IN STOCK AGAIN', 'PUT IN STOCK AGAIN', 'PUT IN STOCK AGAIN', 
                     'PUT IN STOCK AGAIN', 'PUT IN STOCK AGAIN', 'PUT IN STOCK AGAIN', 'PUT IN STOCK AGAIN']
        }
        
        # Sample production data
        self.production_data = {
            'Date': ['31/1/2026', '31/1/2026'],
            'NAME': ['Wine Zari Kaani Set', 'olive paisley print'],
            'top/bottom': ['top', 'bottom'],
            'Size': ['M', 'S'],
            'QTY': [2, 3]
        }
        
        # Sample inventory mapping - some items exist, some don't
        self.mapping_data = {
            'Sku Code': [
                'SIMPLE_123_BOTTOM_S',
                'SIMPLE_456_TOP_S', 
                'SIMPLE_789_BOTTOM_S',
                'SIMPLE_101_TOP_M',
                'SIMPLE_102_BOTTOM_M'
            ],
            'Item Name': [
                'olive paisley print - Bottom S',
                'Wine Embroidered Set with Organza Dupatta - Top S',
                'Wine Embroidered Set with Organza Dupatta - Bottom S', 
                'Wine Zari Kaani Set - Top M',
                'Wine Zari Kaani Set - Bottom M'
            ]
        }
        
        self.returns_df = pd.DataFrame(self.returns_data)
        self.production_df = pd.DataFrame(self.production_data)
        self.mapping_df = pd.DataFrame(self.mapping_data)
    
    def test_find_matching_sku_exact_match(self):
        """Test exact SKU matching"""
        sku_mapping = {
            'olive paisley print - Bottom S': 'SIMPLE_123_BOTTOM_S'
        }
        
        result = find_matching_sku('olive paisley print', 'S', 'BOTTOM', sku_mapping)
        self.assertEqual(result, 'SIMPLE_123_BOTTOM_S')
    
    def test_find_matching_sku_partial_match(self):
        """Test partial SKU matching"""
        sku_mapping = {
            'Wine Zari Kaani Set - Top M': 'SIMPLE_101_TOP_M'
        }
        
        result = find_matching_sku('Wine Zari Kaani Set', 'M', 'TOP', sku_mapping)
        self.assertEqual(result, 'SIMPLE_101_TOP_M')
    
    def test_find_matching_sku_no_match(self):
        """Test when no SKU match is found"""
        sku_mapping = {
            'Different Item - Top L': 'SIMPLE_999_TOP_L'
        }
        
        result = find_matching_sku('Non-existent Item', 'M', 'TOP', sku_mapping)
        self.assertIsNone(result)
    
    def test_process_returns_with_existing_items(self):
        """Test processing returns data with items that exist in inventory"""
        # Empty production data for this test
        empty_production = pd.DataFrame({
            'Date': [], 'NAME': [], 'top/bottom': [], 'Size': [], 'QTY': []
        })
        
        adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
            empty_production, self.returns_df, self.mapping_df
        )
        
        # Should have some successful adjustments
        self.assertGreater(len(adjustment_df), 0)
        
        # Check that valid items were processed
        expected_items = [
            'olive paisley print - Bottom S',
            'Wine Embroidered Set with Organza Dupatta - Top S',
            'Wine Embroidered Set with Organza Dupatta - Bottom S',
            'Wine Zari Kaani Set - Top M',
            'Wine Zari Kaani Set - Bottom M'
        ]
        
        # At least some of these should be in the results
        processed_items = adjustment_df['Item Name'].tolist()
        found_items = [item for item in expected_items if item in processed_items]
        self.assertGreater(len(found_items), 0)
    
    def test_process_returns_with_missing_items(self):
        """Test processing returns data with items that don't exist in inventory"""
        # Create mapping with only one item
        limited_mapping = pd.DataFrame({
            'Sku Code': ['SIMPLE_123_BOTTOM_S'],
            'Item Name': ['olive paisley print - Bottom S']
        })
        
        # Empty production data
        empty_production = pd.DataFrame({
            'Date': [], 'NAME': [], 'top/bottom': [], 'Size': [], 'QTY': []
        })
        
        adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
            empty_production, self.returns_df, limited_mapping
        )
        
        # Should have errors for missing items
        self.assertGreater(len(errors), 0)
        
        # Check that errors contain expected missing items
        error_text = ' '.join(errors)
        self.assertIn('Black Paisley Woven Pant', error_text)
        self.assertIn('Wine Embroidered Set with Organza Dupatta', error_text)
    
    def test_process_production_and_returns(self):
        """Test processing both production and returns data"""
        adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
            self.production_df, self.returns_df, self.mapping_df
        )
        
        # Should have both production and returns adjustments
        self.assertGreater(len(adjustment_df), 0)
        
        # All adjustments should be ADD type for GOOD_INVENTORY
        self.assertTrue(all(adjustment_df['Adjustment Type'] == 'ADD'))
        self.assertTrue(all(adjustment_df['Inventory Type'] == 'GOOD_INVENTORY'))
        
        # Should have some errors for missing items
        self.assertGreater(len(errors), 0)
    
    def test_empty_name_handling(self):
        """Test handling of empty item names in returns data"""
        # This tests the actual case where NAME is empty in returns data
        empty_production = pd.DataFrame({
            'Date': [], 'NAME': [], 'top/bottom': [], 'Size': [], 'QTY': []
        })
        
        adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
            empty_production, self.returns_df, self.mapping_df
        )
        
        # Should not process the empty name row
        # Check that no adjustment was created for empty name
        processed_names = adjustment_df['Item Name'].tolist()
        empty_name_adjustments = [name for name in processed_names if ' - Bottom L' in name and name.startswith(' -')]
        self.assertEqual(len(empty_name_adjustments), 0)
    
    def test_returns_notes_filtering(self):
        """Test that only returns with 'PUT IN STOCK AGAIN' are processed"""
        # Create returns data with mixed notes
        mixed_returns = pd.DataFrame({
            'DATE': ['31/1/2026', '31/1/2026', '31/1/2026'],
            'NAME': ['olive paisley print', 'Wine Zari Kaani Set', 'Black Paisley Woven Pant'],
            'bottom/top/dupatta/potli': ['BOTTOM', 'TOP', 'BOTTOM'],
            'SIZE': ['S', 'M', 'XL'],
            'QTY': [1, 1, 1],
            'notes': ['PUT IN STOCK AGAIN', 'DAMAGED', 'PUT IN STOCK AGAIN']
        })
        
        empty_production = pd.DataFrame({
            'Date': [], 'NAME': [], 'top/bottom': [], 'Size': [], 'QTY': []
        })
        
        adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
            empty_production, mixed_returns, self.mapping_df
        )
        
        # Should have ignored returns for non-"PUT IN STOCK AGAIN" items
        self.assertGreater(len(ignored_returns), 0)
        
        # Check that the damaged item was ignored
        ignored_text = ' '.join(ignored_returns)
        self.assertIn('Wine Zari Kaani Set', ignored_text)
        self.assertIn('DAMAGED', ignored_text)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
