# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Employee Payslip Reports ( PDF/Excel)',
    'version': '16.0.0.2',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'category': 'Human Resources',
    'summary': 'Employee Multiple Payslip Report print employee payslip report hr payslip report employee pay slip report mass employee payslip report print payslip report print employee payroll report print pay slip report print payslip excel report payslip xls report',
    'description': """ 
            

               Employee Multiple Payslip Report PDF & XLS  in odoo,
               Multiple payslip report pdf in odoo,
               Multiple payslip report xls in odoo,
               Salary computation Group by Salary Rule Category in odoo,
               Salary computation Group by Salary Rule in odoo,
               Print Payslip Report by PDF & XLS File Type in odoo,


    """,
    'depends':['hr_payroll'],
    'data':[
        'security/ir.model.access.csv',
        'wizard/payslip_report_wizard.xml',
        'report/employee_payslip_report.xml',
        'report/payslip_report_template.xml',
        ],
    'price': 15,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    "license":'OPL-1',
    'live_test_url':'https://youtu.be/ViSC1MFaHds',
    'images':['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
