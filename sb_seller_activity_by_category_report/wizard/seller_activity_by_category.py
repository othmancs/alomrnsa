from odoo import fields, models


class SellerActivityByCategory(models.TransientModel):
    _name = 'seller.activity.by.category.wizard'

    branch_ids = fields.Many2many('res.branch', string="الفــروع", required=True)
    product_category_ids = fields.Many2many('product.category', string="الفـئة", required=True)
    created_by_id = fields.Many2many('res.partner', string='أنشأ مـن قبـل', domain="[('branch_id', 'in', branch_ids)]")
    date_from = fields.Date(string="مـن تــاريـخ", required=True)
    date_to = fields.Date(string="إلـي تــاريخ", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبــع بـواسـطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تــاريـخ الطـباعــة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def pdf_report_action(self):
        domain = [('invoice_date', '>=', self.date_from),
                  ('invoice_date', '<=', self.date_to),
                  ('move_type', 'in', ['out_invoice', 'out_refund']),
                  ('state', '=', 'posted'),
                  ('branch_id', 'in', self.branch_ids.ids),
                  ('invoice_line_ids.product_id.categ_id', 'in', self.product_category_ids.ids)]

        if self.created_by_id.ids:
            domain.append(('created_by_id', 'in', self.created_by_id.ids))

        lines_data = self.env['account.move'].search(domain)
        existing_branches = lines_data.mapped('branch_id')
        existing_created = list(set(lines_data.mapped('created_by_id')))
        existing_category = list(set(lines_data.mapped('invoice_line_ids.product_id.categ_id')))
        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]
        created_d = {invoice.created_by_id.id: {'branch_name': invoice.branch_id.name,
                                             'created_by_name': invoice.created_by_id.name} for invoice in lines_data}
        created = list(created_d.values())

        report_data = {}
        for branch in existing_branches:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)

            for created_by in existing_created:
                current_created_lines = current_branch_lines.filtered(lambda x: x.created_by_id == created_by)
                for category in existing_category:
                    for line in current_created_lines.invoice_line_ids:
                        current_category_lines = line.filtered(lambda x: x.product_id.categ_id == category and x.move_id.branch_id == branch and x.move_id.created_by_id == created_by and x.product_id.categ_id.id in self.product_category_ids.ids)
                        if current_category_lines:

                            total_option1_branch_purchase = sum(
                                [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                 current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')])
                            total_option2_branch_purchase = sum(
                                [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                 current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')])
                            total_option1_branch_price = sum(
                                [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                 current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')])
                            total_option2_branch_price = sum(
                                [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                 current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')])

                            total_quantity_option1 = sum(
                                current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice').mapped(
                                    'quantity'))

                            total_quantity_option2 = sum(
                                current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice').mapped(
                                    'quantity'))

                            total_option1_branch_purchase_credit = sum(
                                [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                 current_category_lines.filtered(
                                     lambda x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')])
                            total_option2_branch_purchase_credit = sum(
                                [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                 current_category_lines.filtered(
                                     lambda x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')])
                            total_option1_branch_price_credit = sum(
                                [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                 current_category_lines.filtered(
                                     lambda x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')])
                            total_option2_branch_price_credit = sum(
                                [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                 current_category_lines.filtered(
                                     lambda x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')])

                            total_quantity_option1_credit = sum(
                                current_category_lines.filtered(lambda
                                    x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund').mapped(
                                'quantity'))

                            total_quantity_option2_credit = sum(
                                current_category_lines.filtered(lambda
                                    x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund').mapped(
                                'quantity'))

                            #========= for option 1 ===================
                            net_sales_option1 = total_option1_branch_price - total_option1_branch_price_credit
                            cash_profit_option1 = total_option1_branch_purchase - net_sales_option1
                            #========= for option 2 ===================
                            net_sales_option2 = total_option2_branch_price - total_option2_branch_price_credit
                            cash_profit_option2 = total_option2_branch_purchase - net_sales_option2
                            # ========= for profit ===================
                            net_sales_cash_credit  = net_sales_option1 + net_sales_option2
                            net_cost_cash_credit =  total_option1_branch_purchase + total_option2_branch_purchase
                            profit = net_sales_cash_credit - net_cost_cash_credit

                            key = (branch.name, created_by.name, category.name)
                            if key not in report_data:
                                report_data[key] = {
                                    'branch_name': branch.name,
                                    'created_by_name': created_by.name,
                                    'category': category.name,
                                    'total_option1_branch_purchase': 0,
                                    'total_option2_branch_purchase': 0,
                                    'total_option1_branch_price': 0,
                                    'total_option2_branch_price': 0,
                                    'total_quantity_option1': 0,
                                    'total_quantity_option2': 0,

                                    'total_option1_branch_purchase_credit': 0,
                                    'total_option2_branch_purchase_credit': 0,
                                    'total_option1_branch_price_credit': 0,
                                    'total_option2_branch_price_credit': 0,
                                    'total_quantity_option1_credit': 0,
                                    'total_quantity_option2_credit': 0,

                                    'net_sales_option1': 0,
                                    'cash_profit_option1': 0,

                                    'net_sales_option2': 0,
                                    'cash_profit_option2': 0,

                                    'net_sales_cash_credit': 0,
                                    'net_cost_cash_credit': 0,
                                    'profit': 0,
                                }
                            report_data[key]['total_option1_branch_purchase'] += total_option1_branch_purchase
                            report_data[key]['total_option2_branch_purchase'] += total_option2_branch_purchase
                            report_data[key]['total_option1_branch_price'] += total_option1_branch_price
                            report_data[key]['total_option2_branch_price'] += total_option2_branch_price

                            report_data[key]['total_quantity_option1'] += total_quantity_option1
                            report_data[key]['total_quantity_option2'] += total_quantity_option2

                            report_data[key]['total_option1_branch_purchase_credit'] += total_option1_branch_purchase_credit
                            report_data[key]['total_option2_branch_purchase_credit'] += total_option2_branch_purchase_credit
                            report_data[key]['total_option1_branch_price_credit'] += total_option1_branch_price_credit
                            report_data[key]['total_option2_branch_price_credit'] += total_option2_branch_price_credit
                            report_data[key]['total_quantity_option1_credit'] += total_quantity_option1_credit
                            report_data[key]['total_quantity_option2_credit'] += total_quantity_option2_credit

                            #============================== profit =============================================
                            report_data[key]['net_sales_option1'] += net_sales_option1
                            report_data[key]['cash_profit_option1'] += cash_profit_option1
                            report_data[key]['net_sales_option2'] += net_sales_option2
                            report_data[key]['cash_profit_option2'] += cash_profit_option2
                            report_data[key]['net_sales_cash_credit'] += net_sales_cash_credit
                            report_data[key]['net_cost_cash_credit'] += net_cost_cash_credit
                            report_data[key]['profit'] += profit


        # Convert report_data dictionary to a list
        report_data_list = list(report_data.values())
        print('report_data_list', report_data_list)
        data = {
            'form': self.read()[0],
            'branch_data': report_data_list,
            'branches': branches,
            'created': created
        }
        print("branch_data", )
        print("data====>", data)
        return self.env.ref("sb_seller_activity_by_category_report.seller_activity_by_category_report_action").report_action(self, data=data)



    def xls_report_action(self):
        return self.env.ref("sb_seller_activity_by_category_report.seller_activity_by_category_report_action_xls").report_action(self)



































































        #
        # # Prepare data for the report template
        # branch_data = []
        # for branch in self.branch_ids:
        #     created_by_data = {}
        #     for created_by_id in created_by_ids:
        #         branch_domain = domain + [('branch_id', '=', branch.id), ('created_by_id', '=', created_by_id)]
        #         if self.env['account.move'].search_count(branch_domain) > 0:
        #             # Ensure 'option1' and 'option2' are properly populated in result
        #             data_option1 = result['option1'].get(created_by_id, {})
        #             data_option2 = result['option2'].get(created_by_id, {})
        #             created_by_data[created_by_id] = {
        #                 'name': created_by_names.get(created_by_id, ''),
        #                 'option1': data_option1,
        #                 'option2': data_option2,
        #             }
        #
        #     branch_data.append({
        #         'branch_name': branch.name,
        #         'created_by_data': created_by_data,
        #     })
        #
        # wizard_data = {
        #     'company_id': self.company_id.name,
        #     'branch_data': branch_data,
        #     'date_from': self.date_from,
        #     'date_to': self.date_to,
        #     'printed_by': self.printed_by,
        #     'print_date': self.print_date,
        # }
        #
        # data = {
        #     'form': wizard_data,
        # }
        # return self.env.ref("sb_total_seller_activity_report.seller_activity_report_xls").report_action(self, data=data)
        # print("inside xlsx report")


#
# from odoo import fields, models
#
#
# class SellerActivityByCategory(models.TransientModel):
#     _name = 'seller.activity.by.category.wizard'
#
#     branch_ids = fields.Many2many('res.branch', string="Branch", required=True)
#     product_category_ids = fields.Many2many('product.category', string="فئه المنج", required=True)
#     created_by_id = fields.Many2many('res.partner', string='انشأ من قبل', domain="[('branch_id', 'in', branch_ids)]")
#     date_from = fields.Date(string="From Date", required=True)
#     date_to = fields.Date(string="To Date", required=True)
#     company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
#     printed_by = fields.Char(string="Printed By", compute="_compute_printed_by")
#     print_date = fields.Date(string="Print Date", default=fields.Date.context_today)
#
#     def _compute_printed_by(self):
#         for record in self:
#             record.printed_by = self.env.user.name
#
#     def pdf_report_action(self):
#         domain = [('company_id', '=', self.company_id.id)]
#
#         if self.branch_ids:
#             domain += [('branch_id', 'in', self.branch_ids.ids)]
#
#         if self.date_from:
#             domain += [('invoice_date', '>=', self.date_from)]
#
#         if self.date_to:
#             domain += [('invoice_date', '<=', self.date_to)]
#
#         if self.product_category_ids:
#             domain += [('invoice_line_ids.product_id.categ_id', 'in', self.product_category_ids.ids)]
#
#         print('domain======>', domain)
#
#         created_by_records = self.env['res.partner'].search([('id', 'in', self.created_by_id.ids)])
#         print('created_by_records====>', created_by_records)
#         created_by_ids = created_by_records.ids
#         print('created_by_ids====>', created_by_ids)
#         created_by_names = {rec.id: rec.name for rec in created_by_records}
#         print('created_by_names====>', created_by_names)
#
#         result = {'option1': {}, 'option2': {}}
#
#         for payment_method in ['option1', 'option2']:
#             for created_by_id in created_by_ids:
#                 domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted'),
#                                                ('created_by_id', '=', created_by_id),
#                                                ('payment_method', '=', payment_method)]
#                 domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
#                                            ('created_by_id', '=', created_by_id),
#                                            ('payment_method', '=', payment_method)]
#
#                 credit_notes = self.env['account.move'].search(domain_credit_note)
#                 invoices = self.env['account.move'].search(domain_invoice)
#
#                 # Calculate sums and quantities for credit notes
#                 credit_notes_sum = sum(
#                     line.quantity * line.price_unit for credit_note in credit_notes for line in
#                     credit_note.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#                 total_quantity_credit_notes = sum(
#                     line.quantity for credit_note in credit_notes for line in credit_note.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#
#                 # Calculate sums and quantities for invoices
#                 invoices_sum = sum(
#                     line.quantity * line.price_unit for invoice in invoices for line in invoice.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#                 total_quantity_invoices = sum(
#                     line.quantity for invoice in invoices for line in invoice.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#
#                 # Calculate total purchase price for credit notes and invoices
#                 credit_notes_total_purchase_price = sum(
#                     line.price_subtotal for credit_note in credit_notes for line in credit_note.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#
#                 invoices_total_purchase_price = sum(
#                     line.price_subtotal for invoice in invoices for line in invoice.invoice_line_ids
#                     if line.product_id.categ_id.id in self.product_category_ids.ids)
#
#                 credit_notes_read = credit_notes.read(
#                     ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
#                      'total_purchase_price'])
#                 invoices_read = invoices.read(
#                     ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
#                      'total_purchase_price'])
#
#                 result[payment_method][created_by_id] = {
#                     'name': created_by_names.get(created_by_id, ''),
#                     'credit_notes': credit_notes_read,
#                     'invoices': invoices_read,
#                     'credit_notes_sum': credit_notes_sum,
#                     'invoices_sum': invoices_sum,
#                     'credit_notes_quantity': total_quantity_credit_notes,
#                     'invoices_quantity': total_quantity_invoices,
#                     'credit_notes_total_purchase_price': credit_notes_total_purchase_price,
#                     'invoices_total_purchase_price': invoices_total_purchase_price,
#                 }
#
#         # Prepare data for the report template
#         branch_data = []
#         for branch in self.branch_ids:
#             created_by_data = {}
#             for created_by_id in created_by_ids:
#                 branch_domain = domain + [('branch_id', '=', branch.id), ('created_by_id', '=', created_by_id)]
#                 if self.env['account.move'].search_count(branch_domain) > 0:
#                     # Ensure 'option1' and 'option2' are properly populated in result
#                     data_option1 = result['option1'].get(created_by_id, {})
#                     data_option2 = result['option2'].get(created_by_id, {})
#                     created_by_data[created_by_id] = {
#                         'name': created_by_names.get(created_by_id, ''),
#                         'option1': data_option1,
#                         'option2': data_option2,
#                     }
#
#             branch_data.append({
#                 'branch_name': branch.name,
#                 'created_by_data': created_by_data,
#             })
#
#         wizard_data = {
#             'company_id': self.company_id.name,
#             'branch_data': branch_data,
#             'date_from': self.date_from,
#             'date_to': self.date_to,
#             'printed_by': self.printed_by,
#             'print_date': self.print_date,
#             'product_category_ids': self.product_category_ids
#         }
#
#         data = {
#             'form': wizard_data,
#         }
#         print('data====>', data)
#
#         return self.env.ref("sb_seller_activity_by_category_report.seller_activity_by_category_report_action").report_action(self, data=data)



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#==============================================================================================================================================

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#==============================================================================================================================================

   # def pdf_report_action(self):
   #      dic = []
   #      for rec in self.branch_ids:
   #          dic.append(rec.name)
   #      print("dic===>", dic)
   #      cust = []
   #      for rec in self.created_by_id:
   #          cust.append(rec.name)
   #      print("cust===>", cust)
   #
   #      branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in self.branch_ids]
   #      print("branches===>", branches)
   #      domain = [('company_id', '=', self.company_id.id)]
   #      if self.branch_ids:
   #          domain += [('branch_id', 'in', self.branch_ids.ids)]
   #      if self.date_from:
   #          domain += [('invoice_date', '>=', self.date_from)]
   #      if self.date_to:
   #          domain += [('invoice_date', '<=', self.date_to)]
   #
   #      if self.product_category_ids:
   #          domain.append(('line_ids.product_id.categ_id.id', 'in', self.product_category_ids.ids))
   #
   #      created_by_ids = self.created_by_id.ids or self.env['res.partner'].search([]).ids
   #      created_by_names = dict(self.env['res.partner'].browse(created_by_ids).name_get())
   #
   #      result = {'option1': {}, 'option2': {}}
   #
   #      for payment_method in ['option1', 'option2']:
   #          for created_by_id in created_by_ids:
   #              domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted'),
   #                                             ('created_by_id', '=', created_by_id),
   #                                             ('payment_method', '=', payment_method)]
   #              domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
   #                                         ('created_by_id', '=', created_by_id),
   #                                         ('payment_method', '=', payment_method)]
   #
   #              credit_notes = self.env['account.move'].search(domain_credit_note)
   #              invoices = self.env['account.move'].search(domain_invoice)
   #
   #              for rec in self.branch_ids:
   #                  current_branch_lines = invoices.filtered(lambda x: x.branch_id == rec)
   #                  branch_records = [{'created_by_id': invoice.created_by_id.name, 'branch_id': invoice.branch_id.name} for
   #                                    invoice in current_branch_lines]
   #                  print("branch_records", branch_records)
   #
   #              credit_notes_sum = {rec.name: sum(
   #                  line.quantity * line.price_unit for credit_note in credit_notes for line in credit_note.invoice_line_ids
   #                  if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
   #              print("credit_notes_sum====>: ", credit_notes_sum)
   #
   #              invoices_sum = {rec.name: sum(
   #                  line.quantity * line.price_unit for invoice in invoices for line in invoice.invoice_line_ids
   #                  if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
   #              print("invoices_sum====>: ", invoices_sum)
   #
   #              total_quantity_credit_notes = {rec.name: sum(
   #                  line.quantity for credit_note in credit_notes for line in credit_note.invoice_line_ids
   #                  if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
   #              print("total_quantity_credit_notes====>: ", total_quantity_credit_notes)
   #
   #              total_quantity_invoices = {rec.name: sum(
   #                  line.quantity for invoice in invoices for line in invoice.invoice_line_ids
   #                  if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
   #              print("total_quantity_invoices====>: ", total_quantity_invoices)
   #
   #              credit_notes_total_purchase_price = sum(
   #                  sum(
   #                      line.purchase_price * line.quantity
   #                      for line in credit_note.invoice_line_ids
   #                      if line.product_id.categ_id.id in self.product_category_ids.ids
   #                  ) for credit_note in credit_notes
   #              )
   #              print("credit_notes_total_purchase_price====>: ", credit_notes_total_purchase_price)
   #              invoices_total_purchase_price = sum(
   #                  sum(
   #                      line.purchase_price * line.quantity
   #                      for line in invoice.invoice_line_ids
   #                      if line.product_id.categ_id.id in self.product_category_ids.ids
   #                  ) for invoice in invoices
   #              )
   #
   #              print("invoices_total_purchase_price====>: ", invoices_total_purchase_price)
   #              credit_notes_read = credit_notes.read(
   #                  ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
   #                   'total_purchase_price'])
   #              invoices_read = invoices.read(
   #                  ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
   #                   'total_purchase_price'])
   #
   #              result[payment_method][created_by_id] = {
   #                  'name': created_by_names.get(created_by_id, ''),
   #                  'credit_notes': credit_notes_read,
   #                  'invoices': invoices_read,
   #                  'credit_notes_sum': credit_notes_sum,
   #                  'invoices_sum': invoices_sum,
   #                  'credit_notes_quantity': total_quantity_credit_notes,
   #                  'invoices_quantity': total_quantity_invoices,
   #                  'credit_notes_total_purchase_price': credit_notes_total_purchase_price,
   #                  'invoices_total_purchase_price': invoices_total_purchase_price,
   #              }
   #
   #      branch_data = []
   #      for branch in self.branch_ids:
   #          created_by_data = {}
   #          for created_by_id in created_by_ids:
   #              branch_domain = domain + [('branch_id', '=', branch.id), ('created_by_id', '=', created_by_id)]
   #              if self.env['account.move'].search_count(branch_domain) > 0:
   #                  data_option1 = result['option1'].get(created_by_id, {})
   #                  data_option2 = result['option2'].get(created_by_id, {})
   #                  created_by_data[created_by_id] = {
   #                      'name': created_by_names.get(created_by_id, ''),
   #                      'option1': data_option1,
   #                      'option2': data_option2,
   #                  }
   #
   #          branch_data.append({
   #              'branch_name': branch.name,
   #              'created_by_data': created_by_data,
   #          })
   #
   #      wizard_data = {
   #          'company_id': self.company_id.name,
   #          'branch_data': branch_data,
   #          'date_from': self.date_from,
   #          'date_to': self.date_to,
   #          'printed_by': self.printed_by,
   #          'print_date': self.print_date,
   #          'product_category_ids': self.product_category_ids
   #      }
   #
   #      data = {
   #          'form': wizard_data,
   #      }
   #
   #      print("data====>: ", data)
   #
   #      # return self.env.ref("sb_seller_activity_by_category_report.seller_activity_by_category_report_action").report_action(self, data=data)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================


    # def pdf_report_action(self):
    #     domain = [('company_id', '=', self.company_id.id)]
    #     if self.branch_ids:
    #         domain += [('branch_id', 'in', self.branch_ids.ids)]
    #
    #     if self.date_from:
    #         domain += [('invoice_date', '>=', self.date_from)]
    #
    #     if self.date_to:
    #         domain += [('invoice_date', '<=', self.date_to)]
    #
    #     result = {}
    #
    #     for branch in self.branch_ids:
    #         branch_data = {
    #             'branch_name': branch.name,
    #             'created_by_data': {},
    #         }
    #         for created_by in self.created_by_id:
    #             created_by_data = {
    #                 'name': created_by.name,
    #                 'product_category_data': {},
    #             }
    #             for product_category in self.product_category_ids:
    #                 domain_credit_note = domain + [
    #                     ('move_type', '=', 'out_refund'), ('state', '=', 'posted'),
    #                     ('branch_id', '=', branch.id), ('created_by_id', '=', created_by.id),
    #                     ('line_ids.product_id.categ_id', '=', product_category.id)
    #                 ]
    #                 domain_invoice = domain + [
    #                     ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
    #                     ('branch_id', '=', branch.id), ('created_by_id', '=', created_by.id),
    #                     ('line_ids.product_id.categ_id', '=', product_category.id)
    #                 ]
    #                 credit_notes = self.env['account.move'].search(domain_credit_note)
    #                 invoices = self.env['account.move'].search(domain_invoice)
    #
    #                 credit_notes_sum = {rec.name: sum(
    #                     line.quantity * line.price_unit for line in credit_notes.invoice_line_ids
    #                     if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
    #
    #                 print(
    #                     "================================================================================================================================")
    #                 print("credit_notes_sum===>", credit_notes_sum)
    #
    #                 invoices_sum = {rec.name: sum(
    #                     line.quantity * line.price_unit for line in invoices.invoice_line_ids
    #                     if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
    #
    #                 print(
    #                     "================================================================================================================================")
    #                 print("invoices_sum===>", invoices_sum)
    #
    #                 total_quantity_credit_notes = {rec.name: sum(
    #                     line.quantity for line in credit_notes.invoice_line_ids
    #                     if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
    #
    #                 print(
    #                     "================================================================================================================================")
    #                 print("total_quantity_credit_notes===>", total_quantity_credit_notes)
    #
    #                 total_quantity_invoices = {rec.name: sum(
    #                     line.quantity for line in invoices.invoice_line_ids
    #                     if line.product_id.categ_id.id == rec.id) for rec in self.product_category_ids}
    #                 print(
    #                     "================================================================================================================================")
    #                 print("total_quantity_invoices===>", total_quantity_invoices)
    #
    #                 credit_notes_total_purchase_price ={rec.name: sum(
    #                     sum(
    #                         line.purchase_price * line.quantity
    #                         for line in credit_note.invoice_line_ids
    #                         if line.product_id.categ_id.id in self.product_category_ids.ids
    #                     ) for credit_note in credit_notes
    #                 ) for rec in self.product_category_ids}
    #                 print("==========================================================")
    #                 print("credit_notes_total_purchase_price===>", credit_notes_total_purchase_price)
    #
    #                 invoices_total_purchase_price ={rec.name: sum(
    #                     sum(
    #                         line.purchase_price * line.quantity
    #                         for line in invoice.invoice_line_ids
    #                         if line.product_id.categ_id.id in self.product_category_ids.ids
    #                     ) for invoice in invoices
    #                 ) for rec in self.product_category_ids}
    #                 print("=============================================================")
    #                 print("invoices_total_purchase_price===>", invoices_total_purchase_price)
    #
    #                 created_by_data['product_category_data'][product_category.name] = {
    #                     'credit_notes_sum': credit_notes_sum[product_category.name],
    #                     'invoices_sum': invoices_sum[product_category.name],
    #                     'credit_notes_quantity': total_quantity_credit_notes[product_category.name],
    #                     'invoices_quantity': total_quantity_invoices[product_category.name],
    #                     'credit_notes_total_purchase_price': credit_notes_total_purchase_price,
    #                     'invoices_total_purchase_price': invoices_total_purchase_price,
    #                 }
    #
    #             branch_data['created_by_data'][created_by.id] = created_by_data
    #
    #         result[branch.id] = branch_data
    #     print("================================================================================================================================")
    #     print("result===>", result)
    #     wizard_data = {
    #         'company_id': self.company_id.name,
    #         'branch_data': list(result.values()),
    #         'date_from': self.date_from,
    #         'date_to': self.date_to,
    #         'printed_by': self.printed_by,
    #         'print_date': self.print_date,
    #         'product_category_ids': self.product_category_ids
    #     }
    #
    #     data = {
    #         'form': wizard_data,
    #     }
    #     print("================================================================================================================================")
    #     print("data===>", data)
    #
    #     return self.env.ref("sb_seller_activity_by_category_report.seller_activity_by_category_report_action").report_action(self,data=data)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================================================================================