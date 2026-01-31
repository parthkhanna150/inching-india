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

def process_production_to_adjustment(production_df: pd.DataFrame, mapping_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Process production data to create inventory adjustment CSV"""
    
    # Create mapping dictionary from Item Name to SKU
    sku_mapping = {}
    for _, row in mapping_df.iterrows():
        item_name = row['Item Name']
        sku_code = row['Sku Code']
        sku_mapping[item_name] = sku_code
    
    adjustments = []
    errors = []
    
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
    
    adjustment_df = pd.DataFrame(adjustments)
    return adjustment_df, errors

def generate_production_inventory_adjustment():
    """Streamlit interface for generating inventory adjustment from production"""
    
    st.title("🏭 Production Inventory Adjustment")
    
    st.markdown("Upload your production sheet to generate inventory adjustments for newly produced items.")
    
    production_file = st.file_uploader("Upload Production CSV", type=['csv'], key="production")
    
    if production_file:
        try:
            production_df = pd.read_csv(production_file)
            
            # Load static inventory mapping
            mapping_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inventory_mapping.csv')
            mapping_df = pd.read_csv(mapping_path)
            
            with st.expander("📋 Production Data Preview"):
                st.dataframe(production_df.head())
            
            if st.button("Generate Production Adjustment", type="primary"):
                with st.spinner("Processing production adjustments..."):
                    adjustment_df, errors = process_production_to_adjustment(production_df, mapping_df)
                
                if not adjustment_df.empty:
                    st.success(f"✅ Generated {len(adjustment_df)} production adjustments")
                    
                    if errors:
                        st.error("❌ Items not found in inventory:")
                        for error in errors:
                            st.write(f"• {error}")
                    
                    st.subheader("📊 Production Adjustments")
                    st.dataframe(adjustment_df)
                    
                    csv_data = adjustment_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Production Adjustment CSV",
                        data=csv_data,
                        file_name="production_inventory_adjustment.csv",
                        mime="text/csv"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Adjustments", len(adjustment_df))
                    with col2:
                        st.metric("Total Quantity", adjustment_df['Quantity'].sum())
                
                else:
                    st.error("❌ No valid adjustments could be generated.")
                    if errors:
                        for error in errors:
                            st.write(f"• {error}")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    else:
        st.info("👆 Please upload production CSV file to proceed")
