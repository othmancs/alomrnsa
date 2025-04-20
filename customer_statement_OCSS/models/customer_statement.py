from odoo import models, fields, api

class CustomerStatement(models.Model):
    _name = 'customer.statement'
    _description = 'Customer Statement'

    # يمكنك إضافة حقول إضافية هنا إذا لزم الأمر
    # لكن التقرير يعتمد أساساً على نموذج account.move.line الموجود مسبقاً
    
    def get_customer_statement_data(self, partner_id, date_from, date_to, branch_id=False):
        """
        دالة مساعدة لاستخراج بيانات كشف الحساب
        """
        domain = [
            ('partner_id', '=', partner_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['receivable', 'payable']),
        ]
        
        if branch_id:
            domain.append(('branch_id', '=', branch_id))
            
        lines = self.env['account.move.line'].search(domain, order='date, move_id')
        return lines