import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Size and accessory constants from cut-packet-generator
ACCESSORY_KEYWORDS = ["potli","bag","pouch","dupatta","scarf","shawl","stole","belt","cap","mask"]
ALPHA_ORDER = ["XXXS","XXS","XS","S","M","L","XL","XXL","XXXL","FREE SIZE"]
SIZE_TOKEN = r"(XXXL|XXL|XL|XXS|XS|S|M|L|XXXS|FREE SIZE|[2-5]\d)"

def extract_base_product(title: str) -> str:
    """Extract base product name from full title"""
    if not isinstance(title, str):
        return str(title)
    
    # Remove size and variant information after dash
    t = title.strip()
    if " - " in t:
        parts = t.split(" - ")
        # Keep the main product name (first part)
        return parts[0].strip()
    return t

def parse_sku_components(sku: str) -> Dict[str, str]:
    """Parse SKU to extract component type and size"""
    if not isinstance(sku, str):
        return {"type": "unknown", "size": None}
    
    # Pattern: SIMPLE_<hash>_<TYPE>_<SIZE>
    pattern = r"SIMPLE_[a-f0-9]+_([A-Z_]+)_([A-Z0-9]+)"
    match = re.match(pattern, sku)
    
    if match:
        component_type = match.group(1)
        size = match.group(2)
        return {"type": component_type, "size": size}
    
    return {"type": "unknown", "size": None}

def convert_unfulfillable_to_cut_packet_format(input_file: str) -> pd.DataFrame:
    """Convert unfulfillable_production_sheet.csv to cut packet format"""
    
    # Read the unfulfillable production sheet
    df = pd.read_csv(input_file)
    
    # Group by order to reconstruct full products
    orders = {}
    
    for _, row in df.iterrows():
        order_id = str(row['Order #'])
        item_name = row['Item Name']
        sku = row['Item SKU']
        quantity = int(row['Quantity'])
        created_date = row['Created']
        
        if order_id not in orders:
            orders[order_id] = {
                'order_id': order_id,
                'created_date': created_date,
                'items': [],
                'base_product': extract_base_product(item_name)
            }
        
        # Parse SKU to get component info
        sku_info = parse_sku_components(sku)
        
        orders[order_id]['items'].append({
            'name': item_name,
            'sku': sku,
            'quantity': quantity,
            'component_type': sku_info['type'],
            'size': sku_info['size']
        })
    
    # Convert to cut packet format
    cut_packet_rows = []
    
    for order_id, order_data in orders.items():
        # Determine sizes for this order
        top_size = None
        bottom_size = None
        accessories = []
        
        for item in order_data['items']:
            comp_type = item['component_type']
            size = item['size']
            
            if comp_type == 'TOP':
                top_size = size
            elif comp_type == 'BOTTOM':
                bottom_size = size
            elif comp_type in ['WITH_ACCESSORY', 'DUPATTA', 'POTLI']:
                if size and size != 'TRUE':
                    accessories.append(f"Accessory-{size}")
                else:
                    accessories.append("Accessory")
        
        # Create row for cut packet
        row = {
            'Order#': order_id,
            'Product': order_data['base_product'],
            'Date': order_data['created_date'],
            'TopSize': top_size,
            'BottomSize': bottom_size,
            'Accessories': ', '.join(accessories) if accessories else '',
            'Quantity': 1,  # Each order is typically 1 set
            '_FulfillmentStatus': 'unfulfilled'  # All items in this sheet are unfulfillable
        }
        
        cut_packet_rows.append(row)
    
    return pd.DataFrame(cut_packet_rows)

def generate_cut_packet_summary(df: pd.DataFrame) -> Dict:
    """Generate summary statistics for cut packet production"""
    
    if df.empty:
        return {"total_orders": 0, "products": {}, "sizes": {}}
    
    # Count by product
    product_counts = df['Product'].value_counts().to_dict()
    
    # Count by sizes
    size_counts = {}
    
    # Top sizes
    top_sizes = df['TopSize'].dropna().value_counts().to_dict()
    for size, count in top_sizes.items():
        size_counts[f"Top-{size}"] = count
    
    # Bottom sizes  
    bottom_sizes = df['BottomSize'].dropna().value_counts().to_dict()
    for size, count in bottom_sizes.items():
        size_counts[f"Bottom-{size}"] = count
    
    return {
        "total_orders": len(df),
        "products": product_counts,
        "sizes": size_counts
    }

def generate_production_requirements_from_unfulfillable(input_file: str, output_file: str):
    """Main function to generate production requirements from unfulfillable sheet"""
    
    try:
        # Convert to cut packet format
        cut_packet_df = convert_unfulfillable_to_cut_packet_format(input_file)
        
        if cut_packet_df.empty:
            return None, {}, ["No data found in input file"]
        
        # Generate summary
        summary = generate_cut_packet_summary(cut_packet_df)
        
        # Save the cut packet format
        cut_packet_df.to_csv(output_file, index=False)
        
        return cut_packet_df, summary, []
        
    except Exception as e:
        return None, {}, [f"Error processing file: {str(e)}"]
