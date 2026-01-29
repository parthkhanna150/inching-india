#!/usr/bin/env python3

import pandas as pd

# Load data
print("Loading data...")
enabled_df = pd.read_csv("/Users/vasukhanna/Downloads/enabled_products_29th.csv")
mappings_df = pd.read_csv("/Users/vasukhanna/Downloads/Item Master_29012026225903.csv")
duplicates_df = pd.read_csv("/Users/vasukhanna/Downloads/duplicate_item_names.csv")

# Get all enabled SIMPLE_ SKUs
enabled_simples = set(enabled_df[enabled_df['Sku Code'].str.startswith('SIMPLE_')]['Sku Code'])
print(f"Total enabled SIMPLE_ SKUs: {len(enabled_simples)}")

# Get duplicate BDL_ SKUs and their mappings
duplicate_bundles = set(duplicates_df['Sku Code'])
bundle_mappings = mappings_df[mappings_df['Product Code'].isin(duplicate_bundles)]

print(f"Checking {len(duplicate_bundles)} duplicate bundle SKUs...")

bundles_to_disable = []
bundle_stats = []

for bundle_sku in duplicate_bundles:
    # Get all SIMPLE_ items mapped to this bundle
    mapped_simples = bundle_mappings[bundle_mappings['Product Code'] == bundle_sku]['Component Product Code']
    
    # Check if any mapped SIMPLE_ items are still enabled
    enabled_mapped_simples = [s for s in mapped_simples if s in enabled_simples]
    disabled_mapped_simples = [s for s in mapped_simples if s not in enabled_simples]
    
    bundle_stats.append({
        'Bundle_Sku_Code': bundle_sku,
        'Total_Mapped_Simples': len(mapped_simples),
        'Enabled_Mapped_Simples': len(enabled_mapped_simples),
        'Disabled_Mapped_Simples': len(disabled_mapped_simples)
    })
    
    if len(enabled_mapped_simples) == 0 and len(mapped_simples) > 0:
        # All SIMPLE_ items are disabled, so bundle can be disabled
        bundles_to_disable.append({
            'Bundle_Sku_Code': bundle_sku,
            'Total_Mapped_Simples': len(mapped_simples),
            'Enabled_Mapped_Simples': 0,
            'Status': 'CAN_DISABLE'
        })

print(f"\nBundles that can be safely disabled: {len(bundles_to_disable)}")

# Show statistics
stats_df = pd.DataFrame(bundle_stats)
print(f"\nBundle Statistics:")
print(f"Bundles with all SIMPLE_ items enabled: {len(stats_df[stats_df['Disabled_Mapped_Simples'] == 0])}")
print(f"Bundles with some SIMPLE_ items disabled: {len(stats_df[stats_df['Disabled_Mapped_Simples'] > 0])}")
print(f"Bundles with all SIMPLE_ items disabled: {len(stats_df[stats_df['Enabled_Mapped_Simples'] == 0])}")

# Show examples of bundles with disabled components
mixed_bundles = stats_df[stats_df['Disabled_Mapped_Simples'] > 0].head(10)
if len(mixed_bundles) > 0:
    print(f"\nFirst 10 bundles with some disabled SIMPLE_ items:")
    for _, row in mixed_bundles.iterrows():
        print(f"  {row['Bundle_Sku_Code']} - Enabled: {row['Enabled_Mapped_Simples']}, Disabled: {row['Disabled_Mapped_Simples']}")

# Save all statistics
stats_path = "/Users/vasukhanna/Downloads/bundle_component_analysis.csv"
stats_df.to_csv(stats_path, index=False)
print(f"\nAll bundle statistics saved to: {stats_path}")

if bundles_to_disable:
    # Save results
    disable_df = pd.DataFrame(bundles_to_disable)
    output_path = "/Users/vasukhanna/Downloads/bundles_to_disable.csv"
    disable_df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")
    
    # Show first few examples
    print("\nFirst 10 bundles to disable:")
    for bundle in bundles_to_disable[:10]:
        print(f"  {bundle['Bundle_Sku_Code']} - {bundle['Total_Mapped_Simples']} disabled SIMPLE_ items")
else:
    print("No bundles found with all SIMPLE_ items disabled.")
