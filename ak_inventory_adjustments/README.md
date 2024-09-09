# ak_inventory_adjustment 
Open ERP System :- Odoo 16e Version

Upload Attachment in the OGED Portal.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies
- Issues & Bugs
- Steps

Features & Limitations
======================
Inventory Adjustment For Managing Your Stock Effectively

Configuration
============
Ensure the Storage Location and Unit Of Measure boolean is set to true.

Usage
============
The Inventory Adjustment app offers Easily tweak and refine your inventory with simple, intuitive adjustments. Keep your
products in check and operations running smoothly with hassle-free inventory management.

## Dependencies

### Odoo modules dependencies

| Module           | Technical Name   | Why used?                       |
|------------------|------------------|---------------------------------|
| Web domain Field | web_domain_field | Used for dynamic domain feature |
 
### Python library dependencies

This module doesn't have any python dependencies 

Steps
============

* After installing the module, users will have access to the 'Interim Cycle Counting' menu under Inventory > Operations > Interim Cycle Counting.
* Users have the ability to create new inventory adjustments, define product categories, locations, and products. One can also set the Accounting Date and Counted Quantities. Once ready, the inventory process can be initiated using the 'Start Inventory' button.
* After initiating the inventory using the header button, it will display 'Continue Inventory'. Clicking on it will redirect the user to the quants.
* Afterward, one can update the counted quantity, input lot/serial numbers, or generate new quants as needed.
* After updating the counted quantity, one can validate the inventory by button 'Validate Inventory' either from the tree view or the form view of the inventory adjustment.
* When clicking the 'Validate Inventory' button, the status of the inventory adjustment changes to 'validated', and users can then access the 'Product Moves' smart button.
* Clicking on 'Product Moves' redirects to the product moves page, allowing users to view quantities, status, and transfer locations (from and to).
* One can also print count sheet of product moves.
* One can only cancel draft inventory adjustment.

16.0.1.0.0
============
This app is only valid in odoo version 16.0.1.0.0 community & enterprise
