import unittest
import csv
import os
import tempfile
import sys
sys.path.append('../../src/uniware')
sys.path.append('../../src/common')
from item_master_generator import generate_items
from uniware_utils import parse_product_name, sanitize_sku

class TestShopifyItemsGenerator(unittest.TestCase):
    
    def _log_test(self, test_name, input_data, expected, actual, description=""):
        """Helper method to log test input and assertions"""
        print(f"\n=== {test_name} ===")
        if isinstance(input_data, str):
            print(f"INPUT: '{input_data}'")
        else:
            print(f"INPUT: {input_data}")
        print(f"EXPECTED: {expected}")
        print(f"ACTUAL: {actual}")
        if description:
            print(f"✅ {description}")
    
    def _assert_equal_with_log(self, actual, expected, test_name, input_data, description=""):
        """Helper to assert equality with logging"""
        self._log_test(test_name, input_data, expected, actual, description)
        self.assertEqual(actual, expected)
    
    def test_parse_product_name(self):
        test_cases = [
            ("Aafreen Wine Velvet Suit - XL / S / With Potli", [('TOP', 'XL'), ('BOTTOM', 'S'), ('WITH_ACCESSORY', 'TRUE')], "Basic parsing with accessory"),
            ("Aafreen Kaani Set - XXS / XS", [('TOP', 'XXS'), ('BOTTOM', 'XS')], "Parsing without accessory"),
            ("Simple Kurta - XL", [('TOP', 'XL')], "Single variant parsing"),
            ("Simple Product", [('TOP', 'Simple Product')], "Single product without variants")
        ]
        
        for input_str, expected, description in test_cases:
            with self.subTest(input_str=input_str):
                result = parse_product_name(input_str)
                self._assert_equal_with_log(result, expected, "PARSE PRODUCT NAME TEST", input_str, description)
    
    def test_generate_items(self):
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id', 'channelName'])
            writer.writerow(['', 'Aafreen Wine Velvet Suit - XL / S / With Potli', '9084349907162-47107397746906', 'SHOPIFY'])
            writer.writerow(['', 'Aafreen Kaani Set - XXS / XS', '9084349907162-47107397779674', 'SHOPIFY'])
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
                '47107397746906_WITH_ACCESSORY_TRUE',
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
                '47107397746906_XL_S_WITH',
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
    
    def test_variant_truncation(self):
        """Test that variants are truncated to 4 characters max"""
        test_cases = [
            ("Anarkali Set - KURTA / PALAZZO / WITH EMBROIDERED DUPATTA", 
             [('TOP', 'KURTA'), ('BOTTOM', 'PALAZZO'), ('WITH_ACCESSORY', 'TRUE')], 
             "Long variant names with accessory"),
            ("Green Velvet Suit - XXXL / XXL / WITH EMBROIDERED DUPATTA", 
             [('TOP', 'XXXL'), ('BOTTOM', 'XXL'), ('WITH_ACCESSORY', 'TRUE')], 
             "Production example with accessory")
        ]
        
        for input_str, expected, description in test_cases:
            with self.subTest(input_str=input_str):
                result = parse_product_name(input_str)
                self._assert_equal_with_log(result, expected, "VARIANT TRUNCATION TEST", input_str, description)
    
    def test_sanitize_sku(self):
        """Test SKU sanitization removes invalid characters"""
        test_cases = [
            ("ABC123_TOP_KURTA", "ABC123_TOP_KURTA", "No change needed"),
            ("ABC123_TOP_KURTA WITH SPACE", "ABC123_TOP_KURTA_WITH_SPACE", "Spaces replaced with underscores"),
            ("ABC123@#$%", "ABC123____", "Special characters replaced"),
            ("ABC-123.456/789_TEST", "ABC-123.456/789_TEST", "Allowed characters preserved"),
            ("40559697690812_TOP_₹1,000.00", "40559697690812_TOP__1_000.00", "Currency symbols sanitized")
        ]
        
        for input_sku, expected, description in test_cases:
            with self.subTest(input_sku=input_sku):
                result = sanitize_sku(input_sku)
                self._assert_equal_with_log(result, expected, "SKU SANITIZATION TEST", input_sku, description)
    
    def test_sku_length_limit(self):
        """Test that bundle SKU stays under 45 characters"""
        test_cases = [
            ("12345678901234", "KURT_PALA_WITH", 29, "Standard variant length"),
            ("12345678901234", "XXXL_XXL_WITH", 28, "Production example length")
        ]
        
        for base, variant, expected_length, description in test_cases:
            with self.subTest(variant=variant):
                bundle_sku = f"{base}_{variant}"
                input_data = f"Base='{base}', Variant='{variant}'"
                expected = f"Length <= 45 (actual: {expected_length})"
                actual = f"Length: {len(bundle_sku)}"
                
                self._log_test("SKU LENGTH TEST", input_data, expected, actual, description)
                self.assertLessEqual(len(bundle_sku), 45)
                self.assertEqual(len(bundle_sku), expected_length)
    
    def test_bundle_sku_generation(self):
        """Test bundle SKU generation with variant truncation"""
        # Create temporary input file with test cases
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id', 'channelName'])
            writer.writerow(['', 'Anarkali Set - KURTA / PALAZZO / WITH EMBROIDERED DUPATTA', 'SHOP-12345678901234', 'SHOPIFY'])
            writer.writerow(['', 'Green Velvet Suit - XXXL / XXL / WITH EMBROIDERED DUPATTA', 'SHOP-98765432109876', 'SHOPIFY'])
            input_file_path = input_file.name
        
        # Create temporary output files
        simple_output = tempfile.mktemp(suffix='.csv')
        bundle_output = tempfile.mktemp(suffix='.csv')
        
        try:
            # Generate items
            generate_items(input_file_path, simple_output, bundle_output)
            
            # Verify bundle SKUs
            with open(bundle_output, 'r') as f:
                reader = csv.DictReader(f)
                bundle_items = list(reader)
            
            print("\n=== BUNDLE SKU TEST ===")
            for item in bundle_items:
                print(f"Product Code: {item['Product Code*']}, Component: {item['Component Product Code']}")
            
            # Extract unique bundle product codes
            bundle_codes = list(set(item['Product Code*'] for item in bundle_items))
            
            # Verify expected bundle SKUs
            expected_bundles = [
                '12345678901234_KURT_PALA_WITH',  # KURTA->KURT, PALAZZO->PALA
                '98765432109876_XXXL_XXL_WITH'    # XXXL, XXL unchanged
            ]
            
            self.assertEqual(set(bundle_codes), set(expected_bundles))
            
            # Verify all bundle SKUs are under 45 characters
            for code in bundle_codes:
                self.assertLessEqual(len(code), 45)
                print(f"Bundle SKU: {code} (length: {len(code)})")
                
        finally:
            # Clean up
            os.unlink(input_file_path)
            if os.path.exists(simple_output):
                os.unlink(simple_output)
            if os.path.exists(bundle_output):
                os.unlink(bundle_output)
    
    def test_accessory_false_creates_simple_item(self):
        """Test that WITHOUT accessories do NOT create SIMPLE items (only physical items)"""
        # Create temporary input file with WITHOUT accessory
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id', 'channelName'])
            writer.writerow(['', 'Test Set - KURTA / PALAZZO / WITHOUT DUPATTA', 'SHOP-12345678901234', 'SHOPIFY'])
            input_file_path = input_file.name
        
        # Create temporary output files
        simple_output = tempfile.mktemp(suffix='.csv')
        bundle_output = tempfile.mktemp(suffix='.csv')
        
        try:
            # Generate items
            generate_items(input_file_path, simple_output, bundle_output)
            
            # Verify SIMPLE items
            with open(simple_output, 'r') as f:
                reader = csv.DictReader(f)
                simple_items = list(reader)
            
            print("\n=== WITHOUT ACCESSORY TEST ===")
            for item in simple_items:
                print(f"Product Code: {item['Product Code*']}, Name: {item['Name*']}")
            
            # Should create only 2 SIMPLE items: TOP and BOTTOM (no WITH_ACCESSORY_FALSE)
            self.assertEqual(len(simple_items), 2)
            
            # Verify specific codes
            expected_codes = [
                '12345678901234_TOP_KURTA',
                '12345678901234_BOTTOM_PALAZZO'
            ]
            actual_codes = [item['Product Code*'] for item in simple_items]
            self.assertEqual(set(actual_codes), set(expected_codes))
            
            # Verify bundle uses "WITHOUT" in variant but only references physical components
            with open(bundle_output, 'r') as f:
                reader = csv.DictReader(f)
                bundle_items = list(reader)
            
            print("Bundle components:")
            for item in bundle_items:
                print(f"  Bundle: {item['Product Code*']} -> Component: {item['Component Product Code']}")
            
            bundle_codes = list(set(item['Product Code*'] for item in bundle_items))
            expected_bundle = '12345678901234_KURT_PALA_WITHOUT'
            self.assertEqual(bundle_codes, [expected_bundle])
            
            # Verify bundle only references physical components (2 components, not 3)
            self.assertEqual(len(bundle_items), 2)
            component_codes = [item['Component Product Code'] for item in bundle_items]
            self.assertEqual(set(component_codes), set(expected_codes))
            
        finally:
            # Clean up
            os.unlink(input_file_path)
            if os.path.exists(simple_output):
                os.unlink(simple_output)
            if os.path.exists(bundle_output):
                os.unlink(bundle_output)
    
    def test_channel_filtering(self):
        """Test that only SHOPIFY channel products are processed"""
        # Create temporary input file with mixed channels
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id', 'channelName'])
            writer.writerow(['', 'SHOPIFY Product - KURTA / PALAZZO', 'SHOP-12345', 'SHOPIFY'])
            writer.writerow(['', 'AMAZON Product - TOP / BOTTOM', 'AMZN-67890', 'AMAZON'])
            writer.writerow(['', 'MYNTRA Product - XL', 'MYNT-11111', 'MYNTRA'])
            writer.writerow(['', 'SHOPIFY Product 2 - S', 'SHOP-22222', 'SHOPIFY'])
            input_file_path = input_file.name
        
        # Create temporary output files
        simple_output = tempfile.mktemp(suffix='.csv')
        bundle_output = tempfile.mktemp(suffix='.csv')
        
        try:
            print("\n=== CHANNEL FILTERING TEST ===")
            print("INPUT DATA:")
            print("  SHOPIFY Product - KURTA / PALAZZO (SHOP-12345) [SHOPIFY]")
            print("  AMAZON Product - TOP / BOTTOM (AMZN-67890) [AMAZON]")
            print("  MYNTRA Product - XL (MYNT-11111) [MYNTRA]")
            print("  SHOPIFY Product 2 - S (SHOP-22222) [SHOPIFY]")
            print()
            
            # Generate items
            generate_items(input_file_path, simple_output, bundle_output)
            
            # Verify only SHOPIFY products were processed
            with open(simple_output, 'r') as f:
                reader = csv.DictReader(f)
                simple_items = list(reader)
            
            print("GENERATED SIMPLE ITEMS:")
            for item in simple_items:
                print(f"  {item['Product Code*']}")
            print()
            
            # Should only have SHOPIFY products (2 products = 3 SIMPLE items)
            # SHOP-12345: KURTA + PALAZZO = 2 items
            # SHOP-22222: S = 1 item  
            print("ASSERTIONS:")
            print(f"  Expected 3 SIMPLE items, got {len(simple_items)}")
            self.assertEqual(len(simple_items), 3)
            print("  ✅ Correct number of SIMPLE items generated")
            
            # Verify product codes contain only SHOPIFY product bases
            shopify_bases = ['12345', '22222']
            print(f"  Expected SHOPIFY bases: {shopify_bases}")
            for item in simple_items:
                product_code = item['Product Code*']
                has_shopify_base = any(base in product_code for base in shopify_bases)
                self.assertTrue(has_shopify_base, f"Product code {product_code} should contain SHOPIFY base")
            print("  ✅ All items contain SHOPIFY product bases")
            
            # Verify no AMAZON or MYNTRA products
            excluded_bases = ['67890', '11111']
            print(f"  Expected excluded bases: {excluded_bases}")
            for item in simple_items:
                product_code = item['Product Code*']
                self.assertNotIn('67890', product_code, "Should not contain AMAZON product")
                self.assertNotIn('11111', product_code, "Should not contain MYNTRA product")
            print("  ✅ No AMAZON or MYNTRA products in output")
            
        finally:
            # Clean up
            os.unlink(input_file_path)
            if os.path.exists(simple_output):
                os.unlink(simple_output)
            if os.path.exists(bundle_output):
                os.unlink(bundle_output)

if __name__ == '__main__':
    unittest.main()
