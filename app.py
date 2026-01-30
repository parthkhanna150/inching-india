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
from production_template_generator import generate_inventory_adjustment_template
from uniware_inventory_adjustment import generate_uniware_inventory_adjustment
from inventory_template_generator import generate_inventory_template_from_list

st.set_page_config(page_title="Inching India Operations", layout="wide")

# Sidebar for process selection
st.sidebar.title("🛍️ Inching India Operations")

process = st.sidebar.selectbox(
    "Select Process",
    ["Production Kickoff", "Daily Inventory Update", "Product Addition", "Returns Inventory"]
)

st.sidebar.markdown("### 📖 Documentation")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    main_sop = st.button("Main SOP")
with col2:
    prod_sop = st.button("Prod SOP")
with col3:
    ops_sop = st.button("Ops SOP")

# Determine which process to show - buttons override process selection
if main_sop:
    process = "README"
elif prod_sop:
    process = "Production Team SOP"
elif ops_sop:
    process = "Operations Team SOP"

if process == "README":
    st.title("📖 Standard Operating Procedures")
    
    # Read and display the README.md file
    try:
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        st.markdown(readme_content)
        
    except FileNotFoundError:
        st.error("README.md file not found")
    except Exception as e:
        st.error(f"Error reading README.md: {str(e)}")

elif process == "Production Team SOP":
    st.title("🏭 Production Team SOP")
    
    st.markdown("""
    ## Morning - Production Kickoff
    1. **Extract Data:** Navigate to **Orders** → **Unfulfillable**
    2. **Export:** Download the sheet of all items currently short in inventory
    
    ![Unfulfilled Inventory Download](static/images/unfulfilled_inventory_list_download.png)
    
    3. **Process:** Use the Production Kickoff tool to generate DailyProductionRequirements.csv
    4. **Task Allocation:** Break down quantities by SKU and distribute to the **Tailors**

    ## Throughout the Day - Manufacturing
    1. **Manufacturing:** Tailors work on assigned items based on production requirements
    2. **Quality Control:** Verify finished pieces meet standards
    3. **Count:** Track completed quantities by SKU

    ## End of Day - Production Wrap-up
    1. **Count:** Verify total finished pieces produced during the day
    2. **Report:** Prepare clear list (SKU + Final Count) for inventory adjustment

    ## Twice Daily - Daily Inventory Update
    1. **File Prep:** Use production report to create Inventory Adjustment CSV using Daily Inventory Update process
    2. **Generate Template:** Upload DailyProductionRequirements.csv to get template with SKU Code, Item Name, Quantity, Adjustment Type, Inventory Type columns
    3. **Fill Template:** 
       * **Quantity:** Enter produced quantities (positive numbers)
       * **Adjustment Type:** Leave as ADD (default for production)
       * **Inventory Type:** Leave as GOOD_INVENTORY (default for production)
    4. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
       * Select **Update Existing** and upload the generated Uniware CSV
       
    ![Inventory Adjustment Upload](static/images/inventory_adjustment_upload_to_uniware.png)
    
       * *Note: Once uploaded, fulfillable orders will automatically move to Operations Team's Shipping Panel*

    ## TODOs
    - Notes and Shopify Order number needed in unfulfillable sheet
    """)

elif process == "Operations Team SOP":
    st.title("📦 Operations Team SOP")
    
    st.markdown("""
    ## Throughout the Day - Order Processing & Fulfillment

    ### Regular Processing
    1. **Monitor:** Check the **Shipping Panel** for orders that have moved to "Ready to Ship"
    2. **Process:** Select orders (First-Come-First-Serve basis)
    3. **Invoice & Label:** Use the **Top-Left Dropdown** to **Create Invoices**, then **Generate Labels**

    ### Partial Fulfillment
    1. **Identify:** Orders stuck in "Unfulfillable" but have some ready items
    2. **Manual Split:** Go to **Order Details** → **Top-Left Dropdown** → **Create Manual Shipment**
    3. **Select:** Choose only the "Good" items for shipment

    ## One-time Process - Product Addition

    ### Step 1: Create Shopify Products
    - Create Shopify Products as normal (by duplicating from Shopify)
    - *These products will get synced to Uniware (syncing happens every 15 minutes) as UNLINKED products*

    ### Step 2: Add Products to Item Master
    - Go to "Unlinked" tab in Uniware
    - Filter on "Shopify" Channel
    - Download this file and rename to **ShopifyNewProducts.csv**
    
    ![Product Addition Download](static/images/product_addition_download_from_uniware.png)
    
    - Go to Product Addition from the dropdown and use item-master-generator software to upload this file
    - Click "Generate Uniware Items" and download the result (**UniwareNewItems.csv**)
    - Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload UniwareNewItems.csv

    ### Step 3: Link Items to Shopify Products
    - After the Import finishes, go to Product Addition from the dropdown and use uniware-shopify linker software
    - Upload the **original ShopifyNewProducts.csv** file
    - Click "Link New Products" and download the result (**NewLinks.csv**)
    - Go to Imports → Choose "Channel Item Sync" → "Create New and Update Existing" → Upload NewLinks.csv

    ### Step 4: Update Inventory
    - Items have been successfully uploaded and linked for inventory tracking
    - **Important:** The inventory is zero for these new items
    - Follow the **Production Team's Daily Inventory Update process** to update quantities

    ## Returns Inventory Process

    ### When Needed: Returns, Damages, Stock Corrections
    1. **Get Inventory List:** Export current inventory list from Uniware
    2. **Generate Template:** Use Returns Inventory process to upload inventory list and get template
    3. **Fill Template:**
       * **Quantity:** Enter adjustment quantities (always positive numbers)
       * **Adjustment Type:** Choose ADD, REMOVE, or REPLACE as needed
       * **Inventory Type:** Choose GOOD_INVENTORY or VIRTUAL_INVENTORY as appropriate
    4. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
       * Select **Update Existing** and upload the generated Uniware CSV

    **Use Cases:** Returns processing, damaged goods removal, stock corrections, etc.

    ## TODOs
    - Invoicing algorithm for price breakdown
    - Partial CoD adjustment for partial shipments
    """)

elif process == "Production Kickoff":
    st.title("✂️ Cut Packet Generator")
    st.caption("Upload Unfulfillable CSV → select Base Product(s) → optional filters → download Excel with SUMIFS formulas")
    
    # Import the cut packet generator
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'uniware'))
    from cut_packet_generator import generate_cut_packet_data, create_excel_with_formulas, extract_base_product
    
    uploaded_file = st.file_uploader("Upload Unfulfillable Items CSV", type=["csv"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Show preview
            st.write("### Preview of uploaded data:")
            st.dataframe(df.head())
            
            # Get base products for selection
            if 'Item Name' in df.columns:
                titles = df['Item Name'].dropna().astype(str).str.strip()
                base_series = titles.map(extract_base_product)
                counts = base_series.value_counts().to_dict()
                
                # Sort by count desc
                bases_sorted = sorted(counts.keys(), key=lambda b: (-counts[b], b.lower()))
                label_for_base = {b: f"{b} ({counts.get(b, 0)})" for b in bases_sorted}
                base_for_label = {v: k for k, v in label_for_base.items()}
                
                picked_labels = st.multiselect(
                    "Select Base Product(s)",
                    options=[label_for_base[b] for b in bases_sorted]
                )
                picked_bases = [base_for_label[lbl] for lbl in picked_labels]
                
                if st.button("Generate Cut Packet Excel", type="primary", disabled=len(picked_bases)==0):
                    with st.spinner("Processing…"):
                        try:
                            # Generate cut packet data
                            section_a, size_cols = generate_cut_packet_data(df, base_products=picked_bases)
                            
                            if section_a.empty:
                                st.warning("No matching orders found with current filters.")
                            else:
                                st.success(f"✅ Generated {len(section_a)} cut packet entries")
                                
                                # Show preview
                                st.write("### Cut Packet Data Preview")
                                st.dataframe(section_a.head(20))
                                
                                # Create Excel with formulas
                                product_label = ", ".join(picked_bases[:3]) + (" ..." if len(picked_bases) > 3 else "")
                                excel_data = create_excel_with_formulas(section_a, size_cols, product_label)
                                
                                # Download button
                                st.download_button(
                                    label="⬇️ Download Cut Packet Excel",
                                    data=excel_data,
                                    file_name="cut_packet_OUTPUT.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                                
                        except Exception as e:
                            st.error(f"Error generating cut packet: {str(e)}")
            
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")

elif process == "Daily Inventory Update":
    st.title("📊 Daily Inventory Update Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Daily Inventory Update SOP (Production Team)
        **Role:** System Reconciliation (Inventory Sync)
        
        #### Steps:
        1. **Get Production Requirements:** Use the DailyProductionRequirements.csv file generated from the **Production Kickoff** process
        2. **File Prep:** Use **Fill Quantities** tab below to upload DailyProductionRequirements.csv
        3. **Fill Quantities:** Download the template and fill in the produced quantities from production report
        4. **Generate Final CSV:** Use **Uniware Adjustment Generator** tab below to upload the filled template
        5. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
           - Select **Update Existing** and upload the generated Uniware CSV
           - *Note: Once uploaded, fulfillable orders will automatically move to Operations Team's Shipping Panel*
        
        💡 **Note:** If you don't have DailyProductionRequirements.csv, ask Production Team to run the **Production Kickoff** process first.
        """)
    
    # Tabs for daily inventory update tools
    tab1, tab2 = st.tabs(["📋 Fill Quantities", "📤 Uniware Adjustment Generator"])
    
    with tab1:
        st.header("Fill Quantities")
        st.info("Upload DailyProductionRequirements.csv to generate inventory adjustment template")
        
        uploaded_file = st.file_uploader("Upload DailyProductionRequirements.csv", type=["csv"], key="daily_inventory_template")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Inventory Template", key="daily_generate"):
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
                        st.info("💡 Fill in the Quantity column with production numbers from production report")
                        
                        st.download_button(
                            "📥 Download InventoryAdjustmentTemplate.csv",
                            template_df.to_csv(index=False),
                            "InventoryAdjustmentTemplate.csv",
                            "text/csv",
                            key="daily_download_template"
                        )
                    
                finally:
                    os.unlink(input_path)
                    os.unlink(output_file.name)
    
    with tab2:
        st.header("Uniware Adjustment Generator")
        st.info("Upload the filled InventoryAdjustmentTemplate.csv to generate Uniware-compatible CSV")
        
        uploaded_file = st.file_uploader("Upload Filled InventoryAdjustmentTemplate.csv", type=["csv"], key="daily_uniware_adjustment")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Uniware Adjustment CSV", key="daily_uniware_generate"):
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
                            "text/csv",
                            key="daily_download_uniware"
                        )
                    
                finally:
                    os.unlink(input_path)
                    os.unlink(output_file.name)

elif process == "Returns Inventory":
    st.title("🔄 Returns Inventory Process")
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Returns Inventory SOP (Operations Team)
        **Role:** Update inventory for returns and adjustments
        
        #### Steps:
        1. **Get Inventory List:** Export current inventory list from Uniware
        2. **File Prep:** Use **Fill Quantities** tab below to upload the inventory list CSV
        3. **Fill Template:** Download the template and fill in:
           - **Quantity**: Always positive numbers
           - **Adjustment Type**: ADD, REMOVE, or REPLACE
           - **Inventory Type**: GOOD_INVENTORY or VIRTUAL_INVENTORY
        4. **Generate Final CSV:** Use **Uniware Adjustment Generator** tab below to upload the filled template
        5. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
           - Select **Update Existing** and upload the generated Uniware CSV
        
        💡 **Use Cases:** Returns processing, damaged goods removal, stock corrections, etc.
        """)
    
    # Tabs for returns inventory tools
    tab1, tab2 = st.tabs(["📋 Fill Quantities", "📤 Uniware Adjustment Generator"])
    
    with tab1:
        st.header("Fill Quantities")
        st.info("Upload an inventory list CSV to generate inventory adjustment template")
        
        uploaded_file = st.file_uploader("Upload Inventory List CSV", type=["csv"], key="returns_inventory_template")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Template from Inventory List", key="returns_generate"):
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                output_file.close()
                
                try:
                    template_df, errors = generate_inventory_template_from_list(input_path, output_file.name)
                    
                    if errors:
                        st.error("Errors encountered:")
                        for error in errors:
                            st.write(f"❌ {error}")
                    
                    if template_df is not None:
                        st.success("✅ Inventory template generated successfully!")
                        st.write("### Inventory Adjustment Template", template_df)
                        st.info("💡 Fill in the Quantity, Adjustment Type, and Inventory Type columns, then use the 'Uniware Adjustment Generator' tab")
                        
                        st.download_button(
                            "📥 Download InventoryAdjustmentTemplate.csv",
                            template_df.to_csv(index=False),
                            "InventoryAdjustmentTemplate.csv",
                            "text/csv",
                            key="returns_download_template"
                        )
                    
                finally:
                    os.unlink(input_path)
                    os.unlink(output_file.name)
    
    with tab2:
        st.header("Uniware Adjustment Generator")
        st.info("Upload the filled InventoryAdjustmentTemplate.csv to generate Uniware-compatible CSV")
        
        uploaded_file = st.file_uploader("Upload Filled InventoryAdjustmentTemplate.csv", type=["csv"], key="returns_uniware_adjustment")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Uniware Adjustment CSV", key="returns_uniware_generate"):
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
                            "text/csv",
                            key="returns_download_uniware"
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
    tab1, tab2, tab3 = st.tabs(["📋 Inventory Template Generator", "📤 Uniware Adjustment Generator", "📊 Inventory List Template"])
    
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
    
    with tab3:
        st.header("Inventory List Template Generator")
        st.info("Upload an inventory list CSV to generate inventory adjustment template")
        
        uploaded_file = st.file_uploader("Upload Inventory List CSV", type=["csv"], key="inventory_list_template")
        
        if uploaded_file:
            st.write("### Preview of uploaded data:")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Generate Template from Inventory List"):
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                output_file.close()
                
                try:
                    template_df, errors = generate_inventory_template_from_list(input_path, output_file.name)
                    
                    if errors:
                        st.error("Errors encountered:")
                        for error in errors:
                            st.write(f"❌ {error}")
                    
                    if template_df is not None:
                        st.success("✅ Inventory template generated successfully!")
                        st.write("### Inventory Adjustment Template", template_df)
                        st.info("💡 Fill in the 'Quantity' column with adjustment quantities, then use the 'Uniware Adjustment Generator' tab")
                        
                        st.download_button(
                            "📥 Download InventoryAdjustmentTemplate.csv",
                            template_df.to_csv(index=False),
                            "InventoryAdjustmentTemplate.csv",
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
