import pandas as pd
import re
from datetime import datetime, timedelta
from io import BytesIO

def convert_unfulfillable_to_shopify_format(df):
    """Convert unfulfillable sheet to Shopify-like format for cut packet processing"""
    
    # Map columns to Shopify format
    shopify_rows = []
    
    for _, row in df.iterrows():
        # Use Display Order # if available, otherwise fall back to Order #
        order_num = row.get('Display Order #', row.get('Order #', ''))
        
        shopify_row = {
            'Name': str(order_num),
            'Lineitem name': row.get('Channel Product Name', row['Item Name']),
            'Lineitem sku': row['Item SKU'],
            'Lineitem quantity': row['Quantity'],
            'Created at': row['Created'],
            'Lineitem fulfillment status': 'unfulfilled',
            'Notes': row.get('Notes', ''),
            'Shipping Method': row.get('Pymt', 'Standard')
        }
        shopify_rows.append(shopify_row)
    
    return pd.DataFrame(shopify_rows)

def extract_base_product(title):
    """Extract base product name"""
    if not isinstance(title, str):
        return str(title)
    
    # Remove size and variant info after dash
    if " - " in title:
        return title.split(" - ")[0].strip()
    return title.strip()

def parse_sizes_from_sku(sku, title):
    """Extract top/bottom sizes from SKU and title"""
    top_size = bottom_size = None
    
    if isinstance(sku, str) and 'SIMPLE_' in sku:
        # Pattern: SIMPLE_hash_TYPE_SIZE
        parts = sku.split('_')
        if len(parts) >= 4:
            component_type = parts[2]
            size = parts[3]
            
            if component_type == 'TOP':
                top_size = size
            elif component_type == 'BOTTOM':
                bottom_size = size
    
    return top_size, bottom_size

def generate_cut_packet_data(df, base_products=None):
    """Generate cut packet data from unfulfillable sheet"""
    
    # Convert to Shopify-like format
    shopify_df = convert_unfulfillable_to_shopify_format(df)
    
    # Group by order to reconstruct products
    component_orders = {}
    
    for _, row in shopify_df.iterrows():
        order_id = row['Name']
        base_product = extract_base_product(row['Lineitem name'])
        
        # Filter by selected base products
        if base_products and base_product not in base_products:
            continue
        
        # Extract sizes and create separate rows for Top/Bottom
        top_size, bottom_size = parse_sizes_from_sku(row['Lineitem sku'], row['Lineitem name'])
        
        # Only create entries for SIMPLE_ SKUs (Top and Bottom components)
        components = []
        if top_size:
            components.append(('Top', top_size))
        if bottom_size:
            components.append(('Bottom', bottom_size))
        
        # Only add component entries if we have SIMPLE_ SKUs
        for component, size in components:
            component_key = f"{order_id}_{component}_{size}_{row['Lineitem sku']}"
            component_orders[component_key] = {
                'Date': row['Created at'],
                'Order#': order_id,
                'Product': base_product,
                'Component': component,
                'Size': size,
                'Qty': 1,
                'SKU': row['Lineitem sku'],
                'Notes': row.get('Notes', '')
            }
    
    # Convert to DataFrame
    cut_packet_df = pd.DataFrame(list(component_orders.values()))
    
    # Get unique sizes for columns (keeping for compatibility)
    all_sizes = set()
    if not cut_packet_df.empty:
        all_sizes.update(cut_packet_df['Size'].dropna().unique())
    
    size_cols = sorted([s for s in all_sizes if s], key=lambda x: (len(x), x))
    
    return cut_packet_df, size_cols

def create_excel_with_formulas(section_a_df, size_cols, product_label="Selected Products"):
    """Create Excel file with Section A data and Section B with SUMIFS formulas"""
    
    output = BytesIO()
    
    # Create a simple Excel file using pandas
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Section A - Raw data
        section_a_df.to_excel(writer, sheet_name='CutPacket', startrow=2, index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['CutPacket']
        
        # Add title
        worksheet.write(0, 0, f"Cut Packet Report - {product_label}")
        
        # Section B - Summary
        start_row = len(section_a_df) + 6
        worksheet.write(start_row, 0, "Section B - Size Summary")
        
        # Create summary data
        if not section_a_df.empty:
            products = section_a_df['Product'].unique()
            
            # Headers
            worksheet.write(start_row + 2, 0, "Product")
            worksheet.write(start_row + 2, 1, "Total Orders")
            
            col_idx = 2
            for size in size_cols:
                worksheet.write(start_row + 2, col_idx, f"Size {size}")
                col_idx += 1
            
            # Data rows
            for i, product in enumerate(products):
                row_idx = start_row + 3 + i
                product_data = section_a_df[section_a_df['Product'] == product]
                
                worksheet.write(row_idx, 0, product)
                worksheet.write(row_idx, 1, len(product_data))
                
                # Size counts
                col_idx = 2
                for size in size_cols:
                    size_count = len(product_data[product_data['Size'] == size])
                    worksheet.write(row_idx, col_idx, size_count)
                    col_idx += 1
    
    output.seek(0)
    return output.getvalue()
