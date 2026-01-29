import pandas as pd

def find_correct_duplicate_skus():
    """
    Find which duplicate SKUs are correct by checking inventory
    """
    # Read the files
    duplicates_df = pd.read_csv("/Users/vasukhanna/Downloads/duplicate_item_names.csv")
    inventory_df = pd.read_csv("/Users/vasukhanna/Downloads/inventory_29th.csv")
    
    print(f"Total duplicate SKUs: {len(duplicates_df)}")
    print(f"Total inventory records: {len(inventory_df)}")
    
    # Get SKUs that have inventory
    inventory_skus = set(inventory_df['Sku Code'].tolist())
    
    # Find which duplicate SKUs have inventory (correct ones)
    correct_skus = []
    incorrect_skus = []
    
    for _, row in duplicates_df.iterrows():
        sku = row['Sku Code']
        item_name = row['Item Name']
        
        if sku in inventory_skus:
            correct_skus.append({
                'Item Name': item_name,
                'Sku Code': sku,
                'Status': 'CORRECT (Has Inventory)'
            })
        else:
            incorrect_skus.append({
                'Item Name': item_name,
                'Sku Code': sku,
                'Status': 'INCORRECT (No Inventory)'
            })
    
    print(f"\nCorrect SKUs (have inventory): {len(correct_skus)}")
    print(f"Incorrect SKUs (no inventory): {len(incorrect_skus)}")
    
    # Group by item name to show the analysis
    print("\n=== ANALYSIS BY ITEM NAME ===")
    
    all_results = correct_skus + incorrect_skus
    results_df = pd.DataFrame(all_results)
    
    for item_name, group in results_df.groupby('Item Name'):
        correct_count = len(group[group['Status'].str.contains('CORRECT')])
        incorrect_count = len(group[group['Status'].str.contains('INCORRECT')])
        
        print(f"\nItem: {item_name}")
        print(f"  Correct SKUs: {correct_count}, Incorrect SKUs: {incorrect_count}")
        
        for _, row in group.iterrows():
            status_icon = "✅" if "CORRECT" in row['Status'] else "❌"
            print(f"  {status_icon} {row['Sku Code']} - {row['Status']}")
    
    # Save results
    results_df.to_csv("/Users/vasukhanna/Downloads/duplicate_sku_analysis.csv", index=False)
    
    # Create a file with just the incorrect SKUs to disable
    incorrect_df = pd.DataFrame(incorrect_skus)
    if not incorrect_df.empty:
        incorrect_df.to_csv("/Users/vasukhanna/Downloads/incorrect_duplicate_skus.csv", index=False)
        print(f"\nIncorrect SKUs saved to: /Users/vasukhanna/Downloads/incorrect_duplicate_skus.csv")
    
    print(f"Complete analysis saved to: /Users/vasukhanna/Downloads/duplicate_sku_analysis.csv")

if __name__ == "__main__":
    find_correct_duplicate_skus()
