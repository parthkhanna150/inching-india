# Inching India Inventory Management

This repository contains scripts for managing inventory and processing Shopify product data.

## Scripts

### Shopify Items Generator

**Location:** `inventory-management-scripts/shopify_items_generator.py`

Converts Shopify fetched products into SIMPLE and BUNDLE items for inventory management.

**Usage:**
```bash
cd inventory-management-scripts/
python3 shopify_items_generator.py <shopify_products_file>
```

**Example:**
```bash
python3 shopify_items_generator.py ../shopify_fetched_products.csv
```

**Output:**
- `generated_output/generated_simple_items.csv` - Individual components (TOP, BOTTOM, WITH_POTLI)
- `generated_output/generated_bundle_items.csv` - Bundle items containing all components

**Product Name Format:**
- Input: `Aafreen Wine Velvet Suit - XL / S / With Potli`
- Creates: TOP_XL, BOTTOM_S, WITH_POTLI_TRUE items
- Bundle: `47107397746906_XL_S_WITH_POTLI`

### Testing

Run unit tests:
```bash
cd inventory-management-scripts/
python3 test_shopify_items_generator.py
```

## File Structure

```
inching-india/
├── shopify_fetched_products.csv          # Input data from Shopify
├── inventory-management-scripts/
│   ├── shopify_items_generator.py        # Main script
│   ├── test_shopify_items_generator.py   # Unit tests
│   └── generated_output/                 # Generated CSV files (gitignored)
└── README.md
```
