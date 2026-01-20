import pandas as pd

# Read the simple items CSV
df = pd.read_csv('/Users/vasukhanna/Desktop/inching-india/src/uniware/generated_output/simple_items.csv')

# Create inventory adjustment records
inventory_records = []

for _, row in df.iterrows():
    product_code = row['Product Code*']
    name = row['Name*']
    
    # Check if name contains "test" (case insensitive)
    quantity = 1 if 'test' in name.lower() else 1000
    
    inventory_record = {
        'Product Code*': product_code,
        'Quantity*': quantity,
        'Shelf Code*': 'DEFAULT',
        'Adjustment Type*': 'ADD',
        'Inventory Type': 'VIRTUAL_INVENTORY',
        'Transfer to Shelf Code': '',
        'Sla': '',
        'Source Batch Code': '',
        'Remarks': '',
        'Force Allocate': ''
    }
    inventory_records.append(inventory_record)

# Create DataFrame and save to CSV
inventory_df = pd.DataFrame(inventory_records)
inventory_df.to_csv('/Users/vasukhanna/Desktop/inching-india/src/uniware/generated_output/inventory_adjustment.csv', index=False)

print(f"Generated inventory adjustment file with {len(inventory_records)} records")
print(f"Test products (quantity=1): {sum(1 for r in inventory_records if r['Quantity*'] == 1)}")
print(f"Regular products (quantity=1000): {sum(1 for r in inventory_records if r['Quantity*'] == 1000)}")
