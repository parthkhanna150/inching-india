import pandas as pd

def create_disable_item_master(input_file, output_file):
    """
    Create item master CSV to disable SKUs that don't start with SIMPLE_ or BDL_
    """
    # Read the enabled products CSV
    df = pd.read_csv(input_file)
    
    # Filter SKUs that don't start with SIMPLE_ or BDL_
    skus_to_disable = df[~df['Sku Code'].str.startswith(('SIMPLE_', 'BDL_'))]
    
    if skus_to_disable.empty:
        print("No SKUs found that need to be disabled.")
        return
    
    # Create item master format for disabling
    disable_data = []
    for _, row in skus_to_disable.iterrows():
        disable_data.append({
            'Category Code': 'Clothing',
            'Product Code': row['Sku Code'],
            'Name': row['Item Name'],
            'Description': '',
            'Scan Identifier': row['Sku Code'],
            'Requires Customization': 'False',
            'Length (mm)': '1',
            'Width (mm)': '1',
            'Height (mm)': '1',
            'Weight (gms)': '1000.000',
            'EAN': '',
            'UPC': '',
            'ISBN': '',
            'Color': row.get('Color', ''),
            'Size': row.get('Size', ''),
            'Brand': row.get('Brand', 'Inching india'),
            'Item Detail Fields': '',
            'Tags': '',
            'Image Url': '',
            'Product Page Url': '',
            'Tax Type Code': '',
            'GST Tax Type Code': '',
            'Base Price': '',
            'Cost Price': '800.00',
            'TAT': '',
            'MRP': '1000.00',
            'Updated': '',
            'Category Name': 'Clothing',
            'Enabled': 'False',  # This is the key - disable the SKU
            'Type': 'SIMPLE',
            'Component Product Code': '',
            'Component Quantity': '',
            'Component Price': '',
            'HSN CODE': '',
            'Tax Calculation Type': '',
            'Batch Group': '',
            'GRN expiry tolerance (in days)': '',
            'Dispatch expiry tolerance (in days)': '',
            'Return expiry tolerance (in days)': '',
            'Expirable': 'From Category',
            'Determine Expiry From': 'From Category',
            'Shelf Life': '',
            'Expiry Date': '',
            'Sku Type': 'GOODS',
            'Fragile': 'False',
            'Dangerous Good': 'False'
        })
    
    # Create DataFrame and save
    disable_df = pd.DataFrame(disable_data)
    disable_df.to_csv(output_file, index=False)
    
    print(f"Created item master to disable {len(disable_data)} SKUs")
    print(f"Output saved to: {output_file}")
    
    # Show summary of SKUs being disabled
    print("\nSKUs to be disabled:")
    for sku in skus_to_disable['Sku Code'].head(10):
        print(f"  - {sku}")
    if len(skus_to_disable) > 10:
        print(f"  ... and {len(skus_to_disable) - 10} more")

if __name__ == "__main__":
    input_file = "/Users/vasukhanna/Downloads/enabled_products_29th.csv"
    output_file = "/Users/vasukhanna/Downloads/disable_non_standard_skus.csv"
    
    create_disable_item_master(input_file, output_file)
