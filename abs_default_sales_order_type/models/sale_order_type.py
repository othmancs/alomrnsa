# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _

#Class is Extended for new feature for create new menu of sale.type model.
class SaleOrderTypes(models.Model):
    _name = "sale.type"
    _rec_name = "sale_order_type"
    _description = "Sale Type" 

    sale_order_type = fields.Char(string='Sale Order Type' ,required=1)  
    payment_term_id = fields.Many2one('account.payment.term',string='Payment Terms')    
    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse', required=True)  
    incoterm = fields.Many2one('account.incoterms',string='Incoterms') 
    picking_policy = fields.Selection([('direct', 'Deliver each product when available'),('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, default='direct')
    user_id = fields.Many2one('res.users',string='Salesperson',required=False, default=lambda self: self.env.user) 
    tag_ids = fields.Many2many('crm.tag', 'sale_type_tag_rel', 'lead_id', 'sale_type_id', 'Tags')
    team_id = fields.Many2one('crm.team',string='Sales Team')   
    client_order_ref = fields.Char(string='Customer Reference')  
    origin = fields.Char(string='Source Document')  
    campaign_id = fields.Many2one('utm.campaign',string='Campaign')  
    medium_id = fields.Many2one('utm.medium',string='Medium')  
    source_id = fields.Many2one('utm.source',string='Source')  
    opportunity_id = fields.Many2one('crm.lead',string='Opportunity')  

