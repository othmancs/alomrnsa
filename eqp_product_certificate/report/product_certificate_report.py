# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCertificateReport(models.Model):
    _name = "product.certificate.report"
    _description = "Product certificate Statistics"
    _auto = False
    _rec_name = 'certificate_id'
    _order = 'certificate_id desc'

    # **** Product Certificate fields ****
    certificate_id = fields.Many2one('product.certificate', string='Certificate', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible user', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    start_date = fields.Date(string="Start Date", readonly=True)
    expiration_date = fields.Date(string="Expiration Date", readonly=True)
    traffic_light = fields.Selection([('red', 'Red'), ('yellow', 'Yellow'), ('green', 'Green')], string='Traffic Light',
                                    readonly=True)
    state = fields.Selection([('pre-active', 'Pre-Active'), ('active', 'Active'), ('expired', 'Expired')],
                             string='Status', readonly=True)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority',
                                readonly=True)
    stage_id = fields.Many2one('product.certificate.stage', string='Stage', readonly=True)

    _depends = {
        'product.certificate': [
            'name', 'company_id', 'user_id', 'product_id', 'start_date', 'expiration_date', 'priority',
        ],
        'res.company': ['product_certificate_days_to_red', 'product_certificate_days_to_yellow'],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
            SELECT
                pc.id AS id,
                pc.id AS certificate_id,
                company.id AS company_id,
                pc.user_id AS user_id,
                pc.product_id AS product_id,
                product.product_tmpl_id AS product_tmpl_id,
                template.categ_id AS product_categ_id,
                pc.start_date AS start_date,
                pc.expiration_date AS expiration_date,
                CASE
                    WHEN (pc.expiration_date - CURRENT_DATE) <= company.product_certificate_days_to_red THEN 'red'
                    WHEN (pc.expiration_date - CURRENT_DATE) <= company.product_certificate_days_to_yellow THEN 'yellow'
                    ELSE 'green'
                END AS traffic_light,
                CASE
                    WHEN pc.expiration_date < CURRENT_DATE THEN 'expired'
                    WHEN pc.start_date > CURRENT_DATE THEN 'pre-active'
                    ELSE 'active'
                END AS state,
                COALESCE(pc.priority, '0') AS priority,
                pc.stage_id AS stage_id
        '''

    @api.model
    def _from(self):
        return '''
            FROM product_certificate AS pc
                LEFT JOIN res_company company ON pc.company_id = company.id
                LEFT JOIN product_product product ON product.id = pc.product_id
                LEFT JOIN product_template template ON template.id = product.product_tmpl_id
        '''

    @api.model
    def _where(self):
        return '''
            WHERE pc.active
                AND pc.company_id = {company_id}
        '''.format(company_id=self.env.company.ids[0])
