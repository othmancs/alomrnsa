# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, models, fields, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class ProductCertificate(models.Model):
    _name = 'product.certificate'
    _description = 'Product Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code'

    active = fields.Boolean(default=True, tracking=True, string='Active',
                            help="Set active to false to hide the Certificate without removing it.")
    can_edit = fields.Boolean(string='Can Edit', default=True, tracking=True,
                              help="Set can_edit to True to edit the certificate.")
    name = fields.Char(string='Certificate Name', required=True, tracking=True, help="Name of the certificate")
    code = fields.Char(string='Certificate Code', required=True, tracking=True,
                       help="Code of the certificate (if apply)")
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')

    description = fields.Text(string='Certificate description', required=True, help="Add a brief description of the "
                                                                                    "certificate")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company,
                                 readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible user', index=True, required=True, ondelete='cascade',
                              default=lambda self: self.env.user, tracking=True,
                              help="Assign a responsible user for this certificate.")
    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True, check_company=True,
                                 ondelete='restrict', help="Select the product that this certificate applies.")
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id',
                                      store=True, index=True)
    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.context_today,
                             tracking=True, help="The issue date of the certificate.")
    expiration_date = fields.Date(string="Expiration Date", required=True, tracking=True,
                                  help="The expiration date of the certificate.")
    certificate_file = fields.Binary(string="Certificate (PDF) File", help="PDF file which contain the certificate..")
    traffic_light = fields.Selection([('red', 'Red'), ('yellow', 'Yellow'), ('green', 'Green')], string='Traffic Light',
                                     compute='_compute_traffic_light', readonly=True, search='_traffic_light_search')
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority',
                                help="Assign a priority to your Certificates and manage them by urgency level.")
    state = fields.Selection([('pre-active', 'Pre-Active'), ('active', 'Active'), ('expired', 'Expired')],
                             string='Status', compute='_compute_state', search='_state_search', readonly=True)
    stage_required = fields.Boolean(string='Required Stage', readonly=True,
                                    related='company_id.product_certificate_stage_required')
    stage_id = fields.Many2one('product.certificate.stage', string='Stage', index=True, tracking=True,
                               ondelete='restrict',
                               help="If applicable, use Product Certificate Stages to control your own custom flow.")
    tag_ids = fields.Many2many('product.certificate.tag', 'product_certificate_tag_tag_rel', 'certificate_id', 'tag_id',
                               string='Tags', tracking=True, ondelete='restrict',
                               help="Classify and analyze your certificates categories "
                                    "like: CAN, CSA, UL, ANSI, IEC, and ISO")

    _sql_constraints = [('code_unique',
                         'unique(code, product_id, company_id)',
                         'A unique certificate Code per product per company.'),
                        ('check_dates', 'check(expiration_date > start_date)',
                         'The expiration date must be greater that the start Date')]

    @api.constrains('start_date', 'expiration_date')
    def _check_valid_dates(self):
        for record in self:
            if record.start_date and record.expiration_date:
                if record.start_date >= record.expiration_date:
                    raise ValidationError("The Expiration Date must be greater than the Start Date.")

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for certificate in self:
            name = certificate.name or ''
            code = certificate.code or ''
            certificate.display_name = f'[{code}] {name}'

    @staticmethod
    def check_search_operators(operator, value):
        supported_operators = ['in', 'not in', '=', '!=']

        if operator not in supported_operators:
            return expression.TRUE_DOMAIN

        if (value is False and operator == '!=') or (value is True and operator == '=') or (value == [] and operator == 'not in'):
            return expression.TRUE_DOMAIN
        elif (value is False and operator == '=') or (value is True and operator == '!='):
            return expression.FALSE_DOMAIN

        return None

    @api.depends('expiration_date', 'company_id.product_certificate_days_to_red',
                 'company_id.product_certificate_days_to_yellow')
    def _compute_traffic_light(self):
        today = fields.Date.today()
        for certificate in self:
            days_to_red = certificate.company_id.product_certificate_days_to_red
            days_to_yellow = certificate.company_id.product_certificate_days_to_yellow
            # Check policies are set
            if not (days_to_red and days_to_yellow):
                raise ValidationError(
                    "Please configure the Days for Red and Days for Yellow (>1 Day) in the Configuration Panel "
                    "(Inventory module [Product Certificates section]).")
            # Check if there is an Expiration date set (No new record)
            expiration_date = certificate.expiration_date
            days_to_expire = (expiration_date - today).days if expiration_date else 0

            certificate.traffic_light = 'red' if days_to_expire <= days_to_red else \
                'yellow' if days_to_expire <= days_to_yellow else 'green'

    def _traffic_light_search(self, operator, value):

        def get_domain(min_days_num, max_days_num, is_or_operator):

            if min_days_num and max_days_num:
                min_date = today + timedelta(days=min_days_num)
                max_date = today + timedelta(days=max_days_num)
                if is_or_operator:
                    domain = ['|', ('expiration_date', '<=', max_date), ('expiration_date', '>', min_date)]
                else:
                    domain = ['&', ('expiration_date', '<=', max_date), ('expiration_date', '>', min_date)]
            elif min_days_num:
                min_date = today + timedelta(days=min_days_num)
                domain = [('expiration_date', '>', min_date)]
            elif max_days_num:
                max_date = today + timedelta(days=max_days_num)
                domain = [('expiration_date', '<=', max_date)]
            else:
                domain = [()]
            return domain

        # Validate if there is a boolean operator
        op_domain = self.check_search_operators(operator, value)
        if op_domain is not None:
            return op_domain

        company = self.company_id or self.env.company
        days_to_red = company.product_certificate_days_to_red
        days_to_yellow = company.product_certificate_days_to_yellow

        today = fields.Date.today()
        min_days = 0
        max_days = 0
        or_operator = False

        if operator == '=':
            if value == 'green':
                min_days = days_to_yellow
            elif value == 'yellow':
                max_days = days_to_yellow
                min_days = days_to_red
            elif value == 'red':
                max_days = days_to_red
        elif operator == '!=':
            if value == 'green':
                max_days = days_to_yellow
            elif value == 'yellow':
                min_days = days_to_yellow
                max_days = days_to_red
                or_operator = True
            elif value == 'red':
                min_days = days_to_red

        elif operator in ('in', 'not in'):
            if (value == ['red'] and operator == 'in') or ('green' and 'yellow' in value and operator == 'not in'):
                max_days = days_to_red
            elif ('red' and 'yellow' in value and operator == 'in') or (value == ['green'] and operator == 'not in'):
                max_days = days_to_yellow
            elif (value == ['yellow'] and operator == 'in') or ('green' and 'red' in value and operator == 'not in'):
                min_days = days_to_red
                max_days = days_to_yellow
            elif (value == ['green'] and operator == 'in') or ('red' and 'yellow' in value and operator == 'not in'):
                min_days = days_to_yellow
            elif ('green' and 'yellow' in value and operator == 'in') or (value == ['red'] and operator == 'not in'):
                min_days = days_to_red
            elif ('green' and 'red' in value and operator == 'in') or (value == ['yellow'] and operator == 'not in'):
                max_days = days_to_red
                min_days = days_to_yellow
                or_operator = True
        return get_domain(min_days, max_days, or_operator)

    def _compute_state(self):
        today = fields.Date.today()
        for certificate in self:
            if certificate.expiration_date < today:
                certificate.state = 'expired'  # Certificate has expired
            elif certificate.start_date > today:
                certificate.state = 'pre-active'  # Certificate is not yet active
            else:
                certificate.state = 'active'  # Certificate is currently active

    def _state_search(self, operator, value):

        def get_domain(expired, pre_active, active, apply_or_operator):
            today = fields.Date.today()
            domain = []
            if apply_or_operator:
                domain.append('|')
            if expired:
                domain.append(('expiration_date', '<', today))
            if pre_active:
                domain.append(('start_date', '>', today))
            if active:
                domain.extend(['&', ('start_date', '<=', today), ('expiration_date', '>=', today)])
            if not domain:
                domain = [()]
            return domain

        # Validate if there is a boolean operator
        op_domain = self.check_search_operators(operator, value)
        if op_domain is not None:
            return op_domain

        if operator in ('=', '!='):
            is_expired = True if value == 'expired' else False
            is_pre_active = True if value == 'pre-active' else False
            is_active = True if value == 'active' else False
        elif operator in ('in', 'not in'):
            is_expired = 'expired' in value
            is_pre_active = 'pre-active' in value
            is_active = 'active' in value

        # Check special filter scenarios
        # IN All states
        if is_expired and is_pre_active and is_active and operator == 'in':
            return expression.TRUE_DOMAIN
        # NOT IN All states
        if is_expired and is_pre_active and is_active and operator == 'not in':
            return expression.FALSE_DOMAIN

        # Activating Or operator when both val is a list and has more than 1 state in Values
        or_operator = isinstance(value, list) and len(value) > 1

        return get_domain(is_expired, is_pre_active, is_active, or_operator)

    def certificate_can_edit_control(self):
        for certificate in self:
            certificate.can_edit = not certificate.can_edit

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        chosen_code = default.get('code') if default else ''
        new_name = chosen_name or _('%s (copy)', self.name)
        new_code = chosen_code or _('%s (copy)', self.code)
        default = dict(default or {}, name=new_name, code=new_code)
        return super(ProductCertificate, self).copy(default)


class ProductCertificateTag(models.Model):
    _name = 'product.certificate.tag'
    _description = 'Product Certificate Tags'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    active = fields.Boolean(default=True,  string='Active',
                            help="Set active to false to hide the Certificate Tag without removing it.")
    name = fields.Char(string='Tag Name', required=True, tracking=True, help="Name of the Tag")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company,
                                 readonly=True)
    description = fields.Text(string='Tag description', required=True, help="Add a brief description of the Tag.")
    color = fields.Integer("Color", default=0, help="Select a color to visually associate with for quick and easy"
                                                    " identification.")

    _sql_constraints = [('name_unique',
                         'unique(name, company_id)',
                         'A unique Tag per company.')]

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        new_name = chosen_name or _('%s (copy)', self.name)
        default = dict(default or {}, name=new_name)
        return super(ProductCertificateTag, self).copy(default)


class ProductCertificateStage(models.Model):
    _name = 'product.certificate.stage'
    _description = 'Product Certificate Stages'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    active = fields.Boolean(default=True,  string='Active',
                            help="Set active to false to hide the Certificate Stage without removing it.")
    name = fields.Char(string='Stage Name', required=True, tracking=True, help="Name of the Stage")
    sequence = fields.Integer(string='Sequence', required=True, default=1, tracking=True,
                              help="Sequence to order the stages.")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company,
                                 readonly=True)
    description = fields.Text(string='Stage description', help="Add a brief description of the Stage.")
    color = fields.Integer("Color", default=0, help="Select a color to visually associate with for quick and easy"
                                                    " identification.")

    _sql_constraints = [('name_unique', 'unique(name, company_id)', 'A unique Stage Name per company.'),
                        ('sequence_unique', 'unique(sequence, company_id)',
                         'A unique Stage sequence Number per company.')]

    @api.constrains('sequence')
    def _check_positive_sequence(self):
        for record in self:
            if record.sequence < 0:
                raise ValidationError("The value of Sequence must be greater than 0.")

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        chosen_sequence = default.get('sequence') if default else 0
        new_name = chosen_name or _('%s (copy)', self.name)
        new_sequence = chosen_sequence or _(self.sequence) + 10
        default = dict(default or {}, name=new_name, sequence=new_sequence)
        return super(ProductCertificateStage, self).copy(default)
