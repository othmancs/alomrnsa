import base64
import logging
import datetime
import werkzeug

import odoo.http as http
from odoo.http import request
from odoo import http, fields
from odoo.tools.safe_eval import safe_eval
import base64

_logger = logging.getLogger(__name__)


class DynamicPortalController(http.Controller):

    def get_field_value(self, obj, field_str):

        field_value = obj[field_str]

        if obj._fields[field_str].type == 'many2one':

            rec_name = field_value._rec_name

            if field_value._rec_name == 'name':
                rec_name = field_value.name
            else:
                rec_name = self.get_field_value(field_value, rec_name)

            field_value = [field_value.id, rec_name]

        if obj._fields[field_str].type == 'datetime':
            if field_value:
                field_value = fields.Datetime.to_string(field_value)
                field_value = field_value.replace(' ', 'T')

        return field_value

    def check_type(self, ttype):
        if ttype in ['char', 'text', 'float']:
            return 'text'
        if ttype in ['integer']:
            return 'number'
        elif ttype in ['date']:
            return 'date'
        elif ttype in ['datetime']:
            return 'datetime-local'
        elif ttype in ['many2one']:
            return 'many2one'
        elif ttype in ['selection']:
            return 'many2one'
        elif ttype in ['many2many']:
            return 'many2many'
        elif ttype in ['boolean']:
            return 'checkbox'
        elif ttype in ['one2many']:
            return 'one2many'
        elif ttype in ['binary']:
            return 'file'
        else:
            return 'text'

    def get_input_types(self, fields):
        val = {}
        for line in fields:

            ttype = line.field_id.ttype
            field_name = line.field_id.name
            val[field_name] = self.check_type(ttype)

            if ttype == 'one2many':
                item_vals = self.get_input_types(line.table_lines)
                val[field_name] = item_vals

        return val

    def get_list_table(self, fields):
        val = {}
        for line in fields:

            ttype = line.field_id.ttype
            field_name = line.field_id.name

            if ttype == 'one2many':
                list = []
                for subline in line.table_lines:
                    # selection = self.get_selection_data(line.field_id.relation, False, line.table_lines)
                    selection = []

                    if subline.field_id.ttype in ['many2one']:
                        for item in request.env[subline.field_id.relation].sudo().search([]):
                            selection.append({'key': item.id, 'val': item.name})

                    elif subline.field_id.ttype == 'selection':
                        for item in \
                                request.env[line.field_id.relation].fields_get([subline.field_id.name])[
                                    subline.field_id.name][
                                    'selection']:
                            selection.append({'key': item[0], 'val': item[0]})

                    sub_val = {
                        'type': self.check_type(subline.field_id.ttype),
                        'name': subline.field_id.name,
                        'selection': selection
                    }
                    list.append(sub_val)

                val[field_name] = list

        return val

    def get_eval_context(self):
        return {
            'uid': request.env.uid,
            'user': request.env.user,
        }

    def get_selection_data(self, model, record, fields):

        val = {}
        for line in fields:
            ttype = line.field_id.ttype
            field_name = line.field_id.name

            if ttype in ['many2one', 'many2many']:
                relation = line.field_id.relation
                domain = safe_eval(line.domain or '[]', self.get_eval_context())
                item_vals = []
                for item in request.env[relation].sudo().search(domain):
                    selected = False
                    if record:
                        if item in record[field_name]:
                            selected = True
                    item_vals.append({'key': item.id, 'val': item.name, 'selected': selected})
                val[field_name] = item_vals

            if ttype == 'selection':
                selection = request.env[model].fields_get([field_name])[field_name]['selection']
                item_vals = []
                for item in selection:
                    selected = False
                    if record:
                        if record[field_name] == item[0]:
                            selected = True
                    item_vals.append({'key': item[0], 'val': item[1], 'selected': selected})
                val[field_name] = item_vals

            if ttype == 'one2many':
                item_vals = self.get_selection_data(line.field_id.relation, False, line.table_lines)
                val[field_name] = item_vals

        return val

    def prepare_record_data(self, record, fields):
        rec_name = record.name_get()[0][1]
        values = {
            'id': record.id,
            'rec_name': rec_name,
        }
        for line in fields:
            field_name = line.field_id.name

            if line.ttype == 'one2many':
                lst = []
                field_value = self.get_field_value(record, field_name)
                for rec in field_value:
                    lst.append(self.prepare_record_data(rec, line.table_lines))

                values[field_name] = lst
            else:
                field_value = self.get_field_value(record, field_name)
                values.update({field_name: field_value})

        return values

    def prepare_record_list(self, model, portal_view):
        """
        prepare record list
        """
        domain = safe_eval(portal_view.domain or '[]', self.get_eval_context())
        records = request.env[model].sudo().search(domain)

        values = []

        for record in records:
            values.append(self.prepare_record_data(record, portal_view.list_fields))

        return values

    def remove_duplicate(self, dict):
        res = {}
        for key, value in dict.items():
            if value not in res.values():
                res[key] = value
        return res

    def check_computed_fields(self, record):
        all_fields = record.fields_get(attributes=['depends'])
        all_fields = self.remove_duplicate(all_fields)
        for field, val in all_fields.items():
            if val['depends']:
                try:
                    record.sudo()._fields[field].compute_value(record.sudo())
                except Exception:
                    continue

    def reformate_values(self, values, form_fields):
        for line in form_fields:
            field_name = line.field_id.name
            if field_name in values and values[field_name] == '':
                values[field_name] = False

            elif line.field_id.ttype == 'many2one':
                values[field_name] = int(values[field_name])

            elif line.field_id.ttype == 'datetime':
                date_processing = values[field_name].replace('T', ' ')
                date_out = fields.Datetime.from_string(date_processing)
                values[field_name] = date_out

            elif line.field_id.ttype == 'binary':
                if not values[field_name]:
                    values.pop(field_name, None)
                else:
                    data = values[field_name].read()
                    values[field_name] = base64.b64encode(data)

            elif line.field_id.ttype == 'many2many':
                values_ids = list(int(x) for x in request.httprequest.form.getlist(field_name))
                if field_name in values:
                    values[field_name] = values_ids
                else:
                    values[field_name] = False
        return values

    def get_master_data(self, dict, fields, model):
        master_data = {key: value for (key, value) in dict.items() if '.' not in key}
        master_data = self.reformate_values(master_data, fields)
        master_data['model'] = model
        return master_data

    def get_lines_data(self, dict, fields):
        lines = {}
        index = 0
        for key, val in dict.items():
            if '.' in key:
                x = key.split('.')
                line = x[0]
                field = x[1]
                id = x[2]

                field_id = fields.filtered(lambda f: f.field_id.name == line)
                model = field_id.relation
                relation_field = field_id.field_id.relation_field

                if line not in lines:
                    lines[line] = [{'record_id': id, 'model': model, relation_field: 'relation_field'}]

                if int(id) != int(lines[line][index]['record_id']):
                    index += 1
                    lines[line].append({'record_id': id, 'model': model, relation_field: 'relation_field'})
                lines[line][index][field] = val

        data = []

        for key, val in lines.items():
            field_id = fields.filtered(lambda f: f.field_id.name == key)
            for item in val:
                data.append(self.reformate_values(item, field_id.table_lines))

        return data

    def get_data(self, dict, fields, model):
        master_data = self.get_master_data(dict, fields, model)
        data = [master_data]
        lines = self.get_lines_data(dict, fields)
        if lines:
            data.extend(lines)
        return data

    def def_get_current_lines(self, fields, record):
        fields = fields.filtered(lambda f: f.field_id.ttype == 'one2many')
        record_ids = []
        for field in fields:
            for record_id in record[field.field_id.name]:
                record_ids.append(record_id)
        return record_ids

    def check_delete_line(self, form_fields, master_record, record_ids):
        current_lines = self.def_get_current_lines(form_fields, master_record)
        for record in current_lines:
            if record not in record_ids:
                try:
                    with request.env.cr.savepoint():
                        record.sudo().unlink()
                except Exception as e:
                    return e
        return False

    def check_permissions(self, portal_view):
        return {
            'read': portal_view.check_portal_access_rights('read'),
            'write': portal_view.check_portal_access_rights('write'),
            'create': portal_view.check_portal_access_rights('create'),
            'delete': portal_view.check_portal_access_rights('delete'),
        }

    @http.route('/portal/<string:model>', type='http', auth="public", website=True, csrf=True)
    def portal_list_view(self, model):
        """
        portal list view
        """
        portal_view = request.env['portal.portal'].sudo().search([('model_name', '=', model)])

        records = []

        if portal_view.check_portal_access_rights('read'):
            records = self.prepare_record_list(model, portal_view)

        values = {
            'view': portal_view,
            'list_fields': portal_view.list_fields.sorted(key='sequence'),
            'records': records,
            'permissions': self.check_permissions(portal_view),
        }

        return request.render("dynamic_portal.portal_list_view", values)

    def get_attachments(self, record_id, model):
        attachments = request.env["ir.attachment"].sudo().search(
            [('res_model', '=', model), ('res_id', '=', record_id.id)])

        return attachments

    @http.route('/portal/<string:model>/<int:recode_id>', type='http', auth="public", website=True, csrf=True)
    def portal_form_view(self, model, recode_id, **kw):
        portal_view = request.env['portal.portal'].sudo().search([('model_name', '=', model)])
        input_type = self.get_input_types(portal_view.form_fields)
        record, record_id = False, False
        disable_edit = 0

        if int(recode_id) > 0:
            disable_edit = request.params.get('edit', 1)
            record_id = request.env[model].sudo().browse(int(recode_id))
            record = self.prepare_record_data(record_id, portal_view.form_fields)

        selection = self.get_selection_data(model, record_id, portal_view.form_fields)

        list_table = self.get_list_table(portal_view.form_fields)

        values = {
            'view': portal_view,
            'form_fields': portal_view.form_fields.sorted(key='sequence'),
            'record': record,
            'record_obj': record_id,
            'input_type': input_type,
            'selection': selection,
            'list_table': list_table,
            'buttons': portal_view.button_ids,
            'disable_edit': True if disable_edit == 1 else False,
            'permissions': self.check_permissions(portal_view),
            'attrs_readonly': portal_view.get_fields_attrs_readonly(record_id),
            'attrs_invisible': portal_view.get_fields_attrs_invisible(record_id),
            'attrs_buttons': portal_view.get_buttons_attrs_invisible(record_id),
            'default_values': portal_view.get_default_values(),
            'attachments': self.get_attachments(record_id, model) if record_id else [],
        }

        return request.render("dynamic_portal.portal_form_view", values)

    def call_buttons_actions(self, action, model, record_id):
        record = request.env[model].sudo().browse(int(record_id))
        page = "/portal/" + model + "/" + record_id

        try:
            with request.env.cr.savepoint():
                getattr(record, action)()
                return werkzeug.utils.redirect(page)
        except Exception as e:
            response = request.render("dynamic_portal.portal_exception_details", {'error_message': [e]})
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    @http.route('/portal/<string:model>/submit', type="http", auth="user", website=True, csrf=True)
    def submit_record(self, model, action, **kw):
        if action != 'submit':
            return self.call_buttons_actions(action, model, kw['record_id'])
        portal_view = request.env['portal.portal'].sudo().search([('model_name', '=', model)])
        data = self.get_data(kw, portal_view.form_fields, model)
        page = "/portal/" + model
        record_ids = []

        for record_data in data:
            rec_model = record_data.get('model')
            record_id = False
            if record_data.get('record_id'):
                record_id = int(record_data.get('record_id'))
            record_data.pop('record_id', None)
            record_data.pop('model', None)
            try:
                with request.env.cr.savepoint():
                    if rec_model != model:
                        relation_field = list(record_data.keys())[
                            list(record_data.values()).index('relation_field')]
                        record_data[relation_field] = master_record.id
                    if record_id and record_id > 0:
                        record = request.env[rec_model].sudo().browse(record_id)
                        record.sudo().update(record_data)
                    else:
                        record = request.env[rec_model].sudo().create(record_data)
                    self.check_computed_fields(record)
                if rec_model == model:
                    master_record = record
                else:
                    record_ids.append(record)
            except Exception as e:
                response = request.render("dynamic_portal.portal_exception_details", {'error_message': [e]})
                response.headers['X-Frame-Options'] = 'DENY'
                return response

        error = self.check_delete_line(portal_view.form_fields, master_record, record_ids)
        if error:
            response = request.render("dynamic_portal.portal_exception_details", {'error_message': [error]})
            response.headers['X-Frame-Options'] = 'DENY'
            return response

        page += "/" + str(master_record.id)
        return werkzeug.utils.redirect(page)

    @http.route('/portal/<string:model>/delete/<int:recode_id>', type="http", auth="user", website=True, csrf=True)
    def delete_record(self, model, recode_id, **kw):
        record = request.env[model].sudo().browse(int(recode_id))
        try:
            with request.env.cr.savepoint():
                record.sudo().unlink()
                return werkzeug.utils.redirect("/portal/" + model)
        except Exception as e:
            response = request.render("dynamic_portal.portal_exception_details", {'error_message': [e]})
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    @http.route('/portal/clear/<string:model>/<int:recode_id>/<string:field>', type="http", auth="user", website=True,
                csrf=True)
    def clear_field(self, model, recode_id, field, **kw):
        record = request.env[model].sudo().browse(int(recode_id))
        try:
            with request.env.cr.savepoint():
                record.sudo().update({field: False})
                page = "/portal/" + model + "/" + str(recode_id)
                # return werkzeug.utils.redirect(page)
        except Exception as e:
            response = request.render("dynamic_portal.portal_exception_details", {'error_message': [e]})
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    @http.route("/my/portal/<string:model>/<int:recode_id>", type="http", auth="user", methods=['GET'])
    def render_portal_view(self, model, recode_id, ):
        record = request.env[model].sudo().browse(int(recode_id))
        if not record.exists():
            return request.not_found()
        return request.render("dynamic_portal.template_sharing_portal", {'recode_id': recode_id, 'model': model})

    @http.route("/my/<string:model>/<int:recode_id>/sharing", type="http", auth="user", methods=['GET'])
    def render_backend_view(self, model, recode_id, ):
        record = request.env[model].sudo().browse(int(recode_id))
        portal_action = request.env['portal.portal'].sudo().search([('model_name', '=', model)])
        return request.render(
            'dynamic_portal.template_sharing_embed',
            {'session_info': self._prepare_project_sharing_session_info(record, portal_action)},
        )

    def _prepare_project_sharing_session_info(self, record, portal_action):
        session_info = request.env['ir.http'].session_info()
        action_name = portal_action.action_id.xml_id
        session_info.update(
            # cache_hashes=cache_hashes,
            action_name=action_name,
            project_id=record.id,
        )
        return session_info
