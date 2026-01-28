import streamlit as st
import pandas as pd
import tempfile
import os
import sys

# Add src paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'uniware'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'common'))

from item_master_generator import generate_items
from uniware_shopify_linker import generate_channel_item_type

st.set_page_config(page_title="Uniware Tools", layout="wide")

# Sidebar for tool selection
st.sidebar.title("🛍️ Uniware Processing Tools")
tool = st.sidebar.selectbox(
    "Select Tool",
    ["Item Master Generator", "Uniware Shopify Linker"]
)

if tool == "Item Master Generator":
    st.header("📦 Item Master Generator")
    st.write("Upload ShopifyNewProducts.csv to generate Uniware items")
    
    uploaded_file = st.file_uploader("Upload ShopifyNewProducts.csv", type=["csv"])
    
    if uploaded_file and st.button("Generate Uniware Items"):
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
            tmp_input.write(uploaded_file.getvalue())
            input_path = tmp_input.name
        
        # Create temp output files
        simple_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        bundle_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        simple_output.close()
        bundle_output.close()
        
        try:
            # Run the original script
            generate_items(input_path, simple_output.name, bundle_output.name)
            
            # Read results
            simple_df = pd.read_csv(simple_output.name)
            bundle_df = pd.read_csv(bundle_output.name)
            
            st.write("### Simple Items", simple_df)
            st.write("### Bundle Items", bundle_df)
            
            # Combine for download
            combined_df = pd.concat([simple_df, bundle_df], ignore_index=True)
            st.write("### All Items Combined", combined_df)
            st.download_button(
                "📥 Download UniwareNewItems.csv",
                combined_df.to_csv(index=False),
                "UniwareNewItems.csv",
                "text/csv"
            )
            
        finally:
            # Cleanup temp files
            os.unlink(input_path)
            os.unlink(simple_output.name)
            os.unlink(bundle_output.name)

elif tool == "Uniware Shopify Linker":
    st.header("🔗 Uniware Shopify Linker")
    st.write("Upload ShopifyNewProducts.csv to generate channel item mappings")
    
    uploaded_file = st.file_uploader("Upload ShopifyNewProducts.csv", type=["csv"])
    
    if uploaded_file and st.button("Link New Products"):
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
            tmp_input.write(uploaded_file.getvalue())
            input_path = tmp_input.name
        
        # Create temp output file
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        output_file.close()
        
        try:
            # Run the original script
            generate_channel_item_type(input_path, output_file.name)
            
            # Read and display results
            result_df = pd.read_csv(output_file.name)
            st.write("### Channel Items", result_df)
            st.download_button(
                "📥 Download NewLinks.csv",
                result_df.to_csv(index=False),
                "NewLinks.csv",
                "text/csv"
            )
            
        finally:
            # Cleanup temp files
            os.unlink(input_path)
            os.unlink(output_file.name)
