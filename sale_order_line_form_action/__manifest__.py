{
    "name": "Sale Order Line Form Action",
    "summary": """
        Adds a button to open a sale order line in the form view.
    """,
    "author": "Mint System GmbH, Odoo Community Association (OCA)",
    "website": "https://www.mint-system.ch",
    "category": "Sales",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["views/sale_order.xml", "views/sale_order_line.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["images/screen.png"],
}
