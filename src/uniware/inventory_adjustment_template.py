import csv
import pandas as pd

def generate_inventory_adjustment_template(input_file, output_file):
    """
    Generate inventory adjustment template from DailyProductionRequirements.csv
    """
    try:
        # Read the input CSV
        df = pd.read_csv(input_file)
        
        # Check required columns
        if 'Item Name' not in df.columns:
            return None, [f"Error: 'Item Name' column not found in input file"]
        if 'SKU Code' not in df.columns:
            return None, [f"Error: 'SKU Code' column not found in input file"]
        
        # Get unique combinations of SKU Code and Item Name
        unique_items = df[['SKU Code', 'Item Name']].drop_duplicates().dropna()
        
        # Create inventory adjustment template
        adjustment_data = []
        for _, row in unique_items.iterrows():
            adjustment_data.append({
                'SKU Code': row['SKU Code'],
                'Item Name': row['Item Name'],
                'Quantity': '',  # Empty column to be filled
                'Adjustment Type': 'ADD',  # Default value, can be changed
                'Inventory Type': 'GOOD_INVENTORY'  # Default value, can be changed
            })
        
        # Sort by Item Name
        adjustment_data = sorted(adjustment_data, key=lambda x: x['Item Name'])
        
        # Create DataFrame
        adjustment_df = pd.DataFrame(adjustment_data)
        
        # Save to output file
        adjustment_df.to_csv(output_file, index=False)
        
        return adjustment_df, []
        
    except Exception as e:
        return None, [f"Error processing file: {str(e)}"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python inventory_adjustment.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    df, errors = generate_inventory_adjustment_template(input_file, output_file)
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print(f"Inventory adjustment template generated: {output_file}")
        print(f"Unique items: {len(df)}")
