import pandas as pd
import streamlit as st
import os
from typing import Tuple, List, Dict

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

def process_returns_to_adjustment(returns_df: pd.DataFrame, mapping_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Process returns data to create inventory adjustment CSV"""
    
    # Create mapping dictionary from Item Name to SKU
    sku_mapping = {}
    for _, row in mapping_df.iterrows():
        item_name = row['Item Name']
        sku_code = row['Sku Code']
        sku_mapping[item_name] = sku_code
    
    adjustments = []
    errors = []
    ignored_returns = []
    
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
    
    adjustment_df = pd.DataFrame(adjustments)
    return adjustment_df, errors, ignored_returns

def generate_returns_inventory_adjustment():
    """Streamlit interface for generating inventory adjustment from returns"""
    
    st.title("📦 Returns Inventory Adjustment")
    
    st.markdown("Upload your returns sheet to add back items marked 'PUT IN STOCK AGAIN' to inventory.")
    
    returns_file = st.file_uploader("Upload Returns CSV", type=['csv'], key="returns")
    
    if returns_file:
        try:
            returns_df = pd.read_csv(returns_file)
            
            # Load static inventory mapping
            mapping_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inventory_mapping.csv')
            mapping_df = pd.read_csv(mapping_path)
            
            with st.expander("📋 Returns Data Preview"):
                st.dataframe(returns_df.head())
            
            if st.button("Generate Returns Adjustment", type="primary"):
                with st.spinner("Processing returns adjustments..."):
                    adjustment_df, errors, ignored_returns = process_returns_to_adjustment(returns_df, mapping_df)
                
                if not adjustment_df.empty:
                    st.success(f"✅ Generated {len(adjustment_df)} returns adjustments")
                    
                    if errors:
                        st.error("❌ Items not found in inventory:")
                        for error in errors:
                            st.write(f"• {error}")
                    
                    if ignored_returns:
                        st.warning("⚠️ Returns ignored (not marked 'PUT IN STOCK AGAIN'):")
                        for ignored in ignored_returns:
                            st.write(f"• {ignored}")
                    
                    st.subheader("📊 Returns Adjustments")
                    st.dataframe(adjustment_df)
                    
                    csv_data = adjustment_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Returns Adjustment CSV",
                        data=csv_data,
                        file_name="returns_inventory_adjustment.csv",
                        mime="text/csv"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Adjustments", len(adjustment_df))
                    with col2:
                        st.metric("Total Quantity", adjustment_df['Quantity'].sum())
                    with col3:
                        st.metric("Ignored Returns", len(ignored_returns))
                
                else:
                    st.error("❌ No valid adjustments could be generated.")
                    if errors:
                        for error in errors:
                            st.write(f"• {error}")
                    if ignored_returns:
                        st.warning("Returns ignored (not marked 'PUT IN STOCK AGAIN'):")
                        for ignored in ignored_returns:
                            st.write(f"• {ignored}")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    else:
        st.info("👆 Please upload returns CSV file to proceed")
