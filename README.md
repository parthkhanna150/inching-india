*Operations Team: Mehak, Mandeep, Bharti | Production Team: Simran, Ilias Master Ji | Tech Team: Prabhav*

---

## Daily Workflow Overview

### Morning
1. **Production Kickoff** - Extract unfulfillable orders and generate production requirements
2. **Task Assignment** - Distribute work to tailors based on requirements

### Throughout the Day
3. **Manufacturing** - Physical production of items
4. **Fulfillment** - Process and ship ready orders as inventory becomes available

### Twice Daily
5. **Inventory Updates** - Sync completed production with system inventory

### End of Day
6. **Final Processing** - Generate labels and invoices for remaining orders

---

## Team-Specific SOPs

### Production Team SOP

#### Morning - Production Kickoff
1. **Extract Data:** Navigate to **Orders** → **Unfulfillable**
2. **Export:** Download the sheet of all items currently short in inventory
3. **Process:** Use the Production Kickoff tool to generate DailyProductionRequirements.csv
4. **Task Allocation:** Break down quantities by SKU and distribute to the **Tailors**

#### Throughout the Day - Manufacturing
1. **Manufacturing:** Tailors work on assigned items based on production requirements
2. **Quality Control:** Verify finished pieces meet standards
3. **Count:** Track completed quantities by SKU

#### End of Day - Production Wrap-up
1. **Count:** Verify total finished pieces produced during the day
2. **Report:** Prepare clear list (SKU + Final Count) for inventory adjustment

#### Twice Daily - Daily Inventory Update
1. **File Prep:** Use production report to create Inventory Adjustment CSV using Daily Inventory Update process
2. **Generate Template:** Upload DailyProductionRequirements.csv to get template with SKU Code, Item Name, Quantity, Adjustment Type, Inventory Type columns
3. **Fill Template:** 
   * **Quantity:** Enter produced quantities (positive numbers)
   * **Adjustment Type:** Leave as ADD (default for production)
   * **Inventory Type:** Leave as GOOD_INVENTORY (default for production)
4. **Upload:** Navigate to **Tools** → **Imports** → **Inventory Adjustment**
   * Select **Update Existing** and upload the generated Uniware CSV
   * *Note: Once uploaded, fulfillable orders will automatically move to Operations Team's Shipping Panel*

---

### Operations Team SOP

#### Throughout the Day - Fulfillment

##### Regular Processing
1. **Monitor:** Check the **Shipping Panel** for orders that have moved to "Ready to Ship"
2. **Process:** Select orders (First-Come-First-Serve basis)
3. **Invoice & Label:** Use the **Top-Left Dropdown** to **Create Invoices**, then **Generate Labels**

##### Partial Fulfillment
1. **Identify:** Orders stuck in "Unfulfillable" but have some ready items
2. **Manual Split:** Go to **Order Details** → **Top-Left Dropdown** → **Create Manual Shipment**
3. **Select:** Choose only the "Good" items for shipment

#### One-time Process - Product Addition

##### Step 1: Create Shopify Products
- Create Shopify Products as normal (by duplicating from Shopify)
- *These products will get synced to Uniware (syncing happens every 15 minutes) as UNLINKED products*

##### Step 2: Add Products to Item Master
- Go to "Unlinked" tab in Uniware
- Filter on "Shopify" Channel
- Download this file and rename to **ShopifyNewProducts.csv**
- Go to Product Addition from the dropdown and use item-master-generator software to upload this file
- Click "Generate Uniware Items" and download the result (**UniwareNewItems.csv**)
- Go to Imports → Choose "Item Master" → "Create New and Update Existing" → Upload UniwareNewItems.csv
![Uniware Item Master Import Configuration](static/docs/uniware_item_master_import.png)

##### Step 3: Link Items to Shopify Products
- After the Import finishes, go to Product Addition from the dropdown and use uniware-shopify linker software
- Upload the **original ShopifyNewProducts.csv** file
- Click "Link New Products" and download the result (**NewLinks.csv**)
- Go to Imports → Choose "Channel Item Type" → "Create New and Update Existing" → Upload NewLinks.csv
![Uniware Channel Item Type Import Configuration](static/docs/uniware_channel_item_type_import.png)

##### Step 4: Update Inventory
- Items have been successfully uploaded and linked for inventory tracking
- **Important:** The inventory is zero for these new items
- Follow the **Production Team's Daily Inventory Update process** to update quantities

---

## Quick Reference

### Daily Timeline
| Time | Action | Team |
| :--- | :--- | :--- |
| **Morning** | Extract Unfulfillable List & Assign Tasks | Production |
| **Throughout Day** | Manufacturing & Production | Production |
| **Ongoing** | Process Ready Orders & Partial Fulfillment | Operations |
| **Twice Daily** | Update Inventory Adjustments | Production |
| **End of Day** | Generate Labels & Invoices | Operations |

### TODOs
- **Production:** Notes and Shopify Order number needed in unfulfillable sheet
- **Operations:** Invoicing algorithm for price breakdown, Partial CoD adjustment for partial shipments
- **Tech:** Script to prepare product/collection (item master) CSV to upload with all bundle-simple mappings as well as uniware-shopify linkings
