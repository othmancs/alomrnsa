from odoo import models, api, _
from odoo.exceptions import ValidationError

class PartnerMerge(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    @api.model
    def _get_merge_action(self, partner_ids):
        """تجاوز كامل لإزالة القيود"""
        if len(partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل"))
        return {
            'name': _('Merge Partners'),
            'view_mode': 'form',
            'res_model': 'base.partner.merge.automatic.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, partner_ids)],
                'default_max_merge': float('inf')  # إزالة الحد الأقصى
            }
        }

    def action_merge(self):
        """تجاوز دالة الدمج الرئيسية"""
        if len(self.partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل"))
        return super().action_merge()
