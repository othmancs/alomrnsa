# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    account_tag_ids = fields.Many2many(string="Account Tags",comodel_name='account.account.tag')

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    _order = 'id desc'
    _description = "Hr Expense"

    include_salary = fields.Boolean('Include in Salary', default=False)
    slip_id = fields.Many2one('hr.payslip', 'Payslip', readonly=True)
    company_contribution = fields.Float(string='Company Contribution', digits='Account', copy=False, tracking=1)
    emp_contribution = fields.Float(string='Employee Contribution', digits='Account', copy=False, tracking=2)

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    account_tag_ids = fields.Many2many(string="Account Tags", comodel_name='account.account.tag')

    # Following comment is for analytic_account_id is not found in "hr.contract" module.
    @api.onchange('employee_id')
    def employee_onchange(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                rec.write({'analytic_account_id': contract.analytic_account_id.id or False,
                        'account_tag_ids': [(6, 0, contract.account_tag_ids.ids)] or False})

    def _prepare_move_values(self):
        """
        This function prepares move values related to an expense
        """
        self.ensure_one()
        move_values = super(HrExpense, self)._prepare_move_values()
        move_values.update({'branch_id': self.employee_id.branch_id.id})
        return move_values

    def _get_account_move_line_values(self):
        import pdb;
        pdb.set_trace()
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id,
                                                   account_date)
            amount_currency = taxes['total_excluded']

            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': 1,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'account_tag_ids': [(6, 0, expense.account_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id,
                                                       account_date)
                amount_currency = tax['amount']
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': tax['base'],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'account_tag_ids': [(6, 0, expense.account_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
                #'branch_id': expense.employee_id.branch_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'account_tag_ids': [(6, 0, expense.account_tag_ids.ids)],
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    _description = "Expense Report"

    include_salary = fields.Boolean('Include in Salary', compute='_set_include_salary', store=True)
    not_inc_sal_amt = fields.Float('Not Include Salary Amount Total', compute='_compute_not_inc_sal_amt',
                                        store=True)

    @api.depends('expense_line_ids', 'expense_line_ids.include_salary')
    def _set_include_salary(self):

        for rec in self:
            flag = False
            for expense in rec.expense_line_ids:
                if not expense.include_salary:
                    flag = True
            if flag:
                rec.include_salary = False
            else:
                rec.include_salary = True

    @api.depends('expense_line_ids', 'expense_line_ids.total_amount', 'expense_line_ids.currency_id',
                    'expense_line_ids.include_salary')
    def _compute_not_inc_sal_amt(self):
        total_amount = 0.0
        for expense in self.expense_line_ids.filtered(lambda expense: not expense.include_salary):
            total_amount += expense.currency_id.with_context(date=expense.date,
                                                             company_id=expense.company_id.id).compute(expense.total_amount,
                                                                                       self.currency_id[0])
            self.not_inc_sal_amt = total_amount


class HrExpensePayment(models.Model):
    _name = 'hr.expense.payment'
    _order = 'id desc'
    _description = "Hr Expense Payment"
    _inherit = 'mail.thread'

    company_contribution = fields.Float(string='Company Contribution', digits='Account', copy=False, tracking=True)
    expense_note = fields.Text(string='Expense Note')
    emp_contribution = fields.Float(string='Employee Contribution', digits='Account', copy=False, tracking=True)
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company"),
                                     ("both", "Both")], default='own_account', states={'done': [('readonly', True)],
                                    'post': [('readonly', True)]}, string="Payment By", tracking=True)

    calculate_company_expense = fields.Boolean('Calculate Company Expense', copy=False, default=True)
    company_contribution_amount = fields.Float(string='Paid By Company', copy=False, tracking=True)
    emp_contribution_amount = fields.Float(string='Paid By Employee', copy=False, tracking=True)

    def generate_expense_payment(self, catch_obj, description, emp_contribution, company_contribution, payment_mode, name, product_id,
                                expense_total, employee_id=False, company_contribution_amount=False, emp_contribution_amount=False, calculate_company_expense=False):
        """
            Generate total expense of employee.
            return: created expense ID
        """
        self.ensure_one()
        expense_obj = self.env['hr.expense']
        if emp_contribution + company_contribution > expense_total:
            raise UserError(_('Contribution should be either greater then 0 or should not be more that total expense'))

        if not product_id:
            raise UserError(_('Please define expense products'))

        if expense_total and company_contribution_amount != 0 and emp_contribution_amount != 0\
            and expense_total != (company_contribution_amount + emp_contribution_amount):
            raise UserError(_("Employee and Company paid by amount should be equal to total expense amount."))

        if payment_mode in ['own_account', 'both'] and emp_contribution_amount:
            if (emp_contribution_amount <= 0 or emp_contribution_amount > expense_total):
                raise UserError(_('Employee Paid amount should not be more then total expense.'))

        if payment_mode in ['company_account', 'both'] and company_contribution_amount:
            if (company_contribution_amount <= 0 or company_contribution_amount > expense_total):
                raise UserError(_('Company Paid should not be more then total expense.'))

        employee = employee_id.id if employee_id else self.employee_id.id
        contract = self.env['hr.contract'].search([('employee_id', '=', employee), ('state', '=', 'open')])

        expense_data = ({
            'employee_id': employee_id.id if employee_id else self.employee_id.id,
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'date': datetime.today().date(),
            'quantity': 1,
            'description': description,
            'name': name,
            'analytic_account_id': contract and contract[0].analytic_account_id.id or False,
            'account_tag_ids': contract and [(6, 0, contract[0].account_tag_ids.ids)] or False,
        })

        if payment_mode in ['own_account', 'both'] and emp_contribution_amount != 0 and emp_contribution != emp_contribution_amount and emp_contribution >= 0.0:
            if emp_contribution != 0.0 and emp_contribution > emp_contribution_amount:
                paid_emp_contribution = emp_contribution - emp_contribution_amount
                expense_data['payment_mode'] = 'company_account'
                expense_data['emp_contribution'] = emp_contribution
                expense_data['unit_amount'] = paid_emp_contribution
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
            elif emp_contribution != 0.0 and emp_contribution < emp_contribution_amount:
                paid_emp_contribution = emp_contribution_amount - emp_contribution
                expense_data['payment_mode'] = 'own_account'
                expense_data['emp_contribution'] = emp_contribution
                expense_data['unit_amount'] = paid_emp_contribution
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
            elif emp_contribution == 0.0 and emp_contribution_amount > 0:
                paid_emp_contribution = emp_contribution_amount - emp_contribution
                expense_data['payment_mode'] = 'own_account'
                expense_data['emp_contribution'] = emp_contribution
                expense_data['unit_amount'] = paid_emp_contribution
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
        elif payment_mode in ['own_account', 'both'] and emp_contribution > 0 and emp_contribution_amount == 0:
            expense_data['payment_mode'] = 'own_account'
            expense_data['emp_contribution'] = emp_contribution
            # expense_data['unit_amount'] = emp_contribution_amount
            expense_data['unit_amount'] = emp_contribution
            expense_id = expense_obj.create(expense_data)
            catch_obj.expense_ids = [(4, expense_id.id)]
            expense_data['message_follower_ids'] = False
        if payment_mode in ['company_account', 'both'] and company_contribution >= 0:
            if payment_mode == 'company_account' and company_contribution != 0.0 and company_contribution < company_contribution_amount:
                expense_data['payment_mode'] = 'company_account'
                expense_data['company_contribution'] = company_contribution
                expense_data['unit_amount'] = company_contribution_amount - company_contribution
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
            elif company_contribution == 0.0 and company_contribution_amount > 0:
                expense_data['payment_mode'] = 'company_account'
                expense_data['company_contribution'] = company_contribution
                expense_data['unit_amount'] = company_contribution_amount
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
            if calculate_company_expense and company_contribution_amount > 0 and\
                not any(catch_obj.expense_ids.filtered(lambda e: e.payment_mode == 'company_account')):
                expense_data['payment_mode'] = 'company_account'
                expense_data['company_contribution'] = company_contribution_amount
                expense_data['unit_amount'] = company_contribution_amount
                if expense_data.get('description'):
                    expense_data['description'] = expense_data.get('description') + ' (Expense for generate company expense post journal entries)'
                else:
                    expense_data['description'] = '(Expense for generate company expense post journal entries)'
                expense_id = expense_obj.create(expense_data)
                catch_obj.expense_ids = [(4, expense_id.id)]
                expense_data['message_follower_ids'] = False
        if not catch_obj.expense_ids:
            raise UserError(_("No any expense need to create!"))

    def redirect_to_expense(self, expense_ids):
        """
            Show employee expense.
        """
        self.ensure_one()
        tree_view = self.env.ref('hr_expense.view_expenses_tree')
        form_view = self.env.ref('hr_expense.hr_expense_view_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expenses'),
            'res_model': 'hr.expense',
            'view_mode': 'from',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', expense_ids.ids)],
            # 'res_id': expense_ids.ids,
            'context': self.env.context,
        }
