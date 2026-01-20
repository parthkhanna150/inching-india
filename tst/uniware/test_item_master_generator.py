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
    
    def test_parse_product_name(self):
        # Test basic parsing
        result = parse_product_name("Aafreen Wine Velvet Suit - XL / S / With Potli")
        expected = [('TOP', 'XL'), ('BOTTOM', 'S'), ('WITH_ACCESSORY', 'TRUE')]
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
        # Test case 1: Long variant names
        product_name = "Anarkali Set - KURTA / PALAZZO / WITH EMBROIDERED DUPATTA"
        components = parse_product_name(product_name)
        
        print(f"\n=== VARIANT TRUNCATION TEST ===")
        print(f"Input: {product_name}")
        print(f"Parsed components: {components}")
        
        expected_components = [
            ('TOP', 'KURTA'),
            ('BOTTOM', 'PALAZZO'),
            ('WITH_ACCESSORY', 'TRUE')
        ]
        self.assertEqual(components, expected_components)
        
        # Test case 2: Real example from production
        product_name2 = "Green Velvet Suit - XXXL / XXL / WITH EMBROIDERED DUPATTA"
        components2 = parse_product_name(product_name2)
        
        print(f"Input: {product_name2}")
        print(f"Parsed components: {components2}")
        
        expected_components2 = [
            ('TOP', 'XXXL'),
            ('BOTTOM', 'XXL'),
            ('WITH_ACCESSORY', 'TRUE')
        ]
        self.assertEqual(components2, expected_components2)
    
    def test_sanitize_sku(self):
        """Test SKU sanitization removes invalid characters"""
        test_cases = [
            ("ABC123_TOP_KURTA", "ABC123_TOP_KURTA"),
            ("ABC123_TOP_KURTA WITH SPACE", "ABC123_TOP_KURTA_WITH_SPACE"),
            ("ABC123@#$%", "ABC123____"),
            ("ABC-123.456/789_TEST", "ABC-123.456/789_TEST"),
            ("40559697690812_TOP_₹1,000.00", "40559697690812_TOP__1_000.00")  # Currency symbol and comma
        ]
        
        print(f"\n=== SKU SANITIZATION TEST ===")
        for input_sku, expected in test_cases:
            with self.subTest(input_sku=input_sku):
                result = sanitize_sku(input_sku)
                print(f"Input: {input_sku} -> Output: {result}")
                self.assertEqual(result, expected)
    
    def test_sku_length_limit(self):
        """Test that bundle SKU stays under 45 characters"""
        product_code_base = "12345678901234"
        bundle_variant = "KURT_PALA_WITH"
        bundle_sku = f"{product_code_base}_{bundle_variant}"
        
        print(f"\n=== SKU LENGTH TEST ===")
        print(f"Bundle SKU: {bundle_sku} (length: {len(bundle_sku)})")
        
        self.assertLessEqual(len(bundle_sku), 45)
        self.assertEqual(bundle_sku, "12345678901234_KURT_PALA_WITH")
        self.assertEqual(len(bundle_sku), 29)
        
        # Test production example
        bundle_variant2 = "XXXL_XXL_WITH"
        bundle_sku2 = f"{product_code_base}_{bundle_variant2}"
        
        print(f"Bundle SKU: {bundle_sku2} (length: {len(bundle_sku2)})")
        
        self.assertLessEqual(len(bundle_sku2), 45)
        self.assertEqual(bundle_sku2, "12345678901234_XXXL_XXL_WITH")
        self.assertEqual(len(bundle_sku2), 28)
    
    def test_bundle_sku_generation(self):
        """Test bundle SKU generation with variant truncation"""
        # Create temporary input file with test cases
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id'])
            writer.writerow(['', 'Anarkali Set - KURTA / PALAZZO / WITH EMBROIDERED DUPATTA', 'SHOP-12345678901234'])
            writer.writerow(['', 'Green Velvet Suit - XXXL / XXL / WITH EMBROIDERED DUPATTA', 'SHOP-98765432109876'])
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
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id'])
            writer.writerow(['', 'Test Set - KURTA / PALAZZO / WITHOUT DUPATTA', 'SHOP-12345678901234'])
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

if __name__ == '__main__':
    unittest.main()
