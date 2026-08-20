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
from production_inventory_adjustment import generate_production_inventory_adjustment
from returns_inventory_adjustment import generate_returns_inventory_adjustment
from international_item_master_generator import generate_international_bundles

st.set_page_config(page_title="Inching India Operations", layout="wide")

# Sidebar for process selection
st.sidebar.title("🛍️ Inching India Operations")

process = st.sidebar.selectbox(
    "Select Process",
    ["Production Kickoff", "Product Addition", "Manual Inventory Adjustment", "Production Inventory Adjustment", "Returns Inventory Adjustment", "Exhibition Customer Intake"]
)

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
    1. **Extract Data:** Navigate to **Order Items** → **Unfulfillable**
    2. **Export:** Download the sheet of all items currently short in inventory
    """)
    
    st.image("static/images/unfulfilled_inventory_list_download.png", caption="Unfulfilled Inventory Download")
    
    st.markdown("""
    3. **Process:** Use the Production Kickoff tool to generate DailyProductionRequirements.csv
    4. **Task Allocation:** Break down quantities by SKU and distribute to the **Tailors**

    ## Throughout the Day - Manufacturing
    1. **Manufacturing:** Tailors work on assigned items based on production requirements
    2. **Quality Control:** Verify finished pieces meet standards
    3. **Count:** Track completed quantities by SKU

    ## End of Day - Production Wrap-up
    1. **Count:** Verify total finished pieces produced during the day
    2. **Report:** Prepare clear list (SKU + Final Count) for inventory adjustment

    ## Adding Inventory
    **Note:** This inventory update will happen at the time of Processing Returns as well as daily production.
    
    1. **Go to Inventory page** in Uniware (as seen in image)
    2. **Click "Add Inventory"** and in the pop-up, search for the item name, then put quantity to be added as "Good Inventory" type
    """)
    
    st.image("static/images/inventory_adjustment_upload_to_uniware.png", caption="Inventory Page in Uniware")
    st.image("static/images/add_inventory_popup.png", caption="Add Inventory Pop-up")
    
    st.markdown("""

    ## TODOs
    - Notes and Shopify Order number needed in unfulfillable sheet
    """)

elif process == "Manual Inventory Adjustment":
    st.title("📦 Adding Inventory SOP")
    
    st.markdown("""
    ## Adding Inventory Process
    **Note:** This inventory update will happen at the time of Processing Returns as well as daily production.
    
    ### Steps:
    1. **Go to Inventory page** in Uniware (as seen in image)
    2. **Click "Add Inventory"** and in the pop-up, search for the item name, then put quantity to be added as "Good Inventory" type
    """)
    
    st.image("static/images/inventory_adjustment_upload_to_uniware.png", caption="Inventory Page in Uniware")
    st.image("static/images/add_inventory_popup.png", caption="Add Inventory Pop-up")
    
    st.markdown("""
    ### When to Use:
    - **Daily Production:** After completing production, add finished items to inventory
    - **Processing Returns:** When returned items are received and inspected as good condition
    
    ### Important Notes:
    - Always select "Good Inventory" type for items in sellable condition
    - Search by exact item name to ensure correct product selection
    - Double-check quantities before confirming the addition
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
    """)
    
    st.image("static/images/product_addition_download_from_uniware.png", caption="Product Addition Download")
    
    st.markdown("""
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
    
    # SOP Instructions
    with st.expander("📋 SOP Instructions - Click to expand", expanded=True):
        st.markdown("""
        ### Production Kickoff SOP (Production Team)
        **Role:** Orchestrating the whole process
        
        #### Steps:
        1. **Extract Data:** Navigate to **Order Items** → **Unfulfillable**
        """)
        
        st.image("static/images/unfulfilled_inventory_list_download.png", caption="Unfulfilled Inventory Download")
        
        st.markdown("""
        2. **Ensure Created filter is cleared**
        """)
        
        st.image("static/images/clear_created_filter.png", caption="Clear Created Filter")
        
        st.markdown("""
        3. **Export:** Download this sheet
        """)
        
        st.markdown("""
        4. **Process:** Upload the file below to generate **Cut Packet Requirements** (enhanced with cut-packet-generator logic)
        5. **Handoff:** Send this file to **Production Team** to start the tailoring queue
        
        **Enhanced Output:** The processed file will contain:
        - Order-wise breakdown with base products
        - Size requirements (Top/Bottom sizes)
        - Component breakdown for production planning
        - Production summary by product and size
        """)
    
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
        """)
        
        st.image("static/images/inventory_adjustment_upload_to_uniware.png", caption="Inventory Adjustment Upload")
        
        st.markdown("""
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
        
        ### Step 1: Create Shopify Products
        - Create Shopify Products as normal (by duplicating from Shopify)
        - *These products will get synced to Uniware (syncing happens every 15 minutes) as UNLINKED products*

        ### Step 2: Add Products to Item Master
        - Go to "Unlinked" tab in Uniware
        - Filter on "Shopify" Channel
        - Download this file and rename to **ShopifyNewProducts.csv**
        """)
        
        st.image("static/images/product_addition_download_from_uniware.png", caption="Product Addition Download")
        
        st.markdown("""
        - Use **Item Master Generator** tab below to upload this file
        - Click "Generate Uniware Items" and download the result (**UniwareNewItems.csv**)
        - Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload UniwareNewItems.csv
        """)

        st.image("static/images/uniware_item_master_import.png", caption="Uniware Item Master Import Configuration")

        st.markdown("""
        ### Step 3: Link Items to Shopify Products
        - After the Import finishes, use **Uniware Shopify Linker** tab below to upload the **original ShopifyNewProducts.csv** file
        - Click "Link New Products" and download the result (**NewLinks.csv**)
        - Go to Imports → Choose "Channel Item Type" → "Create New and Update Existing" → Upload NewLinks.csv
        """)

        st.image("static/images/uniware_channel_item_type_import.png", caption="Uniware Channel Item Type Import Configuration")

        st.markdown("""
        ### Step 4: Update Inventory
        - Items have been successfully uploaded and linked for inventory tracking
        - **Important:** The inventory is zero for these new items
        - Follow the **Adding Inventory SOP** to update quantities
        """)

        st.divider()

        st.markdown("""
        ---
        ## International Product Addition SOP
        *For adding products to the international website (SHOPIFY_INT / POS channels)*

        The SIMPLE items for international products already exist in the domestic item master.
        You only need to create new BUNDLE items and link them to the international channel.

        ### Step 1: Create International Shopify Products
        - Create products on the international Shopify store (by duplicating from Shopify)
        - These products will sync to Uniware as UNLINKED products under the international channel

        ### Step 2: Download Required Files
        - **Item Master:** Go to Uniware → Item Master → Export All → Download as CSV
        - **Unlinked Listings:** Go to Uniware → Channel Item Type → Filter on international channel (SHOPIFY_INT) → Filter status "UNLINKED" → Download as CSV

        ### Step 3: Generate International Bundles & Links
        - Use the **International Item Master Generator** tab below
        - Upload both files: the full Item Master CSV and the Unlinked International Listings CSV
        - Click "Generate International Bundles"
        - This will generate:
          - **international_bundle_item_master.csv** — New BUNDLE items mapped to existing SIMPLE items
          - **international_channel_item_type.csv** — Channel links for the international channel
          - **missing_components.csv** — Any products whose SIMPLE items don't exist yet (these need to be added via the domestic flow first)

        ### Step 4: Upload to Uniware
        - Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload **international_bundle_item_master.csv**
        - After the Item Master import finishes, go to Imports → Choose "Channel Item Type" → "Create New and Update Existing" → Upload **international_channel_item_type.csv**

        ### Step 5: Handle Missing Components
        - Review **missing_components.csv** for any products that couldn't be linked
        - These products need their SIMPLE items created first using the **domestic** Product Addition flow (Steps 1–3 above)
        - After creating the missing SIMPLE items, re-run the International Item Master Generator
        """)
    
    # Tabs for the tools
    tab1, tab2, tab3 = st.tabs(["🔧 Item Master Generator", "🔗 Uniware Shopify Linker", "🌐 International Item Master Generator"])
    
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

    with tab3:
        st.header("International Item Master Generator")
        st.info("Upload your full Item Master and the unlinked international listings to generate bundle items and channel links.")

        col_upload1, col_upload2 = st.columns(2)
        with col_upload1:
            uploaded_item_master = st.file_uploader("Upload Item Master CSV (full export from Uniware)", type=["csv"], key="intl_item_master")
        with col_upload2:
            uploaded_intl_listings = st.file_uploader("Upload Unlinked International Listings CSV", type=["csv"], key="intl_listings")

        if uploaded_item_master and uploaded_intl_listings:
            st.write("### Preview of International Listings:")
            intl_df = pd.read_csv(uploaded_intl_listings)
            st.dataframe(intl_df.head())

            if st.button("Generate International Bundles"):
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_im:
                    tmp_im.write(uploaded_item_master.getvalue())
                    item_master_path = tmp_im.name

                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_intl:
                    tmp_intl.write(uploaded_intl_listings.getvalue())
                    intl_listings_path = tmp_intl.name

                output_dir = tempfile.mkdtemp()

                try:
                    generate_international_bundles(item_master_path, intl_listings_path, output_dir)

                    bundle_path = os.path.join(output_dir, "international_bundle_item_master.csv")
                    channel_path = os.path.join(output_dir, "international_channel_item_type.csv")
                    missing_path = os.path.join(output_dir, "missing_components.csv")

                    if os.path.exists(bundle_path):
                        bundle_df = pd.read_csv(bundle_path)
                        st.success(f"✅ Generated {len(bundle_df)} bundle item rows")
                        st.write("### Bundle Item Master", bundle_df)
                        st.download_button(
                            "📥 Download international_bundle_item_master.csv",
                            bundle_df.to_csv(index=False),
                            "international_bundle_item_master.csv",
                            "text/csv",
                            key="dl_intl_bundles"
                        )
                    else:
                        st.warning("No bundle items were generated. Check if SIMPLE items exist in the item master.")

                    if os.path.exists(channel_path):
                        channel_df = pd.read_csv(channel_path)
                        st.success(f"✅ Generated {len(channel_df)} channel item links")
                        st.write("### Channel Item Type Links", channel_df)
                        st.download_button(
                            "📥 Download international_channel_item_type.csv",
                            channel_df.to_csv(index=False),
                            "international_channel_item_type.csv",
                            "text/csv",
                            key="dl_intl_channel"
                        )

                    if os.path.exists(missing_path):
                        missing_df = pd.read_csv(missing_path)
                        st.warning(f"⚠️ {len(missing_df)} missing components found — these need SIMPLE items created via the domestic flow first.")
                        st.write("### Missing Components", missing_df)
                        st.download_button(
                            "📥 Download missing_components.csv",
                            missing_df.to_csv(index=False),
                            "missing_components.csv",
                            "text/csv",
                            key="dl_missing"
                        )

                finally:
                    os.unlink(item_master_path)
                    os.unlink(intl_listings_path)

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

elif process == "Production Inventory Adjustment":
    generate_production_inventory_adjustment()

elif process == "Returns Inventory Adjustment":
    generate_returns_inventory_adjustment()

elif process == "Exhibition Customer Intake":
    st.title("🎪 Exhibition Customer Intake")
    st.caption("Capture customer details at the booth and send a WhatsApp follow-up")

    BUSINESS_WHATSAPP = "919041555664"

    with st.form("customer_intake_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone Number *", placeholder="e.g. 9876543210")
            city = st.text_input("City")
        with col2:
            interest = st.multiselect(
                "Interested In",
                ["Kurtas", "Co-ords", "Suits", "Dupattas", "Accessories", "Other"]
            )
            budget = st.selectbox(
                "Budget Range",
                ["", "Under ₹1,000", "₹1,000 – ₹3,000", "₹3,000 – ₹5,000", "Above ₹5,000"]
            )
            follow_up = st.selectbox(
                "Follow-up Preference",
                ["WhatsApp", "Call", "No follow-up needed"]
            )
        notes = st.text_area("Notes / Items they liked", height=80)
        submitted = st.form_submit_button("Save & Generate WhatsApp Link", type="primary")

    if submitted:
        if not name or not phone:
            st.error("Name and phone number are required.")
        else:
            phone_clean = phone.strip().replace(" ", "").replace("-", "").lstrip("0")
            if not phone_clean.startswith("91"):
                phone_clean = "91" + phone_clean

            interest_str = ", ".join(interest) if interest else "general browsing"
            budget_str = f" | Budget: {budget}" if budget else ""
            notes_str = f"\n\nNotes: {notes}" if notes else ""

            message = (
                f"Hi {name}! 👋 Thank you for visiting Inching India at the exhibition.\n\n"
                f"You were interested in: {interest_str}{budget_str}.\n\n"
                f"We'd love to share our latest collection with you. "
                f"Feel free to reach out anytime! 🌸{notes_str}"
            )

            import urllib.parse
            wa_url = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(message)}"

            st.success(f"✅ Captured: {name} ({phone})")

            if follow_up == "WhatsApp":
                st.markdown(f"### [📲 Open WhatsApp for {name}]({wa_url})")
                st.caption("Click the link above to open WhatsApp with the pre-filled message.")

            with st.expander("Preview WhatsApp message"):
                st.text(message)

            st.markdown("---")
            st.markdown(f"**Business WhatsApp:** [wa.me/{BUSINESS_WHATSAPP}](https://wa.me/{BUSINESS_WHATSAPP})")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Team Structure:**")
st.sidebar.markdown("• **Operations:** Mehak, Mandeep, Bharti")
st.sidebar.markdown("• **Production:** Simran, Ilias Master Ji") 
st.sidebar.markdown("• **Tech:** Prabhav")
