import csv
import pandas as pd
from datetime import datetime
from collections import Counter

def generate_production_requirements(input_file, output_file):
    """
    Generate DailyProductionRequirements.csv from unfulfillable items
    """
    try:
        # Read the input CSV
        df = pd.read_csv(input_file)
        
        # Extract required columns
        production_data = []
        
        for _, row in df.iterrows():
            # Extract data with fallbacks
            sku_code = row.get('Item SKU', '')
            item_name = row.get('Item Name', '')
            notes = row.get('Notes', '')  # Fallback to empty if not exists
            date_created = row.get('Created', row.get('Channel Created Date Time', ''))
            order_number = row.get('Order #', '')
            shipping_type = row.get('Shipping Type', row.get('Pymt', ''))  # Fallback to Pymt if Shipping Type doesn't exist
            
            production_data.append({
                'SKU Code': sku_code,
                'Item Name': item_name,
                'Notes': notes,
                'Date Created': date_created,
                'Order Number': order_number,
                'Shipping Type': shipping_type
            })
        
        # Create DataFrame
        production_df = pd.DataFrame(production_data)
        
        # Sort by Date Created
        if 'Date Created' in production_df.columns and not production_df['Date Created'].empty:
            production_df['Date Created'] = pd.to_datetime(production_df['Date Created'], errors='coerce')
            production_df = production_df.sort_values('Date Created')
        
        # Save to output file
        production_df.to_csv(output_file, index=False)
        
        # Generate simple item counts
        simple_items = production_df[production_df['SKU Code'].str.startswith('SIMPLE_', na=False)]
        item_counts = simple_items['Item Name'].value_counts().to_dict()
        
        return production_df, item_counts, []
        
    except Exception as e:
        return None, {}, [f"Error processing file: {str(e)}"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python production_kickoff.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    df, counts, errors = generate_production_requirements(input_file, output_file)
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print(f"Production requirements generated: {output_file}")
        print(f"Total items: {len(df)}")
        print(f"Simple item types: {len(counts)}")
