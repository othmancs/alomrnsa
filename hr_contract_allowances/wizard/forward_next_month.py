# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class ForwardDeductionNextMonth(models.TransientModel):
    _name = "forward.deduction.next.month"
    _description = "Forward Next Month"
    
    no_month = fields.Integer(string="No Of Months", default=1)
    
    #while click on Action Confirm button
    def action_confirm(self):
        """
        it'll move forward entries with given month.
        """
        active_id = self._context.get('active_id',False)
        if active_id:
            contract_deduction_id = self.env['contract.deduction'].browse(int(active_id))
            deduction_line = self.env['contract.deduction.line'].search([('deduction_id','=',contract_deduction_id.id),('status','=','pending')], order = 'date desc')
            date_start = datetime.now().date()
            deduction_date = datetime.strptime(str(deduction_line[0].date), '%Y-%m-%d')
            for i in range(1, int(self.no_month) + 1):
                for line in deduction_line:
                    if datetime.strptime(str(line.date), '%Y-%m-%d').date().month == date_start.month \
                    and datetime.strptime(str(line.date), '%Y-%m-%d').date().year == date_start.year:
                        line.status = 'hold'
                        self.env['contract.deduction.line'].create({
                            'date': deduction_date + relativedelta(months=1),
                            'amount': line.amount,
                            'employee_id': contract_deduction_id.employee_id.id,
                            'deduction_id': contract_deduction_id.id,
                            'installment_type':contract_deduction_id.installment_type,
                            'description' : str(line.description) + '-' + str(deduction_date + relativedelta(months=1))})
                        date_start = date_start + relativedelta(months=1)
                        deduction_date = deduction_date + relativedelta(months=1)