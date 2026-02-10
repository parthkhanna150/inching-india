import csv
import pandas as pd

def generate_uniware_inventory_adjustment(input_file, output_file, default_inventory_type="GOOD_INVENTORY", default_adjustment_type="ADD"):
    """
    Generate Uniware inventory adjustment CSV from filled template
    """
    try:
        # Read the filled template CSV
        df = pd.read_csv(input_file)
        
        # Check required columns
        if 'SKU Code' not in df.columns:
            return None, [f"Error: 'SKU Code' column not found in input file"]
        if 'Quantity' not in df.columns:
            return None, [f"Error: 'Quantity' column not found in input file"]
        
        # Filter out rows with empty quantities
        df = df[df['Quantity'].notna() & (df['Quantity'] != '') & (df['Quantity'] != 0)]
        
        if df.empty:
            return None, [f"Error: No valid quantities found in the template"]
        
        # Create Uniware inventory adjustment format
        uniware_data = []
        for _, row in df.iterrows():
            try:
                quantity = int(float(row['Quantity']))
                if quantity > 0:  # Only process positive quantities
                    # Use values from template if available, otherwise use defaults
                    inventory_type = row.get('Inventory Type', default_inventory_type)
                    adjustment_type = row.get('Adjustment Type', default_adjustment_type)
                    
                    uniware_data.append({
                    'Product Code*': row['SKU Code'],
                    'Quantity*': quantity,
                    'Shelf Code*': 'DEFAULT',
                    'Adjustment Type*': adjustment_type,
                    'Inventory Type': inventory_type,
                    'Transfer to Shelf Code': '',
                    'Sla': '',
                    'Source Batch Code': '',
                    'Remarks': '',
                    'Force Allocate': ''
                    })
            except (ValueError, TypeError):
                continue  # Skip invalid quantities
        
        if not uniware_data:
            return None, [f"Error: No valid positive quantities found"]
        
        # Create DataFrame
        uniware_df = pd.DataFrame(uniware_data)
        
        # Save to output file
        uniware_df.to_csv(output_file, index=False)
        
        return uniware_df, []
        
    except Exception as e:
        return None, [f"Error processing file: {str(e)}"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python uniware_inventory_adjustment.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    df, errors = generate_uniware_inventory_adjustment(input_file, output_file)
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print(f"Uniware inventory adjustment generated: {output_file}")
        print(f"Items to adjust: {len(df)}")
