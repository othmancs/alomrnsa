#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class Portal(models.Model):
    _name = 'portal.portal'

    sequence = fields.Integer(default=999)
    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related="model_id.model")
    url = fields.Char(compute='_compute_url')
    full_url = fields.Char(compute='_compute_url')
    count = fields.Integer(default=0)
    list_fields = fields.One2many('portal.view', 'list_id', string='List Fields')
    form_fields = fields.One2many('portal.view', 'form_id', string='Form Fields')
    button_ids = fields.One2many('portal.view.button', 'portal_id', string='Button')
    access_ids = fields.One2many('portal.access', 'portal_id', string='Access')
    list_color_ids = fields.One2many('portal.list.color', 'portal_id', string='List Colors')
    domain = fields.Char()
    chatter = fields.Boolean()
    action_id = fields.Many2one('ir.actions.act_window', string="Action")

    _sql_constraints = [('name_model_id', 'unique (model_id)', "Model already exists!"), ]

    def check_portal_access_rights(self, operation='read'):

        if self.env.user == self.env.ref('base.user_admin'):
            return True

        assert operation in ('read', 'write', 'create', 'delete'), 'Invalid access mode'

        access_line = self.access_ids.filtered(lambda a: a.user_id == self.env.user)

        if not access_line:
            return False

        operation = 'allow_' + operation
        return access_line[operation]

    @api.constrains('domain')
    def _check_domain(self):
        eval_context = {
            'uid': self.env.uid,
            'user': self.env.user,
        }

        for rec in self:
            try:
                safe_eval(rec.domain or '[]', eval_context)
            except Exception as e:
                error = "This domain is syntactically not correct:\n %s", e
                raise ValidationError(error)

    def get_eval_context(self):
        return {
            'uid': self.env.uid,
            'user': self.env.user,
        }

    def get_default_values(self):
        vals = {}
        for line in self.form_fields:
            field_value = ''
            default_value = self.env[self.model_name].default_get([line.field_name])
            if line.field_name in default_value:
                field_value = self.check_portal_format(line, default_value[line.field_name])
            vals[line.field_name] = field_value
        return vals

    def get_fields_attrs_readonly(self, record):
        vals = {}
        for line in self.form_fields:
            readonly = False
            if line.attrs_readonly:
                domain = safe_eval(line.attrs_readonly or '[]', self.get_eval_context())
                if record and record in self.env[self.model_name].search(domain):
                    readonly = True
            vals[line.field_id.name] = readonly
        return vals

    def get_fields_attrs_invisible(self, record):
        vals = {}
        for line in self.form_fields:
            readonly = True
            if line.attrs_invisible:
                domain = safe_eval(line.attrs_invisible or '[]', self.get_eval_context())
                if record and record in self.env[self.model_name].search(domain):
                    readonly = False
            vals[line.field_id.name] = readonly
        return vals

    def get_buttons_attrs_invisible(self, record):
        vals = {}
        for line in self.button_ids:
            readonly = False
            if line.attrs_invisible:
                domain = safe_eval(line.attrs_invisible or '[]', self.get_eval_context())
                if record and record in self.env[self.model_name].search(domain):
                    readonly = True
            vals[line.action] = readonly
        return vals

    def get_form_fields(self):
        vals = []
        for line in self.form_fields.sudo().filtered(lambda l: l.ttype != 'one2many'):
            vals.append(line.field_id.name)
        return vals

    def reformat_record_values(self, values):
        for field in self.form_fields.sudo():
            if field.ttype == 'many2one' and values[field.field_id.name]:
                values[field.field_id.name] = int(values[field.field_id.name])
        return values

    def check_portal_format(self, field, value):
        field = field.field_id
        if not value:
            return ""
        elif field.ttype == 'many2one':
            res = value[0] if isinstance(value, list) else int(value)
        elif field.ttype == 'datetime':
            field_value = fields.Datetime.to_string(value)
            field_value = field_value.replace(' ', 'T')
            res = field_value
        elif field.ttype == 'date':
            res = fields.Date.to_string(value)
        elif field.ttype != 'boolean' and value == False:
            res = ""
        else:
            res = value
        return res

    def reformat_lines_values(self, table_fields, values):
        lst = []
        for val in values:
            res = {}
            val = val[2]
            if not isinstance(val, dict):
                continue
            for field in table_fields:
                res[field.field_id.name] = self.check_portal_format(field, val[field.field_id.name])
            lst.append(res)

        return lst

    def get_onchange_values(self, field_name, values):
        field = self.form_fields.sudo().filtered(lambda f: f.field_id.name == field_name).sudo()
        if not field:
            return {}
        self.reformat_record_values(values)

        record = self.env[self.model_name]

        if values['id']:
            record = record.browse(int(values['id']))

        record = record.sudo()

        values.pop('id')

        field_onchange = record._onchange_spec()
        val = record.onchange(values, field_name, field_onchange)
        res = {}
        for item in val['value']:
            if item in self.form_fields.mapped('field_name'):
                field_id = self.form_fields.sudo().filtered(lambda f: f.field_id.name == item).sudo()
                # handel one2many lines
                lst = []
                if field_id.field_id.ttype == 'one2many':
                    lst.append(self.reformat_lines_values(field_id.table_lines, val['value'][item]))
                    lst.append(self.get_lines(item))
                    res[item] = lst
                else:
                    res[item] = self.check_portal_format(field_id, val['value'][item])
        return res

    def get_lines(self, field):
        field_id = self.form_fields.sudo().filtered(lambda f: f.field_id.name == field).sudo()
        list = []
        val = {}
        field_name = field

        for line in field_id.table_lines:
            selection = []

            if line.field_id.ttype in ['many2one', 'many2many']:
                for item in self.env[line.field_id.relation].sudo().search([]):
                    selection.append({'key': item.id, 'val': item.name})

            elif line.field_id.ttype == 'selection':
                for item in \
                        self.env[line.field_id.relation].fields_get([line.field_id.name])[
                            line.field_id.name][
                            'selection']:
                    selection.append({'key': item[0], 'val': item[0]})

            sub_val = {
                'type': self.check_type(line.field_id.ttype),
                'name': line.field_id.name,
                'selection': selection
            }
            list.append(sub_val)
        val[field_name] = list
        return list

    def check_type(self, ttype):
        if ttype in ['char', 'text', 'float']:
            return 'text'
        if ttype in ['integer']:
            return 'number'
        elif ttype in ['date']:
            return 'date'
        elif ttype in ['datetime']:
            return 'datetime-local'
        elif ttype in ['many2one', 'selection']:
            return 'select'
        elif ttype in ['boolean']:
            return 'checkbox'
        elif ttype in ['one2many']:
            return 'one2many'
        else:
            return 'text'

    @api.depends('model_id')
    def _compute_url(self):
        for rec in self:
            rec.url, rec.full_url = False, False
            if rec.model_id:
                web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                rec.url = "/portal/" + rec.model_id.model
                rec.full_url = web_base_url + rec.url
