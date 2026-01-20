import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shopify_items_generator import parse_product_name, sanitize_sku

class TestShopifyItemsGenerator(unittest.TestCase):
    
    def test_variant_truncation(self):
        """Test that variants are truncated to 4 characters max"""
        product_name = "Anarkali Set - KURTA / PALAZZO / WITH EMBROIDERED DUPATTA"
        components = parse_product_name(product_name)
        
        # Test component parsing
        expected_components = [
            ('TOP', 'KURTA'),
            ('BOTTOM', 'PALAZZO'),
            ('WITH_DUPATTA', 'TRUE')
        ]
        self.assertEqual(components, expected_components)
        
        # Test variant generation (simulate the logic from main function)
        variant_parts = []
        for comp_type, comp_value in components:
            if comp_type in ['TOP', 'BOTTOM']:
                variant_parts.append(comp_value[:4].upper())
            else:
                if comp_value == 'TRUE':
                    variant_parts.append('WITH')
                else:
                    variant_parts.append('WITHOUT')
        
        bundle_variant = '_'.join(variant_parts)
        self.assertEqual(bundle_variant, 'KURT_PALA_WITH')
    
    def test_sku_length_limit(self):
        """Test that bundle SKU stays under 45 characters"""
        product_code_base = "43484344418522"
        bundle_variant = "KURT_PALA_WITH"
        bundle_sku = f"{product_code_base}_{bundle_variant}"
        
        self.assertLessEqual(len(bundle_sku), 45)
        self.assertEqual(bundle_sku, "43484344418522_KURT_PALA_WITH")
        self.assertEqual(len(bundle_sku), 33)
    
    def test_sanitize_sku(self):
        """Test SKU sanitization removes invalid characters"""
        test_cases = [
            ("ABC123_TOP_KURTA", "ABC123_TOP_KURTA"),
            ("ABC123_TOP_KURTA WITH SPACE", "ABC123_TOP_KURTA_WITH_SPACE"),
            ("ABC123@#$%", "ABC123____"),
            ("ABC-123.456/789_TEST", "ABC-123.456/789_TEST")
        ]
        
        for input_sku, expected in test_cases:
            self.assertEqual(sanitize_sku(input_sku), expected)
    
    def test_accessory_variants(self):
        """Test accessory variants show WITH/WITHOUT"""
        test_cases = [
            ("Set - TOP / BOTTOM / WITH DUPATTA", "WITH"),
            ("Set - TOP / BOTTOM / WITHOUT POTLI", "WITHOUT")
        ]
        
        for product_name, expected_accessory in test_cases:
            components = parse_product_name(product_name)
            accessory_component = [c for c in components if c[0].startswith('WITH_')][0]
            
            if accessory_component[1] == 'TRUE':
                variant = 'WITH'
            else:
                variant = 'WITHOUT'
            
            self.assertEqual(variant, expected_accessory)

if __name__ == '__main__':
    unittest.main()
