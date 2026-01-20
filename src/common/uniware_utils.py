import re

def sanitize_sku(sku):
    """Sanitize SKU to only contain alphanumeric, _, -, ., /"""
    return re.sub(r'[^a-zA-Z0-9_\-./]', '_', sku)

def generate_bundle_variant(components):
    """Generate bundle variant from components with 4-char truncation"""
    variant_parts = []
    for comp_type, comp_value in components:
        if comp_type in ['TOP', 'BOTTOM']:
            variant_parts.append(comp_value[:4].upper())
        else:  # Accessory
            if comp_value == 'TRUE':
                variant_parts.append('WITH')
            else:
                variant_parts.append('WITHOUT')
    return '_'.join(variant_parts)

def parse_product_name(product_name):
    """Extract components from product name after hyphen"""
    if ' - ' not in product_name:
        # Single product with no variants - treat as single TOP component
        return [('TOP', product_name)]
    
    parts = product_name.split(' - ', 1)[1].split(' / ')
    components = []
    
    for part in parts:
        part = part.strip()
        part_upper = part.upper()
        
        # Check if it's an accessory with/without prefix
        is_accessory = False
        has_accessory = None
        
        if part_upper.startswith('WITHOUT'):
            is_accessory = True
            has_accessory = False
        elif part_upper.startswith('WITH'):
            is_accessory = True
            has_accessory = True
        
        if is_accessory:
            components.append(('WITH_ACCESSORY', 'TRUE' if has_accessory else 'FALSE'))
        else:
            # First non-accessory is TOP, second is BOTTOM
            if not any(comp[0] == 'TOP' for comp in components):
                components.append(('TOP', part))
            else:
                components.append(('BOTTOM', part))
    
    return components
