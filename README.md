# Uniware Item Generation Scripts

This repository contains Python scripts for generating Uniware-compatible item master data and channel linking files from Shopify product exports.

## Scripts Overview

### 1. Item Master Generator (`item_master_generator.py`)
Generates SIMPLE and BUNDLE items for Uniware item master import.

### 2. Uniware-Shopify Linker (`uniware_shopify_linker.py`)
Creates channel item type mappings to link Shopify products with Uniware SKUs.

## Standard Operating Procedure (SOP)

### Prerequisites
- Python 3.6+
- Shopify product export CSV file
- Products must be from SHOPIFY channel only

### Step-by-Step Process

1. **Export Shopify Products**
   ```bash
   # Ensure your CSV contains these required columns:
   # - Product Name on Channel
   # - Channel Product Id  
   # - channelName
   # - Seller SKU on Channel (optional)
   ```

2. **Generate Item Master Data**
   ```bash
   cd /path/to/inching-india/src/uniware
   python3 item_master_generator.py /path/to/shopify_export.csv
   ```
   
   **Outputs:**
   - `generated_output/generated_simple_items.csv` - SIMPLE items only
   - `generated_output/generated_bundle_items.csv` - BUNDLE items only  
   - `generated_output/populated_item_master.csv` - Combined file (SIMPLE first, then BUNDLE)

3. **Generate Channel Linking Data**
   ```bash
   python3 uniware_shopify_linker.py /path/to/shopify_export.csv
   ```
   
   **Output:**
   - `generated_output/populated_channel_item_type.csv` - Channel item mappings

4. **Import to Uniware**
   - Import `populated_item_master.csv` to Uniware Item Master
   - Import `populated_channel_item_type.csv` to Uniware Channel Item Type

## Script Features

### Core Features
- **SKU Generation**: Creates unique, compliant SKU codes (≤45 characters)
- **Product Parsing**: Extracts components from product names (TOP, BOTTOM, accessories)
- **Bundle Creation**: Generates BUNDLE items that reference SIMPLE components
- **Channel Filtering**: Only processes SHOPIFY channel products
- **Character Sanitization**: Ensures SKU codes only contain valid characters (alphanumeric, _, -, ., /)

### Advanced Features
- **Variant Truncation**: Truncates long variants to 4 characters (KURTA→KURT, PALAZZO→PALA)
- **Accessory Handling**: Treats any "WITH/WITHOUT" as accessories
- **Inventory Logic**: Only creates inventory for physical items (skips "WITHOUT" accessories)
- **Field Compliance**: Sets required empty fields per Uniware specifications
- **Error Reporting**: Detailed error messages for problematic products

### Data Processing Rules
- **SIMPLE Items**: Individual components (TOP, BOTTOM, accessories)
- **BUNDLE Items**: Collections that reference SIMPLE items
- **Ordering**: SIMPLE items always come before BUNDLE items in output
- **Dependencies**: BUNDLE items only reference existing SIMPLE items

## Guardrails & Validation

### Input Validation
✅ **Valid Input Requirements:**
- CSV file with required columns
- Products from SHOPIFY channel only
- Channel Product Id format: `PREFIX-PRODUCTCODE`
- Product names with proper component structure

❌ **Invalid Input Handling:**
- Non-SHOPIFY channels → Skipped with logging
- Missing required fields → Error logged, row skipped
- Invalid product ID format → Error logged, row skipped
- Products with zero physical components → Skipped
- Malformed product names → Error logged, row skipped

### SKU Code Guardrails
- **Length Limit**: Maximum 45 characters
- **Character Set**: Only alphanumeric, `_`, `-`, `.`, `/`
- **Uniqueness**: Each SKU is unique within the output
- **Format**: `{PRODUCTBASE}_{VARIANT}` structure

### Business Logic Guardrails
- **Physical Inventory Only**: No inventory items for "WITHOUT" accessories
- **Bundle Integrity**: BUNDLE items only reference existing SIMPLE items
- **Channel Consistency**: 100% match between channel and item master files

## Input Format Examples

### Valid Product Name Formats

```csv
Product Name on Channel,Channel Product Id,channelName
"Anarkali Set - KURTA / PALAZZO / WITH DUPATTA",SHOP-12345678901234,SHOPIFY
"Green Velvet Suit - XXXL / XXL / WITH EMBROIDERED DUPATTA",SHOP-98765432109876,SHOPIFY
"Simple Kurta - XL",SHOP-11111111111111,SHOPIFY
"Standalone Product",SHOP-22222222222222,SHOPIFY
"Test Set - KURTA / PALAZZO / WITHOUT POTLI",SHOP-33333333333333,SHOPIFY
```

### Invalid Examples (Will be skipped/error)

```csv
# Wrong channel
"Product Name",SHOP-12345,AMAZON

# Missing required fields  
"",SHOP-12345,SHOPIFY

# Invalid product ID format
"Product Name",INVALID-FORMAT,SHOPIFY

# Only non-physical accessories
"Product - WITHOUT DUPATTA",SHOP-12345,SHOPIFY
```

## Output Examples

### SIMPLE Items Generated
```csv
Category Code*,Product Code*,Name*,Type,Tax Calculation Type,Resync Inventory,Min Order Size
Clothing,12345678901234_TOP_KURTA,Anarkali Set - Top KURTA,SIMPLE,,,
Clothing,12345678901234_BOTTOM_PALAZZO,Anarkali Set - Bottom PALAZZO,SIMPLE,,,
Clothing,12345678901234_WITH_ACCESSORY_TRUE,Anarkali Set - With_Accessory TRUE,SIMPLE,,,
```

### BUNDLE Items Generated
```csv
Category Code*,Product Code*,Name*,Type,Scan Type,Component Product Code,Component Quantity
Clothing,12345678901234_KURT_PALA_WITH,Bundle Anarkali Set - KURTA / PALAZZO / WITH DUPATTA,BUNDLE,SIMPLE,12345678901234_TOP_KURTA,1
Clothing,12345678901234_KURT_PALA_WITH,Bundle Anarkali Set - KURTA / PALAZZO / WITH DUPATTA,BUNDLE,SIMPLE,12345678901234_BOTTOM_PALAZZO,1
Clothing,12345678901234_KURT_PALA_WITH,Bundle Anarkali Set - KURTA / PALAZZO / WITH DUPATTA,BUNDLE,SIMPLE,12345678901234_WITH_ACCESSORY_TRUE,1
```

### Channel Items Generated
```csv
Channel Name*,Channel Product Id*,Seller SKU Code*,Uniware SKU Code
SHOPIFY,SHOP-12345678901234,SHOP-12345678901234,12345678901234_KURT_PALA_WITH
```

## Error Handling & Logging

### Console Output Examples
```
Skipped 150 products from other channels:
  AMAZON: 75 products
  MYNTRA: 50 products
  FLIPKART: 25 products

Encountered 3 errors:
  Row 45: Missing required fields
  Row 67: Invalid channel product id format 'INVALID-FORMAT'
  Row 89: No physical components found in 'Product - WITHOUT DUPATTA' - skipping

Generated /path/to/generated_output/populated_item_master.csv
Generated /path/to/generated_output/populated_channel_item_type.csv
```

## Testing

### Run Unit Tests
```bash
cd tst/uniware
python3 test_item_master_generator.py
python3 test_uniware_shopify_linker.py
```

### Test Coverage
- Product name parsing (various formats)
- SKU generation and sanitization
- Variant truncation (4-character limit)
- Channel filtering (SHOPIFY only)
- Item ordering (SIMPLE before BUNDLE)
- Accessory handling (WITH/WITHOUT logic)
- Error handling and edge cases

## File Structure
```
src/
├── common/
│   └── uniware_utils.py           # Shared utilities
└── uniware/
    ├── item_master_generator.py   # Main item generation
    ├── uniware_shopify_linker.py  # Channel linking
    └── generated_output/          # Output directory
        ├── populated_item_master.csv
        └── populated_channel_item_type.csv

tst/
└── uniware/
    ├── test_item_master_generator.py
    └── test_uniware_shopify_linker.py
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'uniware_utils'"**
- Ensure you're running from the correct directory
- Scripts use absolute path resolution and should work from any directory

**"No components found in product name"**
- Check product name format: should be `"Base Name - Component1 / Component2"`
- Single products without variants are supported

**"SKU collisions or duplicate codes"**
- Usually caused by products from non-SHOPIFY channels
- Ensure input only contains SHOPIFY products

**"Missing BUNDLE items in item master"**
- Check if products have only "WITHOUT" accessories (zero physical components)
- These are correctly skipped as they have no inventory to track

### Performance Notes
- Processing ~26,000 products takes ~10-15 seconds
- Output files are typically 50MB-100MB
- Memory usage scales linearly with input size

## Version History
- **v2.0**: Added channel filtering, enhanced SKU generation, improved test coverage
- **v1.0**: Initial implementation with basic product parsing and item generation
