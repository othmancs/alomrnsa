from odoo import models, api

class DeleteCustomerWizard(models.TransientModel):
    _name = 'delete.customer.wizard'
    _description = 'Confirmation Wizard for Deleting Customers'

    def confirm_delete(self):
        self.env['delete.customer.records'].action_delete_customer_data()
