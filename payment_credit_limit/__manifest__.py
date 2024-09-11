# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Credit Limit',
    'version': '1.0.1',
    'summary': 'Customer payment credit limit',
    'sequence': 20,
    'description': """
        Basic customer credit limit manage of customer.

        credit
credit limit
customer credit
customer credit limit
customer due
past due
credit restriction
payment
payment credit
payment credit limit
customer payment
customer payment credit
customer payment credit limit
credit score
customer credit score
advance credti
advance credit limit
advance customer credit
advance customer credit limit
borrower
withdraw
credit account
payment term
accounting
taxation
audit
account
tax
finance
financial management
letter of credit
leverage
balance
line of credit
bank line
customer
customer payment overdue
overdue customer payment
customer overdue payment reminder
customer overdue payment followup
due days
payment due
due payment
scheduler
analysis
followup analysis
Accounting & Auditing Terms
accounting concepts
marginal benefit
asset
revenue
buyer
amount due
due amount
demand
cash
cash on delivery
deferred payment
period
duration
provision
cash flow
enterpreneur
monitoring
sale
feedback
requirement
effectiveness
following
auditing
management
contract management
    """,
    'category': 'EWS',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['sale_stock', 'account', 'board', 'sale_crm'],
    'data': [
            'wizard/check_credit_limit_view.xml',
            'security/ir.model.access.csv',
            'views/sale_view.xml',
            'views/partner_view.xml'
    ],
    'demo': [],
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 40.0,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
