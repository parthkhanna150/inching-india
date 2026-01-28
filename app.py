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

st.set_page_config(page_title="Inching India Operations", layout="wide")

# Sidebar for process selection
st.sidebar.title("🛍️ Inching India Operations")
process = st.sidebar.selectbox(
    "Select Process",
    ["Product Addition", "Inventory Adjustment"]
)

if process == "Product Addition":
    st.title("📦 Product Addition Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=False):
        st.markdown("""
        ### Product Addition SOP (Mehak)
        **Role:** Add new products in the system before following inventory adjustment
        
        #### Steps:
        1. **Create Shopify Products** as normal (by duplicating from Shopify). 
           *These products will get synced to Uniware (syncing happens every 15 minutes) as UNLINKED products.*
        
        2. **Add unlinked products to item master:**
           - Go to "Unlinked" tab in Uniware
           - Filter on "Shopify" Channel
           - Download this file and rename to **ShopifyNewProducts.csv**
           - Upload to **Step 2** below
           - Click "Generate Uniware Items" and download **UniwareNewItems.csv**
           - Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload UniwareNewItems.csv
        
        3. **Link Uniware Items to Shopify products:**
           - After Import finishes, upload the **original ShopifyNewProducts.csv** to **Step 3** below
           - Click "Link New Products" and download **NewLinks.csv**
           - Go to Imports → Choose "Channel Item Sync" → "Create New and Update Existing" → Upload NewLinks.csv
        
        ⚠️ **Important:** After completion, follow the Inventory Adjustment SOP to update quantities.
        """)
    
    # Step 1: Shopify (Manual)
    st.header("🛒 Step 1: Create Shopify Products")
    st.info("⚠️ This step is done manually on Shopify - Create products by duplicating existing ones. Products will sync to Uniware as UNLINKED products in ~15 minutes.")
    st.markdown("---")
    
    # Step 2: Item Master Generator
    st.header("🔧 Step 2: Item Master Generator")
    st.info("Upload ShopifyNewProducts.csv to generate Uniware items")
    
    uploaded_file_step2 = st.file_uploader("Upload ShopifyNewProducts.csv", type=["csv"], key="item_master")
    
    if uploaded_file_step2:
        st.write("### Preview of uploaded data:")
        df = pd.read_csv(uploaded_file_step2)
        st.dataframe(df.head())
        
        if st.button("Generate Uniware Items"):
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                tmp_input.write(uploaded_file_step2.getvalue())
                input_path = tmp_input.name
            
            simple_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            bundle_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            simple_output.close()
            bundle_output.close()
            
            try:
                generate_items(input_path, simple_output.name, bundle_output.name)
                
                simple_df = pd.read_csv(simple_output.name)
                bundle_df = pd.read_csv(bundle_output.name)
                
                st.success("✅ Items generated successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Simple Items", simple_df)
                with col2:
                    st.write("### Bundle Items", bundle_df)
                
                combined_df = pd.concat([simple_df, bundle_df], ignore_index=True)
                st.write("### All Items Combined", combined_df)
                st.download_button(
                    "📥 Download UniwareNewItems.csv",
                    combined_df.to_csv(index=False),
                    "UniwareNewItems.csv",
                    "text/csv"
                )
                
            finally:
                os.unlink(input_path)
                os.unlink(simple_output.name)
                os.unlink(bundle_output.name)
    
    st.markdown("---")
    
    # Step 3: Uniware Shopify Linker
    st.header("🔗 Step 3: Uniware Shopify Linker")
    st.info("Upload the original ShopifyNewProducts.csv to generate channel item mappings")
    
    uploaded_file_step3 = st.file_uploader("Upload ShopifyNewProducts.csv", type=["csv"], key="shopify_linker")
    
    if uploaded_file_step3:
        st.write("### Preview of uploaded data:")
        df = pd.read_csv(uploaded_file_step3)
        st.dataframe(df.head())
        
        if st.button("Link New Products"):
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                tmp_input.write(uploaded_file_step3.getvalue())
                input_path = tmp_input.name
            
            output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            output_file.close()
            
            try:
                generate_channel_item_type(input_path, output_file.name)
                
                result_df = pd.read_csv(output_file.name)
                st.success("✅ Channel items linked successfully!")
                st.write("### Channel Items", result_df)
                st.download_button(
                    "📥 Download NewLinks.csv",
                    result_df.to_csv(index=False),
                    "NewLinks.csv",
                    "text/csv"
                )
                
            finally:
                os.unlink(input_path)
                os.unlink(output_file.name)

elif process == "Inventory Adjustment":
    st.title("📊 Inventory Adjustment Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=False):
        st.markdown("""
        ### Inventory Adjustment SOP (Simran)
        **Role:** System Reconciliation (Inventory Sync)
        
        #### When: Twice a day - 11am and 3pm
        
        #### Steps:
        1. **File Prep:** Create an Inventory Adjustment CSV based on Ilias's production report
        2. **Data Entry:**
           - **Increment:** Set `GOOD_INVENTORY` to the produced quantity (e.g., `10`)
           - **Decrement:** Set `VIRTUAL_INVENTORY` to the negative of that quantity (e.g., `-10`)
        3. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
           - Select **Update Existing** and upload your file
           - *Note: Once uploaded, fulfillable orders will automatically move to Mehak's Shipping Panel*
        
        ⚠️ **TODO:** Script to prepare Inventory Adjustment CSV will be added here.
        """)
    
    st.info("🚧 Inventory Adjustment tools will be added here soon.")
    st.write("This section will contain scripts to help prepare Inventory Adjustment CSV files based on production reports.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Daily Operations Team:**")
st.sidebar.markdown("• Mehak - Operations")
st.sidebar.markdown("• Mandeep - Processing & Fulfillment") 
st.sidebar.markdown("• Ilias - Production")
st.sidebar.markdown("• Simran - Inventory Adjustment")
st.sidebar.markdown("• Prabhav - Support")
