# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # totals = json.loads(self.tax_totals_json)
        # if totals.get('amount_total', 0) == 0:
        #     raise ValidationError("The Sales Order and all its Lines must have value bigger than Zero.")
        for line in self.order_line:
            if line.price_unit == 0:
                # raise ValidationError("The Sales Order and all its Lines must have value bigger than Zero.")
                raise ValidationError("You can not confirm a Sales Order with Unit Price equal to Zero!")
        res = super(SalesOrder, self).action_confirm()
        return res