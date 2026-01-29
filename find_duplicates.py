import pandas as pd

def find_duplicate_item_names(input_file):
    """
    Find SIMPLE_ and BDL_ SKUs with duplicate item names
    """
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Filter only SIMPLE_ and BDL_ SKUs
    standard_skus = df[df['Sku Code'].str.startswith(('SIMPLE_', 'BDL_'))]
    
    print(f"Total SIMPLE_ and BDL_ SKUs: {len(standard_skus)}")
    
    # Group by Item Name and find duplicates
    duplicates = standard_skus.groupby('Item Name').filter(lambda x: len(x) > 1)
    
    if duplicates.empty:
        print("No duplicate item names found among SIMPLE_ and BDL_ SKUs.")
        return
    
    # Sort by Item Name for better readability
    duplicates = duplicates.sort_values(['Item Name', 'Sku Code'])
    
    print(f"\nFound {len(duplicates)} SKUs with duplicate item names:")
    print(f"Affecting {duplicates['Item Name'].nunique()} unique item names\n")
    
    # Group and display duplicates
    for item_name, group in duplicates.groupby('Item Name'):
        print(f"Item Name: {item_name}")
        for _, row in group.iterrows():
            print(f"  - SKU: {row['Sku Code']}")
        print()
    
    # Save duplicates to CSV for review
    output_file = "/Users/vasukhanna/Downloads/duplicate_item_names.csv"
    duplicates[['Item Name', 'Sku Code', 'Type', 'Enabled']].to_csv(output_file, index=False)
    print(f"Duplicate items saved to: {output_file}")

if __name__ == "__main__":
    input_file = "/Users/vasukhanna/Downloads/enabled_products_29th.csv"
    find_duplicate_item_names(input_file)
