from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PartnerTaxMerge(models.TransientModel):
    _name = 'partner.tax.merge'
    _description = 'دمج جهات الاتصال حسب الرقم الضريبي'
    
    @api.model
    def _default_partner_ids(self):
        active_ids = self.env.context.get('active_ids', [])
        return [(6, 0, active_ids)]
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='جهات الاتصال',
        default=_default_partner_ids,
    )
    target_partner_id = fields.Many2one(
        'res.partner',
        string='جهة الاتصال الهدف',
        required=True,
    )
    
    @api.onchange('partner_ids')
    def _onchange_partner_ids(self):
        if self.partner_ids and len(self.partner_ids) > 0:
            self.target_partner_id = self.partner_ids[0]
    
    def action_merge(self):
        self.ensure_one()
        
        if len(self.partner_ids) < 2:
            raise UserError(_('يجب اختيار جهتي اتصال على الأقل للدمج'))
        
        vat_list = self.partner_ids.mapped('vat')
        if not all(vat == vat_list[0] for vat in vat_list):
            raise UserError(_('لا يمكن دمج جهات اتصال بأرقام ضريبية مختلفة'))
        
        self.env['res.partner']._merge(
            self.partner_ids.ids,
            self.target_partner_id
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
