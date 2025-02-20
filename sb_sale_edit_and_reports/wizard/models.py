from odoo import models, fields, api

class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'sales report wizard'

    date_start = fields.Date(string="تاريخ البداية", required=True)
    date_end = fields.Date(string="تاريخ النهاية", required=True)
    branch_ids = fields.Many2many('res.branch', string="الفروع")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)
    payment_type = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string="نوع الدفع")  # تأكد من ترقية الوحدة لإنشاء عمود هذا الحقل في قاعدة البيانات

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_sales_export_xlsx(self):
        return self.env.ref("sb_sale_edit_and_reports.report_sales_report").report_action(self)

    def generate_pdf_report(self):
        # بناء نطاق البحث باستخدام القيم الموجودة في الـ wizard
        domain = [
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        # إذا كان لديك حقل الدفع على الفاتورة (مثلاً payment_state) فاستخدمه في التصفية
        if self.payment_type:
            domain.append(('payment_state', '=', self.payment_type))

        lines_data = self.env['account.move'].search(domain)
        existing_branches = lines_data.mapped('branch_id')

        report_data = []
        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]

        for branch in existing_branches:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
            total_out_refund_purchase_price = 0.0
            total_out_refund_price = 0.0

            for line in current_branch_lines:
                out_refund_price = self.env['account.move'].search([
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('reversed_entry_id', '=', line.id),
                    ('state', '=', 'posted')
                ])
                total_out_refund_price += sum(out_refund_price.line_ids.mapped(lambda x: x.price_unit * x.quantity))
                total_out_refund_purchase_price += sum(out_refund_price.line_ids.mapped(lambda x: x.purchase_price * x.quantity))

            for account in current_branch_lines:
                invoice_number = account.name
                seller_name = account.create_uid.name
                customer_name = account.partner_id.name
                invoice_date = account.invoice_date
                state = account.payment_state
                cost = sum(account.line_ids.mapped(lambda line: line.purchase_price * line.quantity))
                price = sum(account.mapped('amount_untaxed'))
                total_discount = sum(account.line_ids.mapped('discount'))
                net_cost = sum(account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount))

                out_refund = self.env['account.move'].search([
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('reversed_entry_id', '=', account.id),
                    ('state', '=', 'posted')
                ])
                out_refund_purchase_price = sum(out_refund.line_ids.mapped(lambda x: x.purchase_price * x.quantity))
                out_refund_price = sum(out_refund.mapped('amount_untaxed'))

                report_data.append({
                    'branch_name': branch.name,
                    'invoice_number': invoice_number,
                    'seller_name': seller_name,
                    'customer_name': customer_name,
                    # هنا يتم عرض طريقة الدفع المختارة في الـ wizard
                    'payment_method': self.payment_type,
                    'invoice_date': invoice_date,
                    'total_price': price,
                    'total_discount': total_discount,
                    'net_cost': net_cost,
                    'cost': cost,
                    'total_credit_note': out_refund_price,
                    't': out_refund_purchase_price,
                    'state': state,
                })

        # بدلاً من self.read()[0] نقوم بتجميع بيانات النموذج يدويًا لتجنب محاولة قراءة عمود غير موجود
        form_data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'branch_ids': self.branch_ids.ids,
            'company_id': self.company_id.id,
            'printed_by': self.printed_by,
            'print_date': self.print_date,
            'payment_type': self.payment_type,
        }
        data = {
            'form': form_data,
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_sale_edit_and_reports.sales_report").report_action(self, data=data)
