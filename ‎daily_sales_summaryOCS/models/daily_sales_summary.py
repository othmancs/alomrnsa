@api.model
def generate_sales_collection_report(self):
    """إنشاء تقرير Excel للمبيعات والتحصيل مع تفصيل طرق الدفع"""
    # إنشاء كتاب Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('المبيعات والتحصيل')

    # تنسيقات الخلايا
    title_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter',
        'font_size': 16, 'font_color': '#4472C4'
    })
    subtitle_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14
    })
    date_format = workbook.add_format({
        'align': 'center', 'valign': 'vcenter', 'font_size': 12
    })
    header_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter',
        'bg_color': '#4472C4', 'font_color': 'white', 'border': 1, 'font_size': 12, 'text_wrap': True
    })
    currency_format = workbook.add_format({
        'num_format': '#,##0.00', 'border': 1, 'align': 'right'
    })
    text_format = workbook.add_format({'border': 1, 'align': 'right'})
    total_format = workbook.add_format({
        'bold': True, 'num_format': '#,##0.00', 'border': 1,
        'align': 'right', 'bg_color': '#D9E1F2'
    })

    # كتابة عنوان التقرير
    worksheet.merge_range('A1:I1', self.company_id.name, title_format)
    worksheet.merge_range('A2:I2', 'تقرير حركة المبيعات اليومية', subtitle_format)
    worksheet.merge_range('A3:I3', f'من {self.date_from} إلى {self.date_to}', date_format)
    worksheet.write(3, 0, '', workbook.add_format())

    # الحصول على جميع طرق الدفع الفريدة المستخدمة في الفترة
    payment_methods = set()
    domain = [
        ('invoice_date', '>=', self.date_from),
        ('invoice_date', '<=', self.date_to),
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
        ('payment_state', '=', 'paid'),
        ('company_id', '=', self.company_id.id)
    ]
    if self.branch_ids:
        domain.append(('branch_id', 'in', self.branch_ids.ids))
    
    invoices = self.env['account.move'].search(domain)
    for invoice in invoices:
        for payment in invoice._get_reconciled_payments():
            if payment.payment_method_line_id:
                payment_methods.add(payment.payment_method_line_id.name or 'غير محدد')

    # الحصول على طرق الدفع للتحصيل الآجل
    credit_payment_methods = set()
    credit_payments = self.env['account.payment'].search([
        ('date', '>=', self.date_from),
        ('date', '<=', self.date_to),
        ('payment_type', '=', 'inbound'),
        ('state', '=', 'posted'),
        ('is_internal_transfer', '=', False),
        ('company_id', '=', self.company_id.id)
    ])
    for payment in credit_payments:
        if payment.payment_method_line_id:
            credit_payment_methods.add(payment.payment_method_line_id.name or 'غير محدد')

    # عناوين الأعمدة الجديدة المعدلة حسب الطلب
    base_headers = [
        'الفرع',
        'المبيعات النقدية',  # (إجمالي المبيعات مع الضريبة)
        'صافي المبيعات الآجلة',
        'إجمالي التحصيل النقدي'  # تم نقل هذا العمود ليكون بعد صافي المبيعات الآجلة
    ]
    
    # إضافة أعمدة لطرق الدفع الفريدة (لتحصيل النقدي)
    for method in sorted(payment_methods):
        base_headers.append(f'تحصيل نقدي - {method}')
    
    # إضافة أعمدة لطرق الدفع للتحصيل الآجل
    for method in sorted(credit_payment_methods):
        base_headers.append(f'تحصيل آجل - {method}')
    
    # إضافة الأعمدة المتبقية
    base_headers.extend([
        'إجمالي المقبوضات',
        'إجمالي المبيعات'
    ])

    # تحديد عرض الأعمدة
    worksheet.set_column(0, 0, 30)  # عمود الفرع
    worksheet.set_column(1, len(base_headers)-1, 20)  # الأعمدة الرقمية

    # كتابة العناوين
    for col, header in enumerate(base_headers):
        worksheet.write(4, col, header, header_format)

    # جمع البيانات لكل فرع على حدة
    branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
    branches = self.env['res.branch'].browse(branch_ids)

    # متغيرات لتخزين الإجماليات
    totals = {
        'cash_sales': 0,
        'credit': 0,
        'total_cash_receipts': 0,
        'total_credit_receipts': 0,
        'total_sales': 0
    }
    
    # إضافة إجماليات طرق الدفع النقدية
    for method in payment_methods:
        totals[f'cash_method_{method}'] = 0
    
    # إضافة إجماليات طرق الدفع الآجلة
    for method in credit_payment_methods:
        totals[f'credit_method_{method}'] = 0

    row = 5  # بدء البيانات من الصف 5 بعد العناوين
    for branch in branches:
        # حساب المبيعات النقدية للفرع
        cash_invoices = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ])
        
        # حساب المبيعات حسب طريقة الدفع النقدية
        cash_method_totals = {method: 0.0 for method in payment_methods}
        
        for invoice in cash_invoices:
            for payment in invoice._get_reconciled_payments():
                if payment.payment_method_line_id:
                    method_name = payment.payment_method_line_id.name or 'غير محدد'
                    if method_name in cash_method_totals:
                        cash_method_totals[method_name] += payment.amount
        
        branch_cash_sales = sum(invoice.amount_total for invoice in cash_invoices)  # الإجمالي مع الضريبة

        # حساب المبيعات الآجلة للفرع
        credit_invoices = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ])
        branch_credit = sum(invoice.amount_total for invoice in credit_invoices)  # الإجمالي مع الضريبة

        # حساب إرجاعات مسترد المبلغ للفرع
        cash_refunds = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ])
        branch_cash_refunds = sum(refund.amount_total for refund in cash_refunds)

        # حساب التحصيل النقدي (إجمالي المبيعات النقدية)
        branch_cash_receipts = branch_cash_sales

        # حساب التحصيل الآجل (المدفوعات الواردة)
        payments = self.env['account.payment'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('is_internal_transfer', '=', False),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ])
        
        
        # حساب التحصيل الآجل حسب طريقة الدفع
        credit_method_totals = {method: 0.0 for method in credit_payment_methods}
        branch_total_credit_receipts = 0
        
        for payment in payments:
            if payment.payment_method_line_id:
                method_name = payment.payment_method_line_id.name or 'غير محدد'
                if method_name in credit_method_totals:
                    credit_method_totals[method_name] += payment.amount
                    branch_total_credit_receipts += payment.amount
        
        # طرح الإرجاعات من التحصيل الآجل
        branch_total_credit_receipts = branch_total_credit_receipts + branch_cash_receipts - branch_cash_refunds

        # إجمالي المبيعات للفرع
        branch_total = branch_cash_sales + branch_credit

        # تحديث الإجماليات
        totals['cash_sales'] += branch_cash_sales
        totals['credit'] += branch_credit
        totals['total_cash_receipts'] += branch_cash_receipts
        totals['total_credit_receipts'] += branch_total_credit_receipts
        totals['total_sales'] += branch_total
        
        for method, amount in cash_method_totals.items():
            totals[f'cash_method_{method}'] += amount
        
        for method, amount in credit_method_totals.items():
            totals[f'credit_method_{method}'] += amount

        # كتابة بيانات الفرع حسب الترتيب الجديد
        col = 0
        worksheet.write(row, col, branch.name, text_format); col += 1
        worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
        worksheet.write(row, col, branch_credit, currency_format); col += 1
        worksheet.write(row, col, branch_cash_receipts, currency_format); col += 1  # إجمالي التحصيل النقدي بعد صافي المبيعات الآجلة
        
        # كتابة تحصيل نقدي لكل طريقة دفع
        for method in sorted(payment_methods):
            worksheet.write(row, col, cash_method_totals.get(method, 0.0), currency_format)
            col += 1
        
        # كتابة تحصيل آجل لكل طريقة دفع
        for method in sorted(credit_payment_methods):
            worksheet.write(row, col, credit_method_totals.get(method, 0.0), currency_format)
            col += 1
        
        worksheet.write(row, col, branch_total_credit_receipts, currency_format); col += 1
        worksheet.write(row, col, branch_total, currency_format)

        row += 1

    # إضافة المجموع الكلي إذا كان هناك أكثر من فرع
    if row > 5:
        col = 0
        worksheet.write(row, col, 'الإجمالي', header_format); col += 1
        worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
        worksheet.write(row, col, totals['credit'], total_format); col += 1
        worksheet.write(row, col, totals['total_cash_receipts'], total_format); col += 1  # إجمالي التحصيل النقدي بعد صافي المبيعات الآجلة
        
        # إجمالي تحصيل نقدي لكل طريقة دفع
        for method in sorted(payment_methods):
            worksheet.write(row, col, totals.get(f'cash_method_{method}', 0.0), total_format)
            col += 1
        
        # إجمالي تحصيل آجل لكل طريقة دفع
        for method in sorted(credit_payment_methods):
            worksheet.write(row, col, totals.get(f'credit_method_{method}', 0.0), total_format)
            col += 1
        
        worksheet.write(row, col, totals['total_credit_receipts'], total_format); col += 1
        worksheet.write(row, col, totals['total_sales'], total_format)

    # إغلاق الكتاب وحفظه
    workbook.close()
    output.seek(0)

    return {
        'file_name': f"تقرير_المبيعات_اليومية_{self.date_from}_إلى_{self.date_to}.xlsx",
        'file_content': output.read(),
        'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
