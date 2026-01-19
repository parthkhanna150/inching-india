import csv
import re
import sys
import os

def parse_product_name(product_name):
    """Extract components from product name after hyphen"""
    if ' - ' not in product_name:
        return []
    
    parts = product_name.split(' - ', 1)[1].split(' / ')
    components = []
    
    for part in parts:
        part = part.strip()
        if part.upper() in ['WITH POTLI', 'WITHOUT POTLI']:
            potli_value = 'TRUE' if 'WITH' in part.upper() else 'FALSE'
            components.append(('WITH_POTLI', potli_value))
        else:
            # First size is always TOP, second is BOTTOM (if exists)
            if not any(comp[0] == 'TOP' for comp in components):
                components.append(('TOP', part))
            else:
                components.append(('BOTTOM', part))
    
    return components

def generate_items(input_file, simple_output, bundle_output):
    simple_items = []
    bundle_items = []
    errors = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                product_name = row['Product Name on Channel']
                channel_product_id = row['Channel Product Id']
                
                if not product_name or not channel_product_id:
                    errors.append(f"Row {row_num}: Missing product name or channel product id")
                    continue
                    
                # Extract base product name and components
                base_name = product_name.split(' - ')[0] if ' - ' in product_name else product_name
                components = parse_product_name(product_name)
                
                if not components:
                    errors.append(f"Row {row_num}: No components found in '{product_name}'")
                    continue
                    
                # Get product code base from channel product id
                if '-' not in channel_product_id:
                    errors.append(f"Row {row_num}: Invalid channel product id format '{channel_product_id}'")
                    continue
                    
                product_code_base = channel_product_id.split('-')[1]
                
                # Create variant string for bundle
                variant_parts = []
                for comp_type, comp_value in components:
                    if comp_type in ['TOP', 'BOTTOM']:
                        variant_parts.append(comp_value)
                    else:  # WITH_POTLI
                        variant_parts.append('WITH_POTLI' if comp_value == 'TRUE' else 'WITHOUT_POTLI')
                
                bundle_variant = '_'.join(variant_parts)
                bundle_product_code = f"{product_code_base}_{bundle_variant}"
                
                # Create SIMPLE items
                for comp_type, comp_value in components:
                    simple_product_code = f"{product_code_base}_{comp_type.replace(' ', '_')}_{comp_value}"
                    simple_name = f"{base_name} - {comp_type.title()} {comp_value}"
                    simple_description = f"{base_name.upper().replace(' ', '_')}_{comp_type}_{comp_value}"
                    
                    simple_item = {
                        'Category Code*': 'Clothing',
                        'Product Code*': simple_product_code,
                        'Name*': simple_name,
                        'Description': simple_description,
                        'Scan Identifier': simple_product_code,
                        'Length (mm)': '1',
                        'Width (mm)': '1',
                        'height (mm)': '1',
                        'Weight (gms)': '1000.0',
                        'ean': '',
                        'upc': '',
                        'isbn': '',
                        'color': '',
                        'brand': '',
                        'size': comp_value if comp_type in ['TOP', 'BOTTOM'] else '',
                        'Requires Customization': 'False',
                        'Min Order Size': '1',
                        'Tax Type Code': '',
                        'GST Tax Type Code': '',
                        'HSN Code': '',
                        'Tags': '',
                        'TAT': '',
                        'Image Url': '',
                        'Product Page URL': '',
                        'Item Detail Fields': '',
                        'Cost Price': '800.0',
                        'MRP': '1000.0',
                        'Base Price': '1000.0',
                        'Enabled': 'True',
                        'Resync Inventory': 'False',
                        'Type': 'SIMPLE',
                        'Scan Type': '',
                        'Component Product Code': '',
                        'Component Quantity': '',
                        'Component Price': '',
                        'Batch Group Code': '',
                        'Dispatch Expiry Tolerance': '',
                        'Shelf Life': '',
                        'Tax Calculation Type': 'PRICE_OF_COMPONENT_SKU',
                        'Expirable': 'False',
                        'Determine Expiry From': 'From Category',
                        'grn Expiry Tolerance': '',
                        'Return Expiry Tolerance': '',
                        'Expiry Date as dd/MM/yyyy': '',
                        'Sku Type': 'GOODS',
                        'Fragile': 'False',
                        'Dangerous Good': 'False'
                    }
                    simple_items.append(simple_item)
                
                # Create BUNDLE item entries (one per component)
                bundle_name = f"Bundle {product_name}"
                bundle_description = "BUNDLE"
                
                for comp_type, comp_value in components:
                    component_product_code = f"{product_code_base}_{comp_type.replace(' ', '_')}_{comp_value}"
                    
                    bundle_item = {
                        'Category Code*': 'Clothing',
                        'Product Code*': bundle_product_code,
                        'Name*': bundle_name,
                        'Description': bundle_description,
                        'Scan Identifier': bundle_product_code,
                        'Length (mm)': '1',
                        'Width (mm)': '1',
                        'height (mm)': '1',
                        'Weight (gms)': '1000.0',
                        'ean': '',
                        'upc': '',
                        'isbn': '',
                        'color': '',
                        'brand': '',
                        'size': '',
                        'Requires Customization': 'False',
                        'Min Order Size': '1',
                        'Tax Type Code': '',
                        'GST Tax Type Code': '',
                        'HSN Code': '',
                        'Tags': '',
                        'TAT': '',
                        'Image Url': '',
                        'Product Page URL': '',
                        'Item Detail Fields': '',
                        'Cost Price': '',
                        'MRP': '',
                        'Base Price': '',
                        'Enabled': 'True',
                        'Resync Inventory': 'False',
                        'Type': 'BUNDLE',
                        'Scan Type': '',
                        'Component Product Code': component_product_code,
                        'Component Quantity': '1',
                        'Component Price': '1000.0',
                        'Batch Group Code': '',
                        'Dispatch Expiry Tolerance': '',
                        'Shelf Life': '',
                        'Tax Calculation Type': 'PRICE_OF_BUNDLE_SKU',
                        'Expirable': 'False',
                        'Determine Expiry From': 'From Category',
                        'grn Expiry Tolerance': '',
                        'Return Expiry Tolerance': '',
                        'Expiry Date as dd/MM/yyyy': '',
                        'Sku Type': 'GOODS',
                        'Fragile': 'False',
                        'Dangerous Good': 'False'
                    }
                    bundle_items.append(bundle_item)
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing '{row.get('Product Name on Channel', 'N/A')}' - {str(e)}")
                continue
    
    # Print errors if any
    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors:
            print(f"  {error}")
    
    # Write SIMPLE items
    if simple_items:
        with open(simple_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=simple_items[0].keys())
            writer.writeheader()
            writer.writerows(simple_items)
    
    # Write BUNDLE items
    if bundle_items:
        with open(bundle_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=bundle_items[0].keys())
            writer.writeheader()
            writer.writerows(bundle_items)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python shopify_items_generator.py <shopify_products_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "generated_output")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    simple_output = os.path.join(output_dir, "generated_simple_items.csv")
    bundle_output = os.path.join(output_dir, "generated_bundle_items.csv")
    
    generate_items(input_file, simple_output, bundle_output)
    print(f"Generated {simple_output} and {bundle_output}")
