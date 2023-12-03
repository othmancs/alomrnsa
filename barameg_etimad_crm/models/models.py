# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import requests
import json
from datetime import datetime
import multiprocessing


def converted_date(date_string):
    if not date_string:
        return False
    format_string = "%Y-%m-%dT%H:%M:%S"
    try:
        date_object = datetime.strptime(date_string.split('.')[0], format_string)
        if date_object.year < 1970:
            print(date_object)
            return False
    except ValueError as e:
        return False
    output_format = "%Y-%m-%d %H:%M:%S"
    return date_object.strftime(output_format)


def call_monafasat_endpoint(endpoint_url, client_id, client_key, params=None):
    headers = {
        "X-Etimad-Client-Id": client_id,
        "X-Etimad-Client-Key": client_key,
    }
    try:
        response = requests.get(endpoint_url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error during request: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")
    return data.get('data')


class MonafasatType(models.Model):
    _name = 'monafasat.type'
    _description = 'Monafasat Types'

    monafasat_id = fields.Char()
    name = fields.Char()


class MonafasatAgency(models.Model):
    _inherit = 'res.partner'

    monafasat_id = fields.Char()

    def get_updates(self):
        client_id = self.env['ir.config_parameter'].sudo().get_param('client_id')
        client_key = self.env['ir.config_parameter'].sudo().get_param('client_key')
        if not client_key and not client_key:
            return
        result = call_monafasat_endpoint("https://barameg.co/api/etimad/agencies", client_id, client_key)
        result_records = result.get('records') if result else None
        if result_records:
            existing_records = self.search([])
            existing_monafasat_ids = list(map(
                lambda rec: rec.monafasat_id,
                existing_records
            ))
            records_to_create = list(filter(lambda rec: rec.get('monafasat_id') not in existing_monafasat_ids, result_records))
            records_to_create = list(map(lambda rec: {
                'monafasat_id': rec.get('monafasat_id'),
                'name': rec.get('name'),
            }, records_to_create))
            self.create(records_to_create)


class MonafasatActivity(models.Model):
    _name = 'monafasat.activity'
    _description = 'Monafasat Activities'

    parent_id = fields.Many2one('monafasat.activity')
    name = fields.Char()
    monafasat_id = fields.Char()

    def get_updates(self):
        client_id = self.env['ir.config_parameter'].sudo().get_param('client_id')
        client_key = self.env['ir.config_parameter'].sudo().get_param('client_key')
        if not client_key and not client_key:
            return
        result = call_monafasat_endpoint("https://barameg.co/api/etimad/activities", client_id, client_key)

        result_records = result.get('records') if result else None
        if result_records:
            existing_records = self.search([])
            existing_monafasat_ids = list(map(
                lambda rec: rec.monafasat_id,
                existing_records
            ))
            records_to_create = list(
                filter(lambda rec: rec.get('monafasat_id') not in existing_monafasat_ids, result_records))
            records_to_create = list(map(lambda rec: {
                'monafasat_id': rec.get('monafasat_id'),
                'name': rec.get('name'),
            }, records_to_create))
            self.create(records_to_create)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_id = fields.Char()
    client_key = fields.Char()

    def get_values(self):
        res = super().get_values()
        client_id = self.env['ir.config_parameter'].sudo().get_param('client_id')
        res.update(client_id=client_id)
        client_key = self.env['ir.config_parameter'].sudo().get_param('client_key')
        res.update(client_key=client_key)
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('client_id', self.client_id)
        self.env['ir.config_parameter'].sudo().set_param('client_key', self.client_key)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    etimad_tender_id = fields.Many2one('monafasat.tender')

    def visit_source_link(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': '_blank',
            'url': f'https://tenders.etimad.sa/Tender/DetailsForVisitor?STenderId={self.etimad_tender_id.tender_id_string}',
        }

class MonafasatTender(models.Model):
    _name = 'monafasat.tender'
    _description = 'Monafasat Tenders'

    monafasat_id = fields.Char()
    reference_number = fields.Char(string='Ref #')
    name = fields.Char(string='Name')
    tender_number = fields.Char(string='Tender #')
    agency_code = fields.Char(string='Agency Code')
    branch_id = fields.Char(string='Branch ID')
    branch_name = fields.Char(string='Branch Name')
    agency = fields.Many2one(
        'res.partner',
        string='Agency',
        compute='_compute_tender_agency',
    )
    related_agency = fields.Many2one(
        'res.partner',
        string='Agency',
        related='agency',
        store=True
    )
    agency_name = fields.Char(string='Agency Name')
    tender_id_string = fields.Char(string='Tender ID String')
    tender_status_id = fields.Char(string='Tender Status ID')
    tender_status_id_string = fields.Char(string='Tender Status ID string')
    tender_status_name = fields.Char(string='Tender Status')
    tender_type_id = fields.Char(string='Tender Type ID')
    tender_type_name = fields.Char(string='Tender Type')
    type = fields.Many2one(
        'monafasat.type',
        string='Tender Type',
        compute='_compute_tender_type',
    )
    related_type = fields.Many2one(
        'monafasat.type',
        string='Tender Type',
        related='type',
        store=True
    )
    technical_organization_id = fields.Char(string='Organization ID')
    condetional_booklet_price = fields.Float(string='Booklet Price')
    monafasat_created_at = fields.Datetime(string='Created At')
    last_enqueries_date = fields.Datetime(string='Enquiries Deadline')
    last_offer_presentation_date = fields.Datetime(string='Offers Deadline')
    offers_opening_date = fields.Datetime(string='Offers Opening At')
    tender_activity_name = fields.Char(string='Tender Activity Name')
    activity = fields.Many2one(
        'monafasat.activity',
        string='Tender Activity Name',
        compute='_compute_tender_activity',
    )
    related_activity = fields.Many2one(
        'monafasat.activity',
        string='Tender Activity Name',
        related='activity',
        store=True
    )
    tender_activity_id = fields.Char(string='Tender Activity ID')
    submission_date = fields.Datetime(string='Published At')
    financial_fees = fields.Float(string='Financial Fees')
    invitation_cost = fields.Float(string='Invitation Cost')
    total_fees = fields.Float(
        string='Total Fees',
        compute='_compute_total_fees',
    )
    related_total_fees = fields.Float(
        string='Total Fees',
        related='total_fees',
        store=True  # Set store attribute to True if you want to store the related field
    )
    buying_cost = fields.Float(string='Buying Cost')
    has_invitations = fields.Boolean(string='Has Invitations')
    opportunity = fields.Many2one(
        'crm.lead',
        compute='_compute_has_opportunity'
    )
    related_opportunity = fields.Many2one(
        'crm.lead',
        related='opportunity',
        stored=True
    )

    @api.depends('financial_fees', 'condetional_booklet_price')
    def _compute_has_opportunity(self):
        for rec in self:
            opportunity = self.env['crm.lead'].search([
                ['etimad_tender_id', '=', rec.id]
            ], limit=1)
            rec.opportunity = opportunity.id if opportunity else False

    @api.depends('financial_fees', 'condetional_booklet_price')
    def _compute_total_fees(self):
        print(self, "compute fees")
        for rec in self:
            rec.total_fees = rec.financial_fees + rec.condetional_booklet_price

    @api.depends('agency_name')
    def _compute_tender_agency(self):
        for rec in self:
            agency = self.env['res.partner'].search([
                ['name', '=', rec.agency_name]
            ])
            rec.agency = agency[0].id if agency else False

    @api.depends('tender_activity_name')
    def _compute_tender_activity(self):
        for rec in self:
            activity = self.env['monafasat.activity'].search([
                ['name', '=', rec.tender_activity_name]
            ])
            rec.activity = activity[0].id if activity else False

    @api.depends('tender_type_name', 'tender_type_id')
    def _compute_tender_type(self):
        for rec in self:
            types = self.env['monafasat.type'].search([
                ['name', '=', rec.tender_type_name]
            ])
            if not types:
                types = types.create({
                    'name': rec.tender_type_name,
                    'monafasat_id': rec.tender_type_id
                })
            rec.type = types[0].id if types else False

    def get_updates(self):
        client_id = self.env['ir.config_parameter'].sudo().get_param('client_id')
        client_key = self.env['ir.config_parameter'].sudo().get_param('client_key')
        if not client_key and not client_key:
            return
        last_record = self.search([], limit=1, order='submission_date desc')
        page = 1
        url = f"https://barameg.co/api/etimad/tenders?from={last_record.submission_date if last_record else ''}"
        records = []

        result = call_monafasat_endpoint(f'{url}&page={page}', client_id, client_key)
        result_count = result.get('count') if result else None
        result_records = result.get('records') if result else None
        if result_count and result_records:
            records += result_records
        while result_records:
            page = page + 1
            result = call_monafasat_endpoint(f'{url}&page={page}', client_id, client_key)
            result_count = result.get('count') if result else None
            result_records = result.get('records') if result else None
            if result_count and result_records:
                records += result_records

        agencies_names = list(set(filter(None, map(lambda r: r.get('agency_name'), records))))
        agencies = self.env['res.partner'].search([
            ['name', 'in', agencies_names]
        ])
        if len(agencies) < len(agencies_names):
            self.env['res.partner'].get_updates()

        activities_names = list(set(filter(None, map(lambda r: r.get('tender_activity_name'), records))))
        activities = self.env['monafasat.activity'].search([
            ['name', 'in', activities_names]
        ])
        if len(activities) < len(activities_names):
            self.env['monafasat.activity'].get_updates()

        existing_records = self.search([])
        existing_monafasat_ids = list(map(
            lambda r: r.monafasat_id,
            existing_records
        ))
        records = list(
            filter(lambda r: r.get('monafasat_id') not in existing_monafasat_ids, records))

        records_to_create = []
        for rec in records:
            if str(rec.get('monafasat_id')) not in existing_monafasat_ids:
                records_to_create.append({
                    "monafasat_id": rec.get('monafasat_id'),
                    "reference_number": rec.get('reference_number'),
                    "name": rec.get('name'),
                    "tender_number": rec.get('tender_number'),
                    "agency_code": rec.get('agency_code'),
                    "branch_id": rec.get('branch_id'),
                    "branch_name": rec.get('branch_name'),
                    "agency_name": rec.get('agency_name'),
                    "tender_id_string": rec.get('tender_id_string'),
                    "tender_status_id": rec.get('tender_status_id'),
                    "tender_status_id_string": rec.get('tender_status_id_string'),
                    "tender_status_name": rec.get('tender_status_name'),
                    "tender_type_id": rec.get('tender_type_id'),
                    "tender_type_name": rec.get('tender_type_name'),
                    "technical_organization_id": rec.get('technical_organization_id'),
                    "condetional_booklet_price": rec.get('condetional_booklet_price'),
                    "monafasat_created_at": converted_date(rec.get('monafasat_created_at')),
                    "last_enqueries_date": converted_date(rec.get('last_enqueries_date')),
                    "last_offer_presentation_date": converted_date(rec.get('last_offer_presentation_date')),
                    "offers_opening_date": converted_date(rec.get('offers_opening_date')),
                    "tender_activity_name": rec.get('tender_activity_name'),
                    "tender_activity_id": rec.get('tender_activity_id'),
                    "submission_date": converted_date(rec.get('submission_date')),
                    "financial_fees": rec.get('financial_fees'),
                    "invitation_cost": rec.get('invitation_cost'),
                    "buying_cost": rec.get('buying_cost'),
                    "has_invitations": rec.get('has_invitations'),
                })
        self.create(records)

    def create_opportunity(self):
        action = {
            'name': 'Create Opportunity',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',  # Replace with your actual model name
            'view_mode': 'form',
            'view_id': False,  # You can set the specific form view ID if needed
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_name': self.name,  # Set default values for fields
                'default_partner_id': self.related_agency.id,  # Set default values for fields
                'default_etimad_tender_id': self.id,  # Set default values for fields
                # Add other field default values as needed
            },
        }
        return action

    def visit_source_link(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': '_blank',
            'url': f'https://tenders.etimad.sa/Tender/DetailsForVisitor?STenderId={self.tender_id_string}',
        }
