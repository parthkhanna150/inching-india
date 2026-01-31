import pandas as pd
import streamlit as st
import os
from typing import Tuple, Dict, List

def find_matching_sku(item_name: str, size: str, part_type: str, sku_mapping: Dict[str, str]) -> str:
    """Find matching SKU code based on item name, size, and part type"""
    # Try exact match first
    full_item_name = f"{item_name} - {part_type.title()} {size}"
    if full_item_name in sku_mapping:
        return sku_mapping[full_item_name]
    
    # Try partial matches
    for mapped_name, sku in sku_mapping.items():
        if (item_name.lower() in mapped_name.lower() and 
            size in mapped_name and 
            part_type.lower() in mapped_name.lower()):
            return sku
    
    return None

def process_production_returns_to_adjustment(production_df: pd.DataFrame, 
                                           returns_df: pd.DataFrame, 
                                           mapping_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Process production and returns data to create inventory adjustment CSV
    
    Args:
        production_df: DataFrame with columns [Date, NAME, top/bottom, Size, QTY]
        returns_df: DataFrame with columns [DATE, NAME, bottom/top/dupatta/potli, SIZE, QTY, notes]
        mapping_df: DataFrame with columns [Sku Code, Item Name, ...]
    
    Returns:
        Tuple of (adjustment_df, errors, ignored_returns)
    """
    
    # Create mapping dictionary from Item Name to SKU
    sku_mapping = {}
    for _, row in mapping_df.iterrows():
        item_name = row['Item Name']
        sku_code = row['Sku Code']
        sku_mapping[item_name] = sku_code
    
    adjustments = []
    errors = []
    ignored_returns = []
    
    # Process production data (ADD adjustments)
    for _, row in production_df.iterrows():
        if pd.notna(row['NAME']) and pd.notna(row['QTY']):
            item_name = row['NAME'].strip()
            size = row['Size']
            qty = int(row['QTY'])
            part_type = row['top/bottom'].upper()
            
            # Find matching SKU
            sku_code = find_matching_sku(item_name, size, part_type, sku_mapping)
            if sku_code:
                adjustments.append({
                    'SKU Code': sku_code,
                    'Item Name': f"{item_name} - {part_type.title()} {size}",
                    'Quantity': qty,
                    'Adjustment Type': 'ADD',
                    'Inventory Type': 'GOOD_INVENTORY'
                })
            else:
                errors.append(f"Item not found in inventory: {item_name} - {part_type} {size}")
    
    # Process returns data (ADD adjustments - only for "PUT IN STOCK AGAIN")
    for _, row in returns_df.iterrows():
        if pd.notna(row['NAME']) and pd.notna(row['QTY']) and row['NAME'].strip():
            item_name = row['NAME'].strip()
            size = row['SIZE']
            qty = int(row['QTY'])
            part_type = row['bottom/top/dupatta/potli'].upper()
            notes = str(row.get('notes', '')).strip()
            
            # Only process if notes contain "PUT IN STOCK AGAIN"
            if "PUT IN STOCK AGAIN" in notes.upper():
                # Find matching SKU
                sku_code = find_matching_sku(item_name, size, part_type, sku_mapping)
                if sku_code:
                    adjustments.append({
                        'SKU Code': sku_code,
                        'Item Name': f"{item_name} - {part_type.title()} {size}",
                        'Quantity': qty,
                        'Adjustment Type': 'ADD',
                        'Inventory Type': 'GOOD_INVENTORY'
                    })
                else:
                    errors.append(f"Item not found in inventory: {item_name} - {part_type} {size}")
            else:
                ignored_returns.append(f"{item_name} - {part_type.title()} {size} (Notes: {notes})")
    
    # Create output DataFrame
    adjustment_df = pd.DataFrame(adjustments)
    
    return adjustment_df, errors, ignored_returns

def generate_inventory_adjustment_from_production():
    """Streamlit interface for generating inventory adjustment from production and returns"""
    
    st.title("📦 Inventory Adjustment from Production & Returns")
    
    st.markdown("""
    Upload your production and returns sheets to generate a Uniware-compatible inventory adjustment CSV.
    """)
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Production Sheet")
        production_file = st.file_uploader(
            "Upload Production CSV", 
            type=['csv'],
            key="production"
        )
    
    with col2:
        st.subheader("Returns Sheet")
        returns_file = st.file_uploader(
            "Upload Returns CSV", 
            type=['csv'],
            key="returns"
        )
    
    if production_file and returns_file:
        try:
            # Read uploaded files
            production_df = pd.read_csv(production_file)
            returns_df = pd.read_csv(returns_file)
            
            # Load static inventory mapping
            mapping_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inventory_mapping.csv')
            mapping_df = pd.read_csv(mapping_path)
            
            # Display file previews
            with st.expander("📋 File Previews"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Production Data:**")
                    st.dataframe(production_df.head())
                
                with col2:
                    st.write("**Returns Data:**")
                    st.dataframe(returns_df.head())
            
            # Process the data
            if st.button("Generate Inventory Adjustment", type="primary"):
                with st.spinner("Processing inventory adjustments..."):
                    adjustment_df, errors, ignored_returns = process_production_returns_to_adjustment(
                        production_df, returns_df, mapping_df
                    )
                
                if not adjustment_df.empty:
                    st.success(f"✅ Generated {len(adjustment_df)} inventory adjustments")
                    
                    # Display errors if any
                    if errors:
                        st.error("❌ Items not found in inventory:")
                        for error in errors:
                            st.write(f"• {error}")
                    
                    # Display ignored returns
                    if ignored_returns:
                        st.warning("⚠️ Returns ignored (not marked 'PUT IN STOCK AGAIN'):")
                        for ignored in ignored_returns:
                            st.write(f"• {ignored}")
                    
                    # Display results
                    st.subheader("📊 Generated Adjustments")
                    st.dataframe(adjustment_df)
                    
                    # Download button
                    csv_data = adjustment_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Inventory Adjustment CSV",
                        data=csv_data,
                        file_name="inventory_adjustment_from_production.csv",
                        mime="text/csv"
                    )
                    
                    # Summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Adjustments", len(adjustment_df))
                    with col2:
                        st.metric("Total Quantity", adjustment_df['Quantity'].sum())
                    with col3:
                        st.metric("Errors", len(errors))
                    with col4:
                        st.metric("Ignored Returns", len(ignored_returns))
                
                else:
                    st.error("❌ No valid adjustments could be generated. Please check your data.")
                    if errors:
                        st.error("Items not found in inventory:")
                        for error in errors:
                            st.write(f"• {error}")
                    if ignored_returns:
                        st.warning("Returns ignored (not marked 'PUT IN STOCK AGAIN'):")
                        for ignored in ignored_returns:
                            st.write(f"• {ignored}")
        
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
    
    else:
        st.info("👆 Please upload both production and returns files to proceed")
