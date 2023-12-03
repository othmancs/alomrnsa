# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    second_validate = fields.Boolean(default=False, copy=False)
    custody_id = fields.Many2one(
        'hr.custody',
        string='Custody ref',
        readonly=True,
        copy=True
    )
    project_id = fields.Many2one('project.project')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.custody_id and not self.second_validate:
            self.second_validate = True
            if self.custody_id.state == 'to_approve':
                for line in self.move_ids_without_package:
                    custody_line = self.custody_id.property_ids.filtered(lambda l: l.product_id == line.product_id)
                    if all(l.quantity_done == 0 for l in self.move_ids_without_package):
                        custody_line.delivered += line.product_uom_qty
                    else:
                        custody_line.delivered += line.quantity_done

            elif self.custody_id.state == 'to_approve_return':
                for line in self.move_ids_without_package:
                    custody_line = self.custody_id.property_ids.filtered(lambda l: l.product_id == line.product_id)
                    if all(l.quantity_done == 0 for l in self.move_ids_without_package):
                        custody_line.returned += line.product_uom_qty
                    else:
                        custody_line.returned += line.quantity_done

            self.activity_done()
            self.custody_id.send_activity()

        return res

    def activity_done(self):
        activity_ids = self.env['mail.activity'].sudo().search([('res_id', '=', self.id)])
        if activity_ids:
            for act in activity_ids:
                act.action_done()

    def send_activity(self):
        # group to collect usesrs to create  custody transfers for send an activity for all of them
        stock_group = self.env['res.groups'].sudo().search([('name', '=', 'Custody Transfers Manager')])
        user_ids = []
        if stock_group.users:
            for user in stock_group.users:
                user_ids.append(user.id)
        # user_id = self.approve_user.id
        now = fields.datetime.now()
        date_deadline = now.date()
        activ_list = []
        for user_id in user_ids:
            if user_id and user_id != 'None':
                activity_id = self.sudo().activity_schedule(
                    'mail.mail_activity_data_todo', date_deadline,
                    note=_(
                        '<a>Task </a> for <a>Validate</a>') % (
                         ),
                    user_id=user_id,
                    res_id=self.id,

                    summary=_("PLZ deliver this custody for employee %s")% self.partner_id.name
                )
                activ_list.append(activity_id.id)
        [(4, 0, rec) for rec in activ_list]


    @api.onchange('move_ids_without_package')
    def onchange_move_lines(self):
        for line in self.move_ids_without_package:
            if line.serial_number:
                custody_line = self.env['custody.property'].search([('custody.name','=',self.origin),('product_id','=',line.product_id.id)])
                custody_line.serial_no = line.serial_number

class StockMove(models.Model):
    _inherit = 'stock.move'
    project_id = fields.Many2one('project.project')
