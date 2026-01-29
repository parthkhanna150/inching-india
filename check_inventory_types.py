import pandas as pd

def check_inventory_skus():
    """
    Check what types of SKUs are in the inventory file
    """
    inventory_df = pd.read_csv("/Users/vasukhanna/Downloads/inventory_29th.csv")
    
    print(f"Total inventory records: {len(inventory_df)}")
    
    # Check SKU patterns
    simple_skus = inventory_df[inventory_df['Sku Code'].str.startswith('SIMPLE_', na=False)]
    bdl_skus = inventory_df[inventory_df['Sku Code'].str.startswith('BDL_', na=False)]
    other_skus = inventory_df[~inventory_df['Sku Code'].str.startswith(('SIMPLE_', 'BDL_'), na=False)]
    
    print(f"\nSKU Breakdown in Inventory:")
    print(f"SIMPLE_ SKUs: {len(simple_skus)}")
    print(f"BDL_ SKUs: {len(bdl_skus)}")
    print(f"Other SKUs: {len(other_skus)}")
    
    print(f"\nSample SIMPLE_ SKUs:")
    for sku in simple_skus['Sku Code'].head(5):
        print(f"  {sku}")
    
    print(f"\nSample BDL_ SKUs:")
    for sku in bdl_skus['Sku Code'].head(5):
        print(f"  {sku}")
    
    print(f"\nSample Other SKUs:")
    for sku in other_skus['Sku Code'].head(5):
        print(f"  {sku}")

if __name__ == "__main__":
    check_inventory_skus()
