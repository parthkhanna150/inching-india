import unittest
import csv
import os
import tempfile
from shopify_items_generator import parse_product_name, generate_items

class TestShopifyItemsGenerator(unittest.TestCase):
    
    def test_parse_product_name(self):
        # Test basic parsing
        result = parse_product_name("Aafreen Wine Velvet Suit - XL / S / With Potli")
        expected = [('TOP', 'XL'), ('BOTTOM', 'S'), ('WITH_POTLI', 'TRUE')]
        self.assertEqual(result, expected)
        
        # Test without potli
        result = parse_product_name("Aafreen Kaani Set - XXS / XS")
        expected = [('TOP', 'XXS'), ('BOTTOM', 'XS')]
        self.assertEqual(result, expected)
        
        # Test only top size
        result = parse_product_name("Simple Kurta - XL")
        expected = [('TOP', 'XL')]
        self.assertEqual(result, expected)
        
        # Test no hyphen
        result = parse_product_name("Simple Product")
        self.assertEqual(result, [])
    
    def test_generate_items(self):
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id'])
            writer.writerow(['', 'Aafreen Wine Velvet Suit - XL / S / With Potli', '9084349907162-47107397746906'])
            writer.writerow(['', 'Aafreen Kaani Set - XXS / XS', '9084349907162-47107397779674'])
            input_file_path = input_file.name
        
        # Create temporary output files
        simple_output = tempfile.mktemp(suffix='.csv')
        bundle_output = tempfile.mktemp(suffix='.csv')
        
        try:
            # Generate items
            generate_items(input_file_path, simple_output, bundle_output)
            
            # Verify simple items
            with open(simple_output, 'r') as f:
                reader = csv.DictReader(f)
                simple_items = list(reader)
            
            print("\n=== SIMPLE ITEMS ===")
            for item in simple_items:
                print(f"Product Code: {item['Product Code*']}, Name: {item['Name*']}")
            
            self.assertEqual(len(simple_items), 5)  # 3 + 2 components
            
            # Assert specific product codes
            expected_simple_codes = [
                '47107397746906_TOP_XL',
                '47107397746906_BOTTOM_S', 
                '47107397746906_WITH_POTLI_TRUE',
                '47107397779674_TOP_XXS',
                '47107397779674_BOTTOM_XS'
            ]
            actual_codes = [item['Product Code*'] for item in simple_items]
            self.assertEqual(set(actual_codes), set(expected_simple_codes))
            
            # Verify bundle items
            with open(bundle_output, 'r') as f:
                reader = csv.DictReader(f)
                bundle_items = list(reader)
            
            print("\n=== BUNDLE ITEMS ===")
            for item in bundle_items:
                print(f"Product Code: {item['Product Code*']}, Component: {item['Component Product Code']}")
            
            self.assertEqual(len(bundle_items), 5)  # 3 + 2 components
            
            # Assert bundle product codes
            expected_bundle_codes = [
                '47107397746906_XL_S_WITH_POTLI',
                '47107397779674_XXS_XS'
            ]
            actual_bundle_codes = list(set(item['Product Code*'] for item in bundle_items))
            self.assertEqual(set(actual_bundle_codes), set(expected_bundle_codes))
            
        finally:
            # Clean up
            os.unlink(input_file_path)
            if os.path.exists(simple_output):
                os.unlink(simple_output)
            if os.path.exists(bundle_output):
                os.unlink(bundle_output)

if __name__ == '__main__':
    unittest.main()
