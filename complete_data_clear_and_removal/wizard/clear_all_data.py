# -*- coding: utf-8 -*-
# Copyright (C) Quocent Pvt. Ltd.
# All Rights Reserved

from odoo import models, fields, api, _

class ClearDataWizard(models.TransientModel):
    _name = 'clear.data.wizard'
    _description = 'Clear Data Wizard'

    #all Data
    all_data_clear = fields.Boolean(string="All Data",help="this will clear/delete all data")
    #sale
    sale = fields.Boolean(string="Sale",help="this will clear/delete sales")
    sale_and_transfer = fields.Boolean(string="Sale & All Transfers",help="this will clear/delete all sales and its transaction")
    #purchase
    purchase = fields.Boolean(string="Purchase",help="this will clear/delete purchase ")
    purchase_and_transfer = fields.Boolean(string="Purchase & All Transfers",help="this will clear/delete all purchase and its transfers")
    #inventory
    inventory_only_transfer = fields.Boolean(string="Only Transfers",help="this will clear/delete/delete only transfers")
    #project
    project_tasks_timesheets = fields.Boolean(string="Project, Tasks & Timesheets",help="this will clear/delete all the project, tasks and timesheets")
    only_task_timesheets = fields.Boolean(string="Only Task and Timesheets",help="this will clear/delete only task and timesheets")
    #contacts
    customers_vendors = fields.Boolean(string='Customers & Vendors',help="this will clear/delete all customers and vendors")
    #manufacturing
    bom_manufacturing_orders = fields.Boolean(string="BOM & Manufacturing Orders",help="this will clear/delete all the BOM and Manufacturing orders")
    only_manufacturing_orders = fields.Boolean(string="Only Manufacturing Orders",help="this will only clear/delete manufacturing orders")
    #accounting
    # invoicing_payments_journalentries = fields.Boolean(string="All Invoicing, Payments & Journal Entries",help="this will clear/delete all invoicing, payments and journal entries")
    # only_journal_entries = fields.Boolean(string="Only Journal Entries",help="this will only clear/delete journal entries")

    sale_install = fields.Boolean(string="Sale_invisible")
    sale_and_transfer_install = fields.Boolean(string="Sale_and_transfers_invisible")
    purchase_install = fields.Boolean(string="Purchase_invisible")
    purchase_and_transfer_install = fields.Boolean(string="Purchase_invisible")
    inventory_only_transfer_install = fields.Boolean(string="Inventory_and_transfers_invisible")
    project_tasks_timesheets_install = fields.Boolean(string="Project_invisible")
    bom_manufacturing_orders_install = fields.Boolean(string="Manufacturing_invisible")
    invoicing_cust_and_vend_install = fields.Boolean(string="Accounting_invisible")

    def open_wizard_action(self):
        # Check if the 'sale_management' module is installed
        sale_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'sale_management')
        ]))
        # Check if the 'sale_management' and 'stock' module is installed
        sale_and_transfer_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'sale_management')
        ])) and bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'stock')
        ]))
        # Check if the 'purchase' module is installed
        purchase_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'purchase')
        ]))
        # Check if the 'purchase' and 'stock' module is installed
        purchase_and_transfer_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'purchase')
        ])) and bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'stock')
        ]))
        # Check if the 'stock' module is installed
        inventory_only_transfer_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'stock')
        ]))
        # Check if the 'project' module is installed
        project_tasks_timesheets_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'project')
        ]))
        # Check if the 'mrp' module is installed
        bom_manufacturing_orders_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'mrp')
        ]))
        # Check if the 'Invoicing' module is installed
        invoicing_cust_and_vend_install = bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'account')
        ]))and bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'sale_management')
        ]))and bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'purchase')
        ]))and bool(self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
            ('name', '=', 'stock')
        ]))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'clear.data.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_install': sale_install,
                'default_sale_and_transfer_install': sale_and_transfer_install,
                'default_purchase_install': purchase_install,
                'default_purchase_and_transfer_install': purchase_and_transfer_install,
                'default_inventory_only_transfer_install': inventory_only_transfer_install,
                'default_project_tasks_timesheets_install': project_tasks_timesheets_install,
                'default_bom_manufacturing_orders_install': bom_manufacturing_orders_install,
                'default_invoicing_cust_and_vend_install': invoicing_cust_and_vend_install,
            }
        }

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('all_data_clear')
    def all_data_clear_click(self):
        if self.all_data_clear:
            self.sale,self.sale_and_transfer,self.purchase,self.purchase_and_transfer,self.inventory_only_transfer,self.project_tasks_timesheets,self.only_task_timesheets,self.customers_vendors,self.bom_manufacturing_orders,self.only_manufacturing_orders = True,True,True,True,True,True,True,True,True,True
        else :
            self.sale,self.sale_and_transfer,self.purchase,self.purchase_and_transfer,self.inventory_only_transfer,self.project_tasks_timesheets,self.only_task_timesheets,self.customers_vendors,self.bom_manufacturing_orders,self.only_manufacturing_orders = False,False,False,False,False,False,False,False,False,False

    def clear_data(self):
        #sale-->sale
        if self.sale:
            sale_orders = self.env['sale.order'].search([])
            for order in sale_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            sale_orders.unlink()
        #sale-->sale_and_all_transfers
        if self.sale_and_transfer:
            sale_orders = self.env['sale.order'].search([])
            for order in sale_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            sale_orders.unlink()
            self.env.cr.execute("""
                DELETE FROM stock_move_line
                WHERE picking_id IN (
                    SELECT id FROM stock_picking WHERE origin LIKE 'S0%'
                );
            """)
            self.env.cr.execute("""
                DELETE FROM stock_picking WHERE origin LIKE 'S0%';
            """)
            self.env.cr.commit();
        #purchase-->purchase
        if self.purchase_and_transfer:
            purchase_orders = self.env['purchase.order'].search([])
            for order in purchase_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            purchase_orders.unlink()
        #purchase-->purchase_and_all_transfers
        if self.purchase_and_transfer:
            purchase_orders = self.env['purchase.order'].search([])
            for order in purchase_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            purchase_orders.unlink()

            self.env.cr.execute("""
                DELETE FROM stock_move_line
                WHERE picking_id IN (
                    SELECT id FROM stock_picking WHERE origin LIKE 'P0%'
                );
            """)
            self.env.cr.execute("""
                DELETE FROM stock_picking WHERE origin LIKE 'P0%';
            """)
            self.env.cr.commit()
        #inventory-->inventory_only_transfer
        if self.inventory_only_transfer:
            self.env.cr.execute("""
                    DELETE FROM stock_move_line;
                """)
            self.env.cr.execute("""
                    DELETE FROM stock_move;
                """)
            self.env.cr.commit()
            stock_pickings = self.env['stock.picking'].search([])
            for picking in stock_pickings:
                if picking.state not in ['draft']:
                    picking.write({'state': 'draft'})
            stock_pickings.unlink()
        #project-->project_tasks_timesheets
        if self.project_tasks_timesheets:
            timesheets = self.env['account.analytic.line'].search([])
            timesheets.unlink()
            tasks = self.env['project.task'].search([])
            tasks.unlink()
            projects_updates = self.env['project.update'].search([])
            projects_updates.unlink()
            projects = self.env['project.project'].search([])
            projects.unlink()
        #project-->only_task_timesheets
        if self.only_task_timesheets:
            timesheets = self.env['account.analytic.line'].search([])
            timesheets.unlink()
            tasks = self.env['project.task'].search([])
            tasks.unlink()
        #customer-->vendor&customer
        if self.customers_vendors:
            #for customer
            sale_orders = self.env['sale.order'].search([])
            for order in sale_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            sale_orders.unlink()
            self.env.cr.execute("""
                DELETE FROM stock_move_line
                WHERE picking_id IN (
                    SELECT id FROM stock_picking WHERE origin LIKE 'S0%'
                );
            """)
            self.env.cr.execute("""
                DELETE FROM stock_picking WHERE origin LIKE 'S0%';
            """)
            self.env.cr.commit();
            #for vendor
            purchase_orders = self.env['purchase.order'].search([])
            for order in purchase_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            purchase_orders.unlink()
            self.env.cr.execute("""
                DELETE FROM stock_move_line
                WHERE picking_id IN (
                    SELECT id FROM stock_picking WHERE origin LIKE 'P0%'
                );
            """)
            self.env.cr.execute("""
                DELETE FROM stock_picking WHERE origin LIKE 'P0%';
            """)
            self.env.cr.execute("""
                DELETE FROM account_move;
            """)
            self.env.cr.execute("""
                DELETE FROM account_move_line;
            """)
            self.env.cr.commit()
            active_user_partners = self.env['res.users'].search([('active', '=', True)]).mapped('partner_id')
            company_partners = self.env['res.company'].search([]).mapped('partner_id')
            customer_vendor = self.env['res.partner'].search([])
            partners_to_delete = customer_vendor - active_user_partners - company_partners
            partners_to_delete.unlink()
        # manufacturing-->bom_manufacturing_orders
        if self.bom_manufacturing_orders:
            bom_records = self.env['mrp.bom'].search([])
            manufacturing_orders = self.env['mrp.production'].search([])
            for order in manufacturing_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            manufacturing_orders.unlink()
            bom_records.unlink()
        #manufacturing-->only_manufacturing_orders
        if self.only_manufacturing_orders:
            manufacturing_orders = self.env['mrp.production'].search([])
            for order in manufacturing_orders:
                if order.state not in ['cancel']:
                    order.write({'state': 'cancel'})
            manufacturing_orders.unlink()
        #accounting-->invoicing_payments_journalentries
        # if self.invoicing_payments_journalentries:
        #     #to delete invoices and journal entries
        #     cust_invoice = self.env['account.move'].search([])
        #     for cust in cust_invoice:
        #         if cust.state not in ['draft']:
        #             cust.button_draft()
        #     cust_invoice.unlink()

        #     #to delete payments
        #     payments = self.env['account.payment'].search([])
        #     payments.unlink()
        #accounting-->only_journal_entries
        # if self.only_journal_entries:
        #     cust_invoice = self.env['account.move'].search([])
        #     for cust in cust_invoice:
        #         if cust.state not in ['draft']:
        #             cust.button_draft()
        #     cust_invoice.unlink()

