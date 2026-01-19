# Inching India Inventory Management

This repository contains scripts for managing inventory and processing data from various platforms.

## Project Structure

```
inching-india/
├── src/                                  # Source code
│   ├── uniware/                          # Uniware-specific scripts
│   │   └── shopify_items_generator.py    # Convert Shopify products to items
│   ├── shopify/                          # Shopify-specific scripts
│   └── common/                           # Shared utilities
├── tst/                                  # Tests
│   ├── uniware/
│   │   └── test_shopify_items_generator.py
│   ├── shopify/
│   └── common/
├── data/                                 # Input data files
└── docs/                                 # Documentation
```

## Scripts

### Uniware Scripts

#### Shopify Items Generator

**Location:** `src/uniware/shopify_items_generator.py`

Converts Shopify fetched products into SIMPLE and BUNDLE items for Uniware inventory management.

**Usage:**
```bash
cd src/uniware/
python3 shopify_items_generator.py <shopify_products_file>
```

**Example:**
```bash
python3 shopify_items_generator.py ../../data/shopify_fetched_products.csv
```

**Output:**
- `generated_output/generated_simple_items.csv` - Individual components (TOP, BOTTOM, WITH_POTLI)
- `generated_output/generated_bundle_items.csv` - Bundle items containing all components

**Product Name Format:**
- Input: `Aafreen Wine Velvet Suit - XL / S / With Potli`
- Creates: TOP_XL, BOTTOM_S, WITH_POTLI_TRUE items
- Bundle: `47107397746906_XL_S_WITH_POTLI`

## Testing

Run tests for specific modules:

```bash
# Uniware tests
cd tst/uniware/
python3 test_shopify_items_generator.py

# Or run all tests with pytest
python3 -m pytest tst/ -v
```

## Development Guidelines

1. **Source Code**: All source code goes in `src/` organized by platform/service
2. **Tests**: All tests go in `tst/` mirroring the `src/` structure
3. **Generated Files**: Scripts create `generated_output/` directories (gitignored)
4. **Common Code**: Shared utilities go in `src/common/`
5. **Data Files**: Input data files should be placed in the `data/` directory

## Adding New Scripts

1. Create source file in appropriate `src/` subdirectory
2. Create corresponding test file in `tst/` subdirectory
3. Update this README with usage instructions
4. Add any generated output directories to `.gitignore`
