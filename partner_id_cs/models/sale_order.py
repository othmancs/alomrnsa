from odoo import models, api
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)

        # إذا كان المستخدم لديه المجموعة المحددة، اجعل الحقل غير قابل للإنشاء
        if self.env.user.has_group('restrict_partner_creation_sale.group_restrict_partner_creation_sale_order'):
            doc = etree.XML(res['arch'])
            for field in doc.xpath("//field[@name='partner_id']"):
                field.set('options', '{"no_create": True}')
            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res
