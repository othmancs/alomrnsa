# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    def compute_delivery_state(self):
        for material_request in self:
            picking_recs = self.env["stock.picking"].search(
                [("request_id", "=", material_request.id)]
            )
            if picking_recs and all(
                picking.state in ["done", "cancel"] for picking in picking_recs
            ):
                material_request.delivery_state = "process"
            else:
                material_request.delivery_state = "pending"

    name = fields.Char(string="Reference", index=True, readonly=1)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("approve", "Approved"),
            ("reject", "Rejected"),
        ],
        track_visibility="onchange",
        default="draft",
    )
    user_id = fields.Many2one(
        "res.users",
        string="طلب من قبل",
        default=lambda self: self.env.user and self.env.user.id or False,
        required=True,
        domain=lambda self: [
            ("groups_id", "in", [self.env.ref("stock.group_stock_user").id])
        ],
    )
    branch_from_id = fields.Many2one(
        'res.branch',
        string='من فرع',
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)],
        default=lambda self: self.env.user.branch_id.id,
    )
    branch_to_id = fields.Many2one(
        'res.branch',
        string='الى فرع',
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)],
        default=lambda self: self.env.user.branch_id.id,
    )
    dest_location_id = fields.Many2one(
        "stock.location",
        string="من مستودع",
        copy=True,
        help="Location from where stock will be delivered.",
    )
    location_id = fields.Many2one(
        "stock.location",
        string="الى مستودع",
        copy=False,
        help="Stock needed on Location.",
    )
    request_date = fields.Date(string="تاريخ الطلب", default=datetime.now().date())
    request_line_ids = fields.One2many(
        "material.request.line", "request_id", string="Request", copy=True
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Picking Type",
        copy=False,
        default=lambda self: self.env["stock.picking.type"].search(
            [("code", "=", "internal")], limit=1
        ),
    )
    two_verify = fields.Boolean(string="2 Step Delivery(Via Transit Location)")
    delivery_state = fields.Selection(
        [("pending", "Transfer Pending"), ("process", "No Pending Transfers")],
        track_visibility="onchange",
        default="pending",
        compute="compute_delivery_state",
    )
    good_needed_on = fields.Datetime(string="تاريخ التوصيل")
    picking_count = fields.Integer(string="Picking Count", compute="compute_picking")
    picking_two_verify = fields.Boolean(string="Picking Two Verify")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    approved_user_id = fields.Many2one("res.users", copy=False, string="Approved By")

    @api.onchange('branch_from_id', )
    def _onchange_branch_from_id(self):
        """
        set domain in branch from
        """
        for rec in self:
            rec.dest_location_id = False
            if rec.branch_from_id:
                related_locations = self.env['stock.location'].search([
                    ('branch_id', '=', rec.branch_from_id.id),
                    ('usage', '=', 'internal')]
                )
                return {'domain': {'dest_location_id': [
                    ('id', 'in', related_locations.ids)
                ]}}
            # return {'domain': {'dest_location_id': [('id', '=', False)]}}

    @api.onchange('branch_to_id', )
    def _onchange_branch_to_id(self):
        """
        set domain in branch to
        """
        for rec in self:
            rec.location_id = False
            if rec.branch_to_id:
                related_locations = self.env['stock.location'].search([
                    ('branch_id', '=', rec.branch_to_id.id),
                    ('usage', '=', 'internal')]
                )
                return {'domain': {'location_id': [
                    ('id', 'in', related_locations.ids)
                ]}}
            # return {'domain': {'location_id': [('id', '=', False)]}}

    @api.constrains("dest_location_id")
    def check_dest_location(self):
        for material_req_rec in self:
            if material_req_rec.dest_location_id.id == material_req_rec.location_id.id:
                raise ValidationError(_("Please update Deliver Stock From Location."))

    def compute_picking(self):
        """These method is used for counting the
        Internal Transfer which is created from the material request."""
        for material_request_rec in self:
            material_request_rec.picking_count = self.env["stock.picking"].search_count(
                [("request_id", "=", material_request_rec.id)]
            )

    def action_reset_draft(self):
        for rec in self:
            rec.write({"state": "draft"})

    @api.onchange("company_id")
    def _onchange_2_step_delivery(self):
        for rec in self:
            if rec.company_id.two_step_material_req:
                rec.picking_two_verify = True

    def action_confirm(self):
        for rec in self:
            rec.write({"state": "confirm"})

    def _prepare_pick_vals(self, req_line=False, picking=False):
        """This method is used to create stock moves from picking."""
        pick_vals = {
            "product_id": req_line.product_id.id,
            "product_uom_qty": req_line.qty,
            "product_uom": req_line.uom_id.id,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "picking_type_id": picking.picking_type_id.id,
            "picking_id": picking.id,
            "name": req_line.product_id.display_name,
        }
        return pick_vals

    def action_approve(self):
        """This method is used to create Internal Transfer."""
        stock_move_obj = self.env["stock.move"]
        for material_req_rec in self:
            if not material_req_rec.dest_location_id:
                raise ValidationError(
                    _(
                        "Please select the location from which you want to transfer the Stock."
                    )
                )

            if not material_req_rec.request_line_ids:
                raise ValidationError(_("Please create some requisition lines."))

            scheduled_date = False
            picking_vals = {
                "picking_type_id": material_req_rec.picking_type_id.id,
                "partner_id": material_req_rec.user_id.partner_id.id,
                "request_id": material_req_rec.id,
                "origin": material_req_rec.name,
                "location_id": material_req_rec.dest_location_id.id,
            }
            if material_req_rec.two_verify:
                # Picking create for two step.
                transit_location = self.env["stock.location"].search(
                    [("usage", "=", "transit")], limit=1
                )
                if not transit_location:
                    return {
                        "type": "ir.actions.act_window",
                        "name": "No Transit Location Warning",
                        "view_mode": "form",
                        "res_model": "transit.location.warning",
                        "context": {
                            "default_name": "No active Tranisit Location found in the system. Please contact the Inventory manager to Unarchive the Transit Location."
                        },
                        "target": "new",
                    }
                picking_vals.update({"location_dest_id": transit_location.id})
            else:
                picking_vals.update(
                    {"location_dest_id": material_req_rec.location_id.id}
                )
            # Created Main picking.
            main_picking_rec = self.env["stock.picking"].create(picking_vals)

            if material_req_rec.good_needed_on:
                scheduled_date = material_req_rec.good_needed_on

            if material_req_rec.two_verify:
                two_step_picking_rec = self.env["stock.picking"].create(
                    {
                        "location_id": transit_location.id,
                        "partner_id": material_req_rec.user_id.partner_id.id,
                        "location_dest_id": material_req_rec.location_id.id,
                        "picking_type_id": material_req_rec.picking_type_id.id,
                        "request_id": material_req_rec.id,
                        "origin": material_req_rec.name,
                    }
                )

            for req_line in material_req_rec.request_line_ids:
                stock_move_vals = material_req_rec._prepare_pick_vals(
                    req_line, main_picking_rec
                )
                first_move_rec = stock_move_obj.create(stock_move_vals)
                main_picking_rec.action_confirm()
                if material_req_rec.two_verify:
                    two_verify_stock_move_vals = material_req_rec._prepare_pick_vals(
                        req_line, two_step_picking_rec
                    )
                    two_verify_stock_move_vals.update(
                        {"move_orig_ids": [(6, 0, first_move_rec.ids)]}
                    )
                    stock_move_obj.create(two_verify_stock_move_vals)
                    two_step_picking_rec.action_confirm()
            material_req_rec.write({"state": "approve"})

    def action_reject(self):
        action = self.env.ref(
            "ak_material_request.action_reject_material_request_wizard"
        ).read()[0]
        action["context"] = {"default_material_request_id": self.id}
        return action

    @api.model
    def create(self, vals):
        """seqeunce is created for material request."""
        name = self.env["ir.sequence"].next_by_code("material.request.seq")
        vals.update({"name": name})
        res = super(MaterialRequest, self).create(vals)
        return res

    def show_picking(self):
        """Redirects to the stock picking view."""
        for rec in self:
            res = self.env.ref("stock.action_picking_tree_all")
            res = res.read()[0]
            res["domain"] = str([("request_id", "=", rec.id)])
        return res

    def unlink(self):
        for rec in self:
            if rec.state not in ["draft", "reject"]:
                raise UserError(
                    _("This record can be deleted only in Draft or Rejected state.")
                )
        return super(MaterialRequest, self).unlink()
