# # -*- coding: utf-8 -*-

# from odoo import fields, models


# class AccountingCommonPartnerReport(models.TransientModel):
#     _name = 'account.common.partner.report'
#     _inherit = "account.common.report"
#     _description = 'Account Common Partner Report'

#     result_selection = fields.Selection([('customer', 'Receivable Accounts'),
#                                          ('supplier', 'Payable Accounts'),
#                                          ('customer_supplier', 'Receivable and Payable Accounts')
#                                          ], string="Partner's", required=True, default='customer')
#     partner_ids = fields.Many2many('res.partner', string='Partners')

#     def pre_print_report(self, data):
#         data['form'].update(self.read(['result_selection'])[0])
#         data['form'].update({'partner_ids': self.partner_ids.ids})
#         return data
# # -*- coding: utf-8 -*-

from odoo import fields, models


class AccountingCommonPartnerReport(models.TransientModel):
    _name = 'account.common.partner.report'
    _inherit = "account.common.report"
    _description = 'Account Common Partner Report'

    # إضافة خيارات المدين والدائن معاً
    result_selection = fields.Selection([
        ('customer', 'Receivable Accounts'),
        ('supplier', 'Payable Accounts'),
        ('customer_supplier', 'كل الحسابات')
    ], string="Partner's", required=True, default='customer')
    
    partner_ids = fields.Many2many('res.partner', string='Partners')

    def pre_print_report(self, data):
        """
        تجهيز البيانات لطباعة التقرير بناءً على الإختيار.
        """
        # تحديث البيانات بناءً على الاختيار الحالي
        data['form'].update(self.read(['result_selection'])[0])
        data['form'].update({'partner_ids': self.partner_ids.ids})

        # منطق خاص لإضافة خيار "Receivable and Payable Accounts"
        if data['form']['result_selection'] == 'customer_supplier':
            data['form']['include_customer_supplier'] = True
        else:
            data['form']['include_customer_supplier'] = False
        
        return data
