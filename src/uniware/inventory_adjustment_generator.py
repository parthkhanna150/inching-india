import pandas as pd

# Read the populated item master CSV and filter for SIMPLE items only
df = pd.read_csv('/Users/vasukhanna/Desktop/inching-india/src/uniware/generated_output/populated_item_master.csv')
simple_items = df[df['Type'] == 'SIMPLE']

# Create inventory adjustment records
inventory_records = []

for _, row in simple_items.iterrows():
    product_code = row['Product Code*']
    name = row['Name*']
    
    # GOOD_INVENTORY record (quantity = 0)
    good_inventory_record = {
        'Product Code*': product_code,
        'Quantity*': 0,
        'Shelf Code*': 'DEFAULT',
        'Adjustment Type*': 'ADD',
        'Inventory Type': 'GOOD_INVENTORY',
        'Transfer to Shelf Code': '',
        'Sla': '',
        'Source Batch Code': '',
        'Remarks': '',
        'Force Allocate': ''
    }
    inventory_records.append(good_inventory_record)
    
    # VIRTUAL_INVENTORY record (quantity = 1000)
    virtual_inventory_record = {
        'Product Code*': product_code,
        'Quantity*': 1000,
        'Shelf Code*': 'DEFAULT',
        'Adjustment Type*': 'ADD',
        'Inventory Type': 'VIRTUAL_INVENTORY',
        'Transfer to Shelf Code': '',
        'Sla': '',
        'Source Batch Code': '',
        'Remarks': '',
        'Force Allocate': ''
    }
    inventory_records.append(virtual_inventory_record)

# Create DataFrame and save to CSV
inventory_df = pd.DataFrame(inventory_records)
inventory_df.to_csv('/Users/vasukhanna/Desktop/inching-india/src/uniware/generated_output/inventory_adjustment.csv', index=False)

print(f"Generated inventory adjustment file with {len(inventory_records)} records")
print(f"SIMPLE items processed: {len(simple_items)}")
print(f"GOOD_INVENTORY records (quantity=0): {len(simple_items)}")
print(f"VIRTUAL_INVENTORY records (quantity=1000): {len(simple_items)}")
