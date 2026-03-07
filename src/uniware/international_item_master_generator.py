import csv
import sys
import os
import re

# Add src to path for imports
sys.path.append(os.path.join(os.getcwd(), 'src', 'common'))
from uniware_utils import parse_product_name, sanitize_sku, generate_bundle_variant

BUNDLE_HEADERS = [
    'Category Code*', 'Product Code*', 'Name*', 'Description', 'Scan Identifier',
    'Length (mm)', 'Width (mm)', 'height (mm)', 'Weight (gms)',
    'ean', 'upc', 'isbn', 'color', 'brand', 'size',
    'Requires Customization', 'Min Order Size',
    'Tax Type Code', 'GST Tax Type Code', 'HSN Code', 'Tags', 'TAT',
    'Image Url', 'Product Page URL', 'Item Detail Fields',
    'Cost Price', 'MRP', 'Base Price', 'Enabled', 'Resync Inventory',
    'Type', 'Scan Type',
    'Component Product Code', 'Component Quantity', 'Component Price',
    'Batch Group Code', 'Dispatch Expiry Tolerance', 'Shelf Life',
    'Tax Calculation Type', 'Expirable', 'Determine Expiry From',
    'grn Expiry Tolerance', 'Return Expiry Tolerance',
    'Expiry Date as dd/MM/yyyy', 'Sku Type', 'Fragile', 'Dangerous Good'
]

def diagnose_missing_component(target_name, base_name, name_to_sku):
    """Figure out why a component wasn't found in the item master."""
    base_lower = base_name.strip().lower()
    # Find all SIMPLE SKUs that share this base name
    matching = [n for n in name_to_sku if n.startswith(base_lower + ' - ')]

    if not matching:
        # No SKUs with this base name at all
        return f"No SIMPLE SKUs found in item master for '{base_name}'"

    # SKUs exist for this product but not this specific component
    available_suffixes = sorted(set(n.split(' - ', 1)[1] for n in matching))
    target_suffix = target_name.split(' - ', 1)[1] if ' - ' in target_name else target_name
    return f"Size/variant '{target_suffix}' not found. Available: {', '.join(available_suffixes)}"

def generate_international_bundles(item_master_path, international_listings_path, output_dir):
    print(f"Loading Item Master from {item_master_path}...")

    name_to_sku = {}

    try:
        with open(item_master_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['Type'] != 'SIMPLE':
                    continue
                if row['Enabled'].lower() != 'true':
                    continue

                name = row['Name'].strip().lower()
                sku = row['Product Code'].strip()
                name_to_sku[name] = sku
    except Exception as e:
        print(f"Error loading Item Master: {e}")
        return

    print(f"Unique SIMPLE item names indexed: {len(name_to_sku)}")

    print(f"Loading International Listings from {international_listings_path}...")
    bundle_rows = []
    channel_item_rows = []
    missing_components = []
    
    try:
        with open(international_listings_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            listings = list(reader)
            
            for row in listings:
                listing_name = row['Product Name on Channel'].strip()
                channel_product_id = row['Channel Product Id'].strip()
                channel_name = row['channelName'].strip()
                seller_sku = row.get('Seller SKU on Channel', '').strip() or channel_product_id
                
                if not listing_name or not channel_product_id or '-' not in channel_product_id:
                    continue
                    
                product_code_base = channel_product_id.split('-')[1]
                components = parse_product_name(listing_name)
                
                # Create bundle SKU using project convention
                bundle_variant = generate_bundle_variant(components)
                bundle_sku = sanitize_sku(f"BDL_{product_code_base}_{bundle_variant}")
                
                base_name = listing_name.split(' - ')[0]
                
                found_all = True
                component_skus = []
                
                for comp_type, comp_value in components:
                    if comp_type == 'WITH_ACCESSORY' and comp_value == 'FALSE':
                        continue

                    target_name = f"{base_name} - {comp_type.title()} {comp_value}".lower()
                    comp_sku = name_to_sku.get(target_name)

                    if not comp_sku:
                        comp_sku = name_to_sku.get(listing_name.lower())

                    if not comp_sku:
                        target_name_fallback = f"{base_name} - {comp_value}".lower()
                        comp_sku = name_to_sku.get(target_name_fallback)

                    if not comp_sku:
                        target_name_listing_case = f"{base_name} - {comp_type} {comp_value}".lower()
                        comp_sku = name_to_sku.get(target_name_listing_case)

                    if comp_sku:
                        component_skus.append(comp_sku)
                    elif comp_type == 'BOTTOM' and component_skus:
                        # Product is likely a single garment listed with dual-size on channel;
                        # TOP was found but no BOTTOM exists — skip BOTTOM gracefully.
                        reason = diagnose_missing_component(target_name, base_name, name_to_sku)
                        missing_components.append({
                            'Listing': listing_name,
                            'Base': base_name,
                            'Required Component': target_name,
                            'SKU': channel_product_id,
                            'Note': 'BOTTOM not found; mapped as single-component bundle',
                            'Reason': reason
                        })
                    else:
                        found_all = False
                        reason = diagnose_missing_component(target_name, base_name, name_to_sku)
                        missing_components.append({
                            'Listing': listing_name,
                            'Base': base_name,
                            'Required Component': target_name,
                            'SKU': channel_product_id,
                            'Note': '',
                            'Reason': reason
                        })
                        break
                
                if found_all and component_skus:
                    # Item Master Rows
                    for comp_sku in component_skus:
                        bundle_row = {h: '' for h in BUNDLE_HEADERS}
                        bundle_row.update({
                            'Category Code*': 'Clothing',
                            'Product Code*': bundle_sku,
                            'Name*': f"Bundle {listing_name}",
                            'Description': 'BUNDLE',
                            'Scan Identifier': bundle_sku,
                            'Length (mm)': '1',
                            'Width (mm)': '1',
                            'height (mm)': '1',
                            'Weight (gms)': '1000.0',
                            'Requires Customization': 'False',
                            'Enabled': 'True',
                            'Type': 'BUNDLE',
                            'Scan Type': 'SIMPLE',
                            'Component Product Code': comp_sku,
                            'Component Quantity': '1',
                            'Component Price': '1000.0',
                            'Tax Calculation Type': 'PRICE_OF_BUNDLE_SKU',
                            'Expirable': 'False',
                            'Determine Expiry From': 'From Category',
                            'Sku Type': 'GOODS',
                            'Fragile': 'False',
                            'Dangerous Good': 'False'
                        })
                        bundle_rows.append(bundle_row)
                    
                    # Channel Item Type Row (Linker)
                    channel_item_rows.append({
                        'Channel Name*': channel_name,
                        'Channel Product Id*': channel_product_id,
                        'Seller SKU Code*': seller_sku,
                        'Uniware SKU Code': bundle_sku,
                        'Live': 'true'
                    })
    except Exception as e:
        print(f"Error processing listings: {e}")
        return

    print(f"Processed {len(listings)} listings.")
    print(f"Successfully mapped: {len(channel_item_rows)}")
    print(f"Failed to map: {len(set(m['SKU'] for m in missing_components))}")

    if missing_components:
        missing_path = os.path.join(output_dir, "missing_components.csv")
        with open(missing_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=missing_components[0].keys())
            writer.writeheader()
            writer.writerows(missing_components)
        print(f"Missing components report saved to {missing_path}")

    if bundle_rows:
        output_path = os.path.join(output_dir, "international_bundle_item_master.csv")
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=BUNDLE_HEADERS)
            writer.writeheader()
            writer.writerows(bundle_rows)
        print(f"Bundle Item Master saved to {output_path}")

        mapping_path = os.path.join(output_dir, "international_bundle_mapping.csv")
        mapping_rows = []
        for b in bundle_rows:
            mapping_rows.append({
                'Bundle SKU': b['Product Code*'],
                'Component SKU': b['Component Product Code'],
                'Quantity': b['Component Quantity']
            })
        
        with open(mapping_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Bundle SKU', 'Component SKU', 'Quantity'])
            writer.writeheader()
            writer.writerows(mapping_rows)
        print(f"Bundle Mapping saved to {mapping_path}")

    if channel_item_rows:
        linker_path = os.path.join(output_dir, "international_channel_item_type.csv")
        headers = ['Channel Name*', 'Channel Product Id*', 'Seller SKU Code*', 'Uniware SKU Code', 'Live']
        with open(linker_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(channel_item_rows)
        print(f"Channel Item Type (Linker) saved to {linker_path}")

if __name__ == "__main__":
    item_master = "../../Downloads/Item Master_18022026212711.csv"
    intl_listings = "../../Downloads/DATATABLE CHANNEL ITEM TYPE_18022026202225.csv"
    output_dir = "generated_output"
    os.makedirs(output_dir, exist_ok=True)
    
    generate_international_bundles(item_master, intl_listings, output_dir)
