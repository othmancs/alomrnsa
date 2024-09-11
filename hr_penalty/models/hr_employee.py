# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_pen_reg_count(self):
        for pen_reg in self:
            pen_reg.pen_reg_count = len(pen_reg.pen_reg_ids)

    pen_reg_count = fields.Integer(
        compute="_compute_pen_reg_count", string="Penalty Register Count"
    )
    pen_reg_ids = fields.One2many(
        "hr.penalty.register", "employee_id", string="Penalty"
    )

    def view_penalty_register(self):
        """
        Redirects to the Penalty Register view in Odoo if penalty register IDs exist.

        :return: A dictionary containing information for redirecting to the Penalty Register view. It
        includes the type of action, name of the view, model, view modes, views to be displayed (tree
        and form), domain filter based on the penalty register IDs, and the context.
        """
        self.ensure_one()
        if self.pen_reg_ids:
            tree_view = self.env.ref("hr_penalty.view_hr_penalty_register_tree")
            form_view = self.env.ref("hr_penalty.view_hr_penalty_register_form")
            return {
                "type": "ir.actions.act_window",
                "name": _("Payment Register"),
                "res_model": "hr.penalty.register",
                "view_mode": "form",
                "views": [(tree_view.id, "tree"), (form_view.id, "form")],
                "domain": [("id", "in", self.pen_reg_ids.ids)],
                "context": self.env.context,
            }
