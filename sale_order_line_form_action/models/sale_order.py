from odoo import _, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref(
            "sale_order_line_form_action.sale_order_line_view_form_editable"
        )
        return {
            "name": _("Sale Order Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
        }
