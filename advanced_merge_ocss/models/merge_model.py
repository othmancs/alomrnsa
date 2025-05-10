from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdvancedMerge(models.Model):
    _name = 'advanced.merge'
    _description = 'أداة الدمج المتقدم'

    def merge_records(self, model_name, record_ids, master_id, fields_to_merge):
        """
        نسخة محسنة مع معالجة الأخطاء والعلاقات
        """
        if not record_ids or len(record_ids) < 2:
            raise UserError(_("يجب تحديد سجلين على الأقل للدمج"))

        Model = self.env[model_name]

        # التحقق من الصلاحيات
        if not Model.check_access_rights('write') or not Model.check_access_rights('unlink'):
            raise UserError(_("ليس لديك صلاحية للدمج"))

        master_record = Model.browse(master_id)
        other_records = Model.browse(record_ids).filtered(lambda r: r.id != master_id)

        for record in other_records:
            # معالجة الحقول العادية
            for field in fields_to_merge:
                if field in Model._fields:
                    field_type = Model._fields[field].type
                    if field_type in ['char', 'text', 'boolean', 'integer', 'float', 'date', 'datetime']:
                        if not master_record[field] and record[field]:
                            master_record[field] = record[field]
                    elif field_type == 'many2one':
                        if not master_record[field] and record[field]:
                            master_record[field] = record[field].id
                    elif field_type in ['many2many', 'one2many']:
                        master_record[field] |= record[field]

            # حذف السجل مع التعامل مع الأخطاء
            try:
                record.unlink()
            except Exception as e:
                raise UserError(_("خطأ في حذف السجل %s: %s") % (record.display_name, str(e)))

        # تسجيل العملية
        self.env['ir.logging'].create({
            'name': 'دمج السجلات',
            'type': 'server',
            'dbname': self._cr.dbname,
            'level': 'info',
            'message': f'تم دمج {len(other_records)} سجلات في {master_record.display_name}',
            'path': 'advanced_merge',
            'line': 'merge_records',
        })

        return master_record


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_merge_wizard(self):
        if not self.env.context.get('active_ids') or len(self.env.context.get('active_ids', [])) < 2:
            raise UserError(_("يجب تحديد سجلين على الأقل للدمج"))

        return {
            'name': 'دمج متقدم',
            'type': 'ir.actions.act_window',
            'res_model': 'merge.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_record_ids': self.env.context.get('active_ids'),
                'default_model_name': 'res.partner',
            }
        }