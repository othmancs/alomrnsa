# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)


from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rma_type_id = fields.Many2one("stock.picking.type", "RMA Type")

    def _get_sequence_values(self):
        res = super()._get_sequence_values()
        res.update(
            {
                "rma_type_id": {
                    "name": self.name + " " + _("Sequence RMAR"),
                    "prefix": "RMAR/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return res

    def _get_picking_type_update_values(self):
        res = super()._get_picking_type_update_values()
        res["rma_type_id"] = {
            "default_location_src_id": self.env["ir.model.data"]._xmlid_to_res_id(
                "stock.stock_location_customers"
            ),
            "default_location_dest_id": self.env["ir.model.data"]._xmlid_to_res_id(
                "sod_crm_claim.stock_location_RMA"
            ),
        }
        return res

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "rma_type_id": {
                    "name": _("Return to RMA"),
                    "code": "incoming",
                    "use_create_lots": True,
                    "use_existing_lots": True,
                    "default_location_src_id": self.env[
                        "ir.model.data"
                    ]._xmlid_to_res_id("stock.stock_location_customers"),
                    "default_location_dest_id": self.env[
                        "ir.model.data"
                    ]._xmlid_to_res_id("sod_crm_claim.stock_location_RMA"),
                    "sequence": next_sequence + 1,
                    "sequence_code": "RMA",
                },
            }
        )
        return data, max_sequence + 4
