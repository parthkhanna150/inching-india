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
from production_kickoff import generate_production_requirements
from inventory_adjustment_template import generate_inventory_adjustment_template
from uniware_inventory_adjustment import generate_uniware_inventory_adjustment

st.set_page_config(page_title="Inching India Operations", layout="wide")

# Sidebar for process selection
st.sidebar.title("🛍️ Inching India Operations")

# Separate daily and one-off processes
st.sidebar.markdown("### 📅 Daily Processes")
daily_process = st.sidebar.selectbox(
    "Select Daily Process",
    ["Production Kickoff", "Inventory Adjustment"]
)

st.sidebar.markdown("### 🔧 One-off Processes")
oneoff_process = st.sidebar.selectbox(
    "Select One-off Process",
    ["Product Addition"]
)

st.sidebar.markdown("### 📖 Documentation")
show_readme = st.sidebar.button("SOP")

# Determine which process to show
if show_readme:
    process = "README"
elif daily_process:
    process = daily_process
else:
    process = oneoff_process

if process == "README":
    st.title("📖 Standard Operating Procedures")
    
    # Read and display the README.md file
    try:
        with open('/Users/vasukhanna/Desktop/inching-india/README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        st.markdown(readme_content)
        
    except FileNotFoundError:
        st.error("README.md file not found")
    except Exception as e:
        st.error(f"Error reading README.md: {str(e)}")

elif process == "Production Kickoff":
    st.title("🚀 Production Kickoff Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Production Kickoff SOP (Production Team)
        **Role:** Orchestrating the whole process
        
        #### Steps:
        1. **Extract Data:** Navigate to **Orders** → **Unfulfillable**
        2. **Export:** Download the sheet of all items currently short in inventory
        3. **Process:** Upload the file below to generate **DailyProductionRequirements.csv**
        4. **Handoff:** Send this file to **Production Team** to start the tailoring queue
        
        **Output:** The processed file will contain:
        - SKU Code, Item Name, Notes, Date Created, Order Number, Shipping Type
        - Sorted by creation date
        - Count summary of each simple item needed
        """)
    
    st.header("📊 Generate Daily Production Requirements")
    st.info("Upload the Unfulfillable items CSV to generate production requirements")
    
    uploaded_file = st.file_uploader("Upload Unfulfillable Items CSV", type=["csv"], key="production_kickoff")
    
    if uploaded_file:
        st.write("### Preview of uploaded data:")
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        
        if st.button("Generate Production Requirements"):
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                tmp_input.write(uploaded_file.getvalue())
                input_path = tmp_input.name
            
            output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            output_file.close()
            
            try:
                production_df, item_counts, errors = generate_production_requirements(input_path, output_file.name)
                
                if errors:
                    st.error("Errors encountered:")
                    for error in errors:
                        st.write(f"❌ {error}")
                
                if production_df is not None:
                    st.success("✅ Production requirements generated successfully!")
                    
                    # Show the processed data
                    st.write("### Daily Production Requirements", production_df)
                    
                    # Show item counts
                    if item_counts:
                        st.write("### Simple Item Counts")
                        counts_df = pd.DataFrame(list(item_counts.items()), columns=['Item Name', 'Quantity Needed'])
                        st.dataframe(counts_df)
                    
                    # Download button
                    st.download_button(
                        "📥 Download DailyProductionRequirements.csv",
                        production_df.to_csv(index=False),
                        "DailyProductionRequirements.csv",
                        "text/csv"
                    )
                
            finally:
                os.unlink(input_path)
                os.unlink(output_file.name)

elif process == "Product Addition":
    st.title("📦 Product Addition Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Product Addition SOP (Operations Team)
        **Role:** Add new products in the system before following inventory adjustment
        
        #### Steps:
        1. **Create Shopify Products** as normal (by duplicating from Shopify). 
           *These products will get synced to Uniware (syncing happens every 15 minutes) as UNLINKED products.*
        
        2. **Add unlinked products to item master:**
           - Go to "Unlinked" tab in Uniware
           - Filter on "Shopify" Channel
           - Download this file and rename to **ShopifyNewProducts.csv**
           - Use **Item Master Generator** tab below to upload this file
           - Click "Generate Uniware Items" and download **UniwareNewItems.csv**
        
        3. **Import to Uniware:**
           - Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload UniwareNewItems.csv
        
        4. **Link Uniware Items to Shopify products:**
           - After Import finishes, use **Uniware Shopify Linker** tab below to upload the **original ShopifyNewProducts.csv**
           - Click "Link New Products" and download **NewLinks.csv**
        
        5. **Import Channel Links:**
           - Go to Imports → Choose "Channel Item Sync" → "Create New and Update Existing" → Upload NewLinks.csv
        
        ⚠️ **Important:** After completion, follow the Inventory Adjustment SOP to update quantities.
        """)
    
    # Tabs for the tools
    tab1, tab2 = st.tabs(["🔧 Item Master Generator", "🔗 Uniware Shopify Linker"])
    
    with tab1:
        st.header("Item Master Generator")
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
    
    with tab2:
        st.header("Uniware Shopify Linker")
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
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Inventory Adjustment SOP (Production Team)
        **Role:** System Reconciliation (Inventory Sync)
        
        #### Steps:
        1. **Get Production Requirements:** Use the DailyProductionRequirements.csv file generated from the **Production Kickoff** process
        2. **File Prep:** Use **Inventory Template Generator** tab below to upload DailyProductionRequirements.csv
        3. **Fill Quantities:** Download the template and fill in the produced quantities from production report
        4. **Generate Final CSV:** Use **Uniware Adjustment Generator** tab below to upload the filled template
        5. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
           - Select **Update Existing** and upload the generated Uniware CSV
           - *Note: Once uploaded, fulfillable orders will automatically move to Operations Team's Shipping Panel*
        
        💡 **Note:** If you don't have DailyProductionRequirements.csv, ask Operations Team to run the **Production Kickoff** process first.
        """)
    
    # Tabs for inventory adjustment tools
    tab1, tab2 = st.tabs(["📋 Inventory Template Generator", "📤 Uniware Adjustment Generator"])
    
    with tab1:
        st.header("Inventory Template Generator")
        st.info("Upload DailyProductionRequirements.csv to generate inventory adjustment template")
        
        uploaded_file = st.file_uploader("Upload DailyProductionRequirements.csv", type=["csv"], key="inventory_template")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Inventory Template"):
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                output_file.close()
                
                try:
                    template_df, errors = generate_inventory_adjustment_template(input_path, output_file.name)
                    
                    if errors:
                        st.error("Errors encountered:")
                        for error in errors:
                            st.write(f"❌ {error}")
                    
                    if template_df is not None:
                        st.success("✅ Inventory template generated successfully!")
                        st.write("### Inventory Adjustment Template", template_df)
                        st.info("💡 Fill in the 'Quantity' column with production numbers from Ilias's report")
                        
                        st.download_button(
                            "📥 Download InventoryAdjustmentTemplate.csv",
                            template_df.to_csv(index=False),
                            "InventoryAdjustmentTemplate.csv",
                            "text/csv"
                        )
                    
                finally:
                    os.unlink(input_path)
                    os.unlink(output_file.name)
    
    with tab2:
        st.header("Uniware Adjustment Generator")
        st.info("Upload the filled InventoryAdjustmentTemplate.csv to generate Uniware-compatible CSV")
        
        uploaded_file = st.file_uploader("Upload Filled InventoryAdjustmentTemplate.csv", type=["csv"], key="uniware_adjustment")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Uniware Adjustment CSV"):
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                output_file.close()
                
                try:
                    uniware_df, errors = generate_uniware_inventory_adjustment(input_path, output_file.name)
                    
                    if errors:
                        st.error("Errors encountered:")
                        for error in errors:
                            st.write(f"❌ {error}")
                    
                    if uniware_df is not None:
                        st.success("✅ Uniware adjustment CSV generated successfully!")
                        st.write("### Uniware Inventory Adjustment", uniware_df)
                        st.info("📤 Upload this file to Uniware: Tools → Imports → Inventory Adjustment → Update Existing")
                        
                        st.download_button(
                            "📥 Download UniwareInventoryAdjustment.csv",
                            uniware_df.to_csv(index=False),
                            "UniwareInventoryAdjustment.csv",
                            "text/csv"
                        )
                    
                finally:
                    os.unlink(input_path)
                    os.unlink(output_file.name)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Team Structure:**")
st.sidebar.markdown("• **Operations:** Mehak, Mandeep, Bharti")
st.sidebar.markdown("• **Production:** Simran, Ilias Master Ji") 
st.sidebar.markdown("• **Tech:** Prabhav")
