import pandas as pd

def find_unmapped_duplicate_skus():
    """
    Find duplicate SKUs that don't have bundle-to-simple mappings
    """
    # Read the files
    duplicates_df = pd.read_csv("/Users/vasukhanna/Downloads/incorrect_duplicate_skus.csv")
    mappings_df = pd.read_csv("/Users/vasukhanna/Downloads/Item Master_29012026225903.csv")
    
    print(f"Total duplicate SKUs: {len(duplicates_df)}")
    print(f"Total mapping records: {len(mappings_df)}")
    
    # Get unique bundle SKUs from mappings
    mapped_bundle_skus = set(mappings_df['Product Code'].tolist())
    
    print(f"Unique bundle SKUs with mappings: {len(mapped_bundle_skus)}")
    
    # Find duplicate SKUs that don't have mappings
    unmapped_skus = []
    mapped_skus = []
    
    for _, row in duplicates_df.iterrows():
        sku = row['Sku Code']
        item_name = row['Item Name']
        
        if sku in mapped_bundle_skus:
            mapped_skus.append({
                'Item Name': item_name,
                'Sku Code': sku,
                'Status': 'HAS MAPPING'
            })
        else:
            unmapped_skus.append({
                'Item Name': item_name,
                'Sku Code': sku,
                'Status': 'NO MAPPING'
            })
    
    print(f"\nDuplicate SKUs with mappings: {len(mapped_skus)}")
    print(f"Duplicate SKUs WITHOUT mappings: {len(unmapped_skus)}")
    
    # Show summary statistics only
    print(f"\n=== SUMMARY ===")
    all_results = mapped_skus + unmapped_skus
    results_df = pd.DataFrame(all_results)
    
    summary_stats = []
    for item_name, group in results_df.groupby('Item Name'):
        mapped_count = len(group[group['Status'] == 'HAS MAPPING'])
        unmapped_count = len(group[group['Status'] == 'NO MAPPING'])
        summary_stats.append({
            'Item Name': item_name,
            'With Mappings': mapped_count,
            'Without Mappings': unmapped_count,
            'Total': len(group)
        })
    
    summary_df = pd.DataFrame(summary_stats)
    print(f"Items with mixed mapping status: {len(summary_df[summary_df['With Mappings'] > 0])}")
    print(f"Items with no mappings at all: {len(summary_df[summary_df['With Mappings'] == 0])}")
    
    # Show first few examples
    print(f"\nFirst 5 items with mixed status:")
    mixed_items = summary_df[summary_df['With Mappings'] > 0].head()
    for _, row in mixed_items.iterrows():
        print(f"  {row['Item Name'][:50]}... - Mapped: {row['With Mappings']}, Unmapped: {row['Without Mappings']}")
    
    # Save results
    if unmapped_skus:
        unmapped_df = pd.DataFrame(unmapped_skus)
        unmapped_df.to_csv("/Users/vasukhanna/Downloads/unmapped_duplicate_skus.csv", index=False)
        print(f"\nUnmapped duplicate SKUs saved to: /Users/vasukhanna/Downloads/unmapped_duplicate_skus.csv")
        print(f"These {len(unmapped_skus)} SKUs can be safely disabled as they have no bundle mappings.")
    
    if mapped_skus:
        mapped_df = pd.DataFrame(mapped_skus)
        mapped_df.to_csv("/Users/vasukhanna/Downloads/mapped_duplicate_skus.csv", index=False)
        print(f"Mapped duplicate SKUs saved to: /Users/vasukhanna/Downloads/mapped_duplicate_skus.csv")
        print(f"These {len(mapped_skus)} SKUs have mappings - review carefully before disabling.")

if __name__ == "__main__":
    find_unmapped_duplicate_skus()
