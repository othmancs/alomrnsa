from odoo import models, fields, api

class MergeWizard(models.TransientModel):
    _name = 'merge.wizard'
    _description = 'معالج دمج السجلات'

    model_name = fields.Char(string='النموذج', default='res.partner')
    record_ids = fields.Many2many('res.partner', string='السجلات المراد دمجها')
    master_id = fields.Many2one('res.partner', string='السجل الرئيسي')
    fields_to_merge = fields.Many2many('ir.model.fields', 
        domain="[('model', '=', model_name)]",
        string='الحقول المطلوب دمجها')

    def action_merge(self):
        self.env['advanced.merge'].merge_records(
            self.model_name,
            self.record_ids.ids,
            self.master_id.id,
            self.fields_to_merge.mapped('name')
        )
        return {'type': 'ir.actions.act_window_close'}