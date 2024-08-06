from odoo import models, fields, api,_
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_method = fields.Selection([("fixed", "Fixed"), ("percentage", "Percentage")], string="Discount Method")
    discount_amount = fields.Float(string="Discount Amount")
    total_discount = fields.Float(string="- Discount")

    @api.onchange("discount_method", "discount_amount", "amount_untaxed")
    def onchange_on_total_discount(self):
        if self.state in ["draft", "sale"]:
            if self.discount_amount and self.discount_method:
                if self.amount_untaxed:
                    if self.discount_method == "fixed":
                        amount = self.discount_amount
                        self.total_discount = amount
                    else:
                        amount = round((self.discount_amount * self.amount_untaxed) / 100, 2)
                        self.total_discount = amount
                    self.amount_total = (self.amount_untaxed + self.amount_tax) - amount
                else:
                    self.total_discount = 0.0
            else:
                self.total_discount = 0.0

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.state == "draft":
            if vals.get("total_discount") or vals.get("order_line"):
                self.amount_total = (self.amount_untaxed + self.amount_tax) - self.total_discount
        elif self.state == "sale":
            if vals.get("order_line"):
                self.amount_total = (self.amount_untaxed + self.amount_tax) - self.total_discount

        if self.discount_method == 'fixed':
            if self.discount_amount > self.amount_total:
                raise UserError(_('You can not add more then amount in fix rate'))
        if self.discount_method == 'percentage':
            if self.discount_amount > 100 or  self.discount_amount < 0:
                raise UserError(_('You can not add value less then 0 and grater then 100'))

        return res

    @api.depends('order_line.price_total')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        for rec in self:
            if rec.amount_total:
                rec.amount_total = rec.amount_total - rec.total_discount
        return res

