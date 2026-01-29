import csv
import pandas as pd
from datetime import datetime
from collections import Counter
from cut_packet_adapter import generate_production_requirements_from_unfulfillable, generate_cut_packet_summary

def generate_production_requirements(input_file, output_file):
    """
    Generate production requirements using cut-packet-generator logic
    """
    try:
        # Use the new cut packet adapter
        cut_packet_df, summary, errors = generate_production_requirements_from_unfulfillable(input_file, output_file)
        
        if errors:
            return None, {}, errors
        
        if cut_packet_df is None or cut_packet_df.empty:
            return None, {}, ["No production requirements generated"]
        
        # Return in expected format
        return cut_packet_df, summary.get('products', {}), []
        
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
