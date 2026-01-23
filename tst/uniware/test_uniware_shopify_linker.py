import unittest
import csv
import os
import tempfile
import sys
sys.path.append('../../src/uniware')
sys.path.append('../../src/common')
from uniware_shopify_linker import parse_product_name, generate_channel_item_type

class TestChannelItemTypeGenerator(unittest.TestCase):
    
    def test_parse_product_name(self):
        # Test with potli
        result = parse_product_name("Aafreen Wine Velvet Suit - XL / S / With Potli")
        expected = [('TOP', 'XL'), ('BOTTOM', 'S'), ('WITH_ACCESSORY', 'TRUE')]
        self.assertEqual(result, expected)
        
        # Test without potli
        result = parse_product_name("Aafreen Wine Velvet Suit - XL / S / Without Potli")
        expected = [('TOP', 'XL'), ('BOTTOM', 'S'), ('WITH_ACCESSORY', 'FALSE')]
        self.assertEqual(result, expected)
        
        # Test with dupatta
        result = parse_product_name("Elegant Kurta Set - L / Pant M / With Dupatta")
        expected = [('TOP', 'L'), ('BOTTOM', 'Pant M'), ('WITH_ACCESSORY', 'TRUE')]
        self.assertEqual(result, expected)
        
        # Test without accessory variant
        result = parse_product_name("Aafreen Kaani Set - XXS / XS")
        expected = [('TOP', 'XXS'), ('BOTTOM', 'XS')]
        self.assertEqual(result, expected)
    
    def test_generate_channel_item_type(self):
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Channel Product Image', 'Product Name on Channel', 'Channel Product Id', 'channelName', 'Seller SKU on Channel'])
            writer.writerow(['', 'Aafreen Wine Velvet Suit - XL / S / With Potli', '9084349907162-47107397746906', 'SHOPIFY', 'CUSTOM_SKU_1'])
            writer.writerow(['', 'Elegant Kurta Set - L / Pant M / With Dupatta', '9084349907162-47107397746907', 'SHOPIFY', 'CUSTOM_SKU_2'])
            writer.writerow(['', 'Aafreen Wine Velvet Suit - M / L / Without Potli', '9084349907162-47107397746908', 'SHOPIFY', 'CUSTOM_SKU_3'])
            writer.writerow(['', 'Aafreen Kaani Set - XXS / XS', '9084349907162-47107397779674', 'SHOPIFY', ''])
            input_file_path = input_file.name
        
        # Create temporary template file
        output_file = tempfile.mktemp(suffix='.csv')
        
        try:
            # Generate channel item type
            generate_channel_item_type(input_file_path, output_file)
            
            # Verify output
            with open(output_file, 'r') as f:
                reader = csv.DictReader(f)
                items = list(reader)
            
            print("\n=== CHANNEL ITEM TYPE ENTRIES ===")
            for item in items:
                print(f"Channel: {item['Channel Name*']}, Product ID: {item['Channel Product Id*']}, Uniware SKU: {item['Uniware SKU Code']}")
            
            self.assertEqual(len(items), 4)
            
            # Check first item (with potli)
            first_item = items[0]
            self.assertEqual(first_item['Uniware SKU Code'], 'BDL_47107397746906_XL_S_WITH')
            
            # Check second item (with dupatta)
            second_item = items[1]
            self.assertEqual(second_item['Uniware SKU Code'], 'BDL_47107397746907_L_PANT_WITH')
            
            # Check third item (without potli)
            third_item = items[2]
            self.assertEqual(third_item['Uniware SKU Code'], 'BDL_47107397746908_M_L_WITHOUT')
            
            # Check fourth item (no accessory variant)
            fourth_item = items[3]
            self.assertEqual(fourth_item['Uniware SKU Code'], 'BDL_47107397779674_XXS_XS')
            
        finally:
            # Clean up
            os.unlink(input_file_path)
            if os.path.exists(output_file):
                os.unlink(output_file)

if __name__ == '__main__':
    unittest.main()
