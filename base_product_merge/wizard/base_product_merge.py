# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from openupgradelib import openupgrade_merge_records

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseProductMerge(models.Model):
    _name = "base.product.merge"
    _description = "Merges two products"

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)
        ptype = active_model
        rec.update({"ptype": ptype})
        
        if ptype == "product.product":
            products = self.env[active_model].browse(active_ids)
            # Group products by default_code
            code_groups = defaultdict(list)
            for product in products:
                code_groups[product.default_code].append(product.id)
            
            # Select first product from each group as destination
            product_ids = []
            for code, ids in code_groups.items():
                product_ids.extend(ids)
            
            rec.update({
                "product_ids": [(6, 0, product_ids)],
                "auto_merge": len(code_groups) > 0,
            })
        else:
            product_templates = self.env[active_model].browse(active_ids)
            # Group templates by default_code
            code_groups = defaultdict(list)
            for template in product_templates:
                code_groups[template.default_code].append(template.id)
            
            # Select first template from each group as destination
            product_tmpl_ids = []
            for code, ids in code_groups.items():
                product_tmpl_ids.extend(ids)
            
            rec.update({
                "product_tmpl_ids": [(6, 0, product_tmpl_ids)],
                "auto_merge": len(code_groups) > 0,
            })
        return rec

    dst_product_id = fields.Many2one(
        "product.product", 
        string="Destination product",
        domain="[('id', 'in', product_ids)]"
    )
    product_ids = fields.Many2many(
        "product.product",
        "product_rel",
        "product_merge_id",
        "product_id",
        string="Products to merge",
    )
    ptype = fields.Selection(
        [("product.product", "Product"), ("product.template", "Template")]
    )
    dst_product_tmpl_id = fields.Many2one(
        "product.template", 
        string="Destination product template",
        domain="[('id', 'in', product_tmpl_ids)]"
    )
    product_tmpl_ids = fields.Many2many(
        "product.template",
        "product_tmpl_rel",
        "product_tmpl_merge_id",
        "product_tmpl_id",
        string="Products Template to merge",
    )
    merge_method = fields.Selection([("sql", "SQL"), ("orm", "ORM")], default="sql")
    auto_merge = fields.Boolean("Auto Merge by Reference", default=False)

    def action_merge(self):
        if self.auto_merge:
            return self.action_auto_merge()
        
        if self.ptype == "product.product":
            dst_product = self.dst_product_id
            products_to_merge = self.product_ids - dst_product
        else:
            dst_product = self.dst_product_tmpl_id
            products_to_merge = self.product_tmpl_ids - dst_product
            # merge product first when there is template with single product
            if not any(
                products_to_merge.product_variant_ids.mapped("combination_indices")
            ):
                dst_product_product = self.dst_product_tmpl_id.product_variant_id
                product_product_to_merge = (
                    self.product_tmpl_ids.product_variant_ids - dst_product_product
                )
                if not product_product_to_merge:
                    raise UserError(_("You cannot merge product to it self."))
                self.merge_products(
                    "product.product", product_product_to_merge, dst_product_product
                )
        self.merge_products(self.ptype, products_to_merge, dst_product)

    def action_auto_merge(self):
        if self.ptype == "product.product":
            # Group products by default_code
            code_groups = defaultdict(list)
            for product in self.product_ids:
                code_groups[product.default_code].append(product.id)
            
            # Merge each group
            for code, product_ids in code_groups.items():
                if len(product_ids) > 1:
                    dst_product = self.env["product.product"].browse(product_ids[0])
                    products_to_merge = self.env["product.product"].browse(product_ids[1:])
                    self.merge_products("product.product", products_to_merge, dst_product)
        else:
            # Group templates by default_code
            code_groups = defaultdict(list)
            for template in self.product_tmpl_ids:
                code_groups[template.default_code].append(template.id)
            
            # Merge each group
            for code, template_ids in code_groups.items():
                if len(template_ids) > 1:
                    dst_template = self.env["product.template"].browse(template_ids[0])
                    templates_to_merge = self.env["product.template"].browse(template_ids[1:])
                    
                    # merge product variants first if single variant templates
                    if not any(templates_to_merge.product_variant_ids.mapped("combination_indices")):
                        dst_product = dst_template.product_variant_id
                        products_to_merge = templates_to_merge.product_variant_ids - dst_product
                        if products_to_merge:
                            self.merge_products("product.product", products_to_merge, dst_product)
                    
                    self.merge_products("product.template", templates_to_merge, dst_template)
        
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Products merged successfully by internal reference."),
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            }
        }

    def merge_products(self, model, products_to_merge, dst_product):
        try:
            if not products_to_merge:
                return
            openupgrade_merge_records.merge_records(
                self.env,
                model,
                products_to_merge.ids,
                dst_product.id,
                method=self.merge_method,
            )
        except Exception as e:
            _logger.warning(e)
            raise UserError(_("Error occurred while merging products.")) from e
