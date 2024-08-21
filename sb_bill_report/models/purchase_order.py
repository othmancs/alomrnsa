from odoo import models, fields, api

class InvoiceGenerator(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        invoice = super(InvoiceGenerator, self)._prepare_invoice()
        # Add the purchase name to the invoice
        invoice['purchase_name'] = self.name
        invoice['warehouse_name'] = self.picking_type_id.warehouse_id.name

        return invoice




