import csv
import sys
import os
sys.path.append('../common')
from uniware_utils import sanitize_sku, generate_bundle_variant, parse_product_name

def generate_channel_item_type(shopify_file, output_file):
    channel_items = []
    errors = []
    
    with open(shopify_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                product_name = row['Product Name on Channel']
                channel_product_id = row['Channel Product Id']
                channel_name = row['channelName']
                seller_sku = row.get('Seller SKU on Channel', '') or channel_product_id
                
                if not product_name or not channel_product_id or not channel_name:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                
                components = parse_product_name(product_name)
                if not components:
                    errors.append(f"Row {row_num}: No components found in '{product_name}'")
                    continue
                
                if '-' not in channel_product_id:
                    errors.append(f"Row {row_num}: Invalid channel product id format '{channel_product_id}'")
                    continue
                
                product_code_base = channel_product_id.split('-')[1]
                
                # Create bundle variant for Uniware SKU
                bundle_variant = generate_bundle_variant(components)
                uniware_sku = sanitize_sku(f"{product_code_base}_{bundle_variant}")
                
                channel_item = {
                    'Channel Name*': channel_name,
                    'Channel Product Id*': channel_product_id,
                    'Seller SKU Code*': seller_sku,
                    'Uniware SKU Code': uniware_sku,
                    'Blocked Inventory': '',
                    'Live': '',
                    'Disabled': '',
                    'Selling Price': '',
                    'Max Retail Price': '',
                    'Min Selling Price': '',
                    'Currency Code': '',
                    'Ignore': '',
                    'Shipping Package Type Code': '',
                    'Verified': '',
                    'Product url': '',
                    'Product name': '',
                    'Channel Product image url': ''
                }
                channel_items.append(channel_item)
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing '{row.get('Product Name on Channel', 'N/A')}' - {str(e)}")
                continue
    
    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors:
            print(f"  {error}")
    
    # Write output
    if channel_items:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=channel_items[0].keys())
            writer.writeheader()
            writer.writerows(channel_items)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python uniware_shopify_linker.py <shopify_products_file>")
        sys.exit(1)
    
    shopify_file = sys.argv[1]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "generated_output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "populated_channel_item_type.csv")
    
    generate_channel_item_type(shopify_file, output_file)
    print(f"Generated {output_file}")
