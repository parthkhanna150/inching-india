import csv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from uniware_utils import sanitize_sku, generate_bundle_variant, parse_product_name

def generate_channel_item_type(shopify_file, output_file):
    channel_items = []
    errors = []
    skipped_channels = {}
    
    with open(shopify_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                product_name = row['Product Name on Channel']
                channel_product_id = row['Channel Product Id']
                channel_name = row['channelName']
                seller_sku = row.get('Seller SKU on Channel', '') or channel_product_id
                
                # Only process SHOPIFY channel products
                if channel_name.upper() != 'SHOPIFY':
                    skipped_channels[channel_name] = skipped_channels.get(channel_name, 0) + 1
                    continue
                
                if not product_name or not channel_product_id or not channel_name:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                
                components = parse_product_name(product_name)
                if not components:
                    errors.append(f"Row {row_num}: No components found in '{product_name}'")
                    continue
                
                # Check if there are any physical components (skip if only non-physical accessories)
                physical_components = [
                    (comp_type, comp_value) for comp_type, comp_value in components
                    if not (comp_type == 'WITH_ACCESSORY' and comp_value == 'FALSE')
                ]
                
                if not physical_components:
                    errors.append(f"Row {row_num}: No physical components found in '{product_name}' - skipping")
                    continue
                
                if '-' not in channel_product_id:
                    errors.append(f"Row {row_num}: Invalid channel product id format '{channel_product_id}'")
                    continue
                
                product_code_base = channel_product_id.split('-')[1]
                
                # Create bundle variant for Uniware SKU
                bundle_variant = generate_bundle_variant(components)
                uniware_sku = sanitize_sku(f"BDL_{product_code_base}_{bundle_variant}")
                
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
    
    # Print skipped channels summary
    if skipped_channels:
        print(f"Skipped {sum(skipped_channels.values())} products from other channels:")
        for channel, count in sorted(skipped_channels.items()):
            print(f"  {channel}: {count} products")
    
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
