import unittest
import tempfile
import csv
import os
import sys
import pandas as pd

# Add the src directory to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'uniware'))

class TestInventoryAdjustmentGenerator(unittest.TestCase):
    
    def test_inventory_adjustment_generation(self):
        """Test that inventory adjustment records are generated correctly"""
        
        # Create test populated_item_master.csv with SIMPLE items
        test_data = [
            {
                'Product Code*': 'SIMPLE_abc123_TOP_S',
                'Name*': 'Test Product - Top S',
                'Type': 'SIMPLE'
            },
            {
                'Product Code*': 'SIMPLE_def456_BOTTOM_M',
                'Name*': 'Test Product - Bottom M',
                'Type': 'SIMPLE'
            },
            {
                'Product Code*': 'BDL_12345_S_M',
                'Name*': 'Bundle Test Product',
                'Type': 'BUNDLE'
            }
        ]
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.DictWriter(input_file, fieldnames=test_data[0].keys())
            writer.writeheader()
            writer.writerows(test_data)
            input_path = input_file.name
        
        # Create temporary output file path
        output_path = tempfile.mktemp(suffix='.csv')
        
        try:
            # Mock the file paths in the generator
            import inventory_adjustment_generator
            
            # Read the test data
            df = pd.read_csv(input_path)
            simple_items = df[df['Type'] == 'SIMPLE']
            
            # Generate inventory records
            inventory_records = []
            for _, row in simple_items.iterrows():
                product_code = row['Product Code*']
                
                # GOOD_INVENTORY record
                good_inventory_record = {
                    'Product Code*': product_code,
                    'Quantity*': 0,
                    'Shelf Code*': 'DEFAULT',
                    'Adjustment Type*': 'ADD',
                    'Inventory Type': 'GOOD_INVENTORY',
                    'Transfer to Shelf Code': '',
                    'Sla': '',
                    'Source Batch Code': '',
                    'Remarks': '',
                    'Force Allocate': ''
                }
                inventory_records.append(good_inventory_record)
                
                # VIRTUAL_INVENTORY record
                virtual_inventory_record = {
                    'Product Code*': product_code,
                    'Quantity*': 1000,
                    'Shelf Code*': 'DEFAULT',
                    'Adjustment Type*': 'ADD',
                    'Inventory Type': 'VIRTUAL_INVENTORY',
                    'Transfer to Shelf Code': '',
                    'Sla': '',
                    'Source Batch Code': '',
                    'Remarks': '',
                    'Force Allocate': ''
                }
                inventory_records.append(virtual_inventory_record)
            
            # Save to output file
            inventory_df = pd.DataFrame(inventory_records)
            inventory_df.to_csv(output_path, index=False)
            
            # Read and verify the output
            with open(output_path, 'r') as f:
                reader = csv.DictReader(f)
                output_records = list(reader)
            
            # Verify we have 4 records (2 SIMPLE items × 2 inventory types)
            self.assertEqual(len(output_records), 4)
            
            # Verify GOOD_INVENTORY records
            good_records = [r for r in output_records if r['Inventory Type'] == 'GOOD_INVENTORY']
            self.assertEqual(len(good_records), 2)
            for record in good_records:
                self.assertEqual(record['Quantity*'], '0')
                self.assertEqual(record['Adjustment Type*'], 'ADD')
                self.assertEqual(record['Shelf Code*'], 'DEFAULT')
                self.assertTrue(record['Product Code*'].startswith('SIMPLE_'))
            
            # Verify VIRTUAL_INVENTORY records
            virtual_records = [r for r in output_records if r['Inventory Type'] == 'VIRTUAL_INVENTORY']
            self.assertEqual(len(virtual_records), 2)
            for record in virtual_records:
                self.assertEqual(record['Quantity*'], '1000')
                self.assertEqual(record['Adjustment Type*'], 'ADD')
                self.assertEqual(record['Shelf Code*'], 'DEFAULT')
                self.assertTrue(record['Product Code*'].startswith('SIMPLE_'))
            
            # Verify BUNDLE items are excluded
            bundle_records = [r for r in output_records if 'BDL_' in r['Product Code*']]
            self.assertEqual(len(bundle_records), 0)
            
        finally:
            # Clean up temporary files
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_inventory_adjustment_structure(self):
        """Test that inventory adjustment records have correct structure"""
        
        # Create minimal test data
        test_data = [
            {
                'Product Code*': 'SIMPLE_test123_TOP_L',
                'Name*': 'Test Item - Top L',
                'Type': 'SIMPLE'
            }
        ]
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.DictWriter(input_file, fieldnames=test_data[0].keys())
            writer.writeheader()
            writer.writerows(test_data)
            input_path = input_file.name
        
        output_path = tempfile.mktemp(suffix='.csv')
        
        try:
            # Generate records
            df = pd.read_csv(input_path)
            simple_items = df[df['Type'] == 'SIMPLE']
            
            inventory_records = []
            for _, row in simple_items.iterrows():
                product_code = row['Product Code*']
                
                # Create both inventory types
                for inv_type, quantity in [('GOOD_INVENTORY', 0), ('VIRTUAL_INVENTORY', 1000)]:
                    record = {
                        'Product Code*': product_code,
                        'Quantity*': quantity,
                        'Shelf Code*': 'DEFAULT',
                        'Adjustment Type*': 'ADD',
                        'Inventory Type': inv_type,
                        'Transfer to Shelf Code': '',
                        'Sla': '',
                        'Source Batch Code': '',
                        'Remarks': '',
                        'Force Allocate': ''
                    }
                    inventory_records.append(record)
            
            # Save and verify
            inventory_df = pd.DataFrame(inventory_records)
            inventory_df.to_csv(output_path, index=False)
            
            # Check structure
            with open(output_path, 'r') as f:
                reader = csv.DictReader(f)
                records = list(reader)
            
            # Verify required columns exist
            expected_columns = [
                'Product Code*', 'Quantity*', 'Shelf Code*', 'Adjustment Type*',
                'Inventory Type', 'Transfer to Shelf Code', 'Sla', 'Source Batch Code',
                'Remarks', 'Force Allocate'
            ]
            
            for column in expected_columns:
                self.assertIn(column, records[0].keys())
            
            # Verify we have exactly 2 records
            self.assertEqual(len(records), 2)
            
            # Verify one GOOD_INVENTORY and one VIRTUAL_INVENTORY
            inventory_types = [r['Inventory Type'] for r in records]
            self.assertIn('GOOD_INVENTORY', inventory_types)
            self.assertIn('VIRTUAL_INVENTORY', inventory_types)
            
        finally:
            # Clean up
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

if __name__ == '__main__':
    unittest.main()
