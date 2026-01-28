# Daily Operations Standard Operating Procedure (SOP)
*System: Uniware | Team: Mehak, Mandeep, Ilias, Simran, Prabhav*

---

# Recurring Processes

## SOP: Operations (Mehak)
**Role:** Orchestrating the whole process.

### Production Kickoff
**Morning**

1. **Extract Data:** Navigate to **Orders** -> **Unfulfillable**.
2. **Export:** Download the sheet of all items currently short in inventory.
3. **Handoff:** Send this file to **Ilias** immediately to start the tailoring queue.

TODOs: Notes and Shopify Order number needed in this sheet.

## Processing & Partial Fulfillment. (Mandeep)
**Role:** Shipping management.

### Fulfillments
**Afternoon/Ongoing**

1. **Regular Processing:**
   * Go to the **Shipping Panel**.
   * Select orders that have moved to "Ready to Ship" (First-Come-First-Serve).
   * Use the **Top-Left Dropdown** to **Create Invoices**, then **Generate Labels**.
2. **Partial Fulfillment:**
   * **Before Shipping Panel:** If an order is stuck in "Unfulfillable" but has some ready items, go to **Order Details** -> **Top-Left Dropdown** -> **Create Manual Shipment**. Select only the "Good" items.

TODOs: Invoicing algorithm for price breakdown, Partial CoD adjustment for partial shipments.

---

## SOP: Production (Ilias)
**Role:** Physical Manufacturing & Tailor Management

### Task Allocation
**Morning**

1. **Review:** Open the Unfulfillable sheet provided by Mehak.
2. **Assign:** Break down quantities by SKU and distribute to the **Tailors**.

### Production Wrap-up
**Afternoon/Ongoing**

1. **Count:** Verify total finished pieces produced during the day.
2. **Handoff:** Send a clear list (SKU + Final Count) to **Simran**.

---

## SOP: Inventory Adjustment (Simran)
**Role:** System Reconciliation (Inventory Sync)

### Inventory Adjustment
**Twice a day - 11am and 3pm**

1. **File Prep:** Create an Inventory Adjustment CSV based on Ilias's report.
2. **Data Entry:**
   * **Increment:** Set `GOOD_INVENTORY` to the produced quantity (e.g., `10`).
   * **Decrement:** Set `VIRTUAL_INVENTORY` to the negative of that quantity (e.g., `-10`).
3. **Upload:** Navigate to **Tools** -> **Imports** -> **Inventory Adjustment**.
   * Select **Update Existing** and upload your file.
   * *Note: Once uploaded, fulfillable orders will automatically move to Mehak's Shipping Panel.*

TODOs: Script to prepare Inventory Adjustment CSV (excel file) which is straightforward to fill.

---

## Daily Workflow Summary

| Time | Action | Responsibility |
| :--- | :--- | :--- |
| **09:00 AM** | Export Unfulfillable List | Mehak |
| **10:00 AM** | Assign tasks to Tailors | Ilias |
| **Ongoing** | Partial/Manual Splits | Mehak |
| **04:00 PM** | Finalize Production List | Ilias |
| **04:30 PM** | Upload Inventory Adjustment | Simran |
| **End of Day** | Generate Labels & Invoices | Mehak |

---

# One-time Processes

## SOP: Add new Product/Collection (Mehak)
**Role:** Add new products in the system before following inventory adjustment

### Product Addition

1. Create Shopify Products as normal (by duplicating from Shopify). *These products will get synced to Uniware (syncing happens every 15minutes) as UNLINKED products.*
2. Add these unlinked products to our item master so we have them available in Uniware system.
  a. Go to "Unlinked" tab.
  b. Filter on "Shopify" Channel.
  c. Download this file (called ShopifyNewProducts.csv). These are the new shopify products whose inventory we don't track.
  d. Go to [item-master-generator software]() and upload this file.
  e. Click "Generate Uniware Items". Download the result (called UniwareNewItems.csv).
  f. Go to Imports. Choose "Item Master" from the first dropdown and "Create New and Update Existing" from the second dropdown. Upload the UniwareNewItems.csv.
3. Link the newly created Uniware Items to the Shopify products so that inventory tracking can be achieved.
  g. After the Import finishes, go to [uniware-shopify linker software]() and upload the **first file** ShopifyNewProducts.csv.
  h. Click "Link New Products". Download the result (NewLinks.csv).
  i. Go to Imports. Choose Channel Item Sync from the first dropdown, "Create New and Update Existing" from the second dropdown. Upload the NewLinks.csv.
Perfect! Items have been successfully uploaded and linked for inventory tracking. **However, the inventory is zero for these so follow the Inventory Adjustment SOP now to update the quantity.**


TODOs: Script to prepare product/collection (item master) CSV to upload with all bundle-simple mappings as well as uniware-shopify linkings.
