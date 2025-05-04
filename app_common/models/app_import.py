# -*- coding: utf-8 -*-

import os.path
import json
from os.path import basename, splitext
from odoo import api, fields, models, modules, tools, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)

def app_quick_import(env, content_path, model_name=None, sep=None, context={}):
    if not sep:
        sep = '/'
    dir_split = content_path.split(sep)
    module_name = dir_split[0]
    filename = dir_split[-1]
    md_name, file_extension = splitext(filename)
    if not model_name:
        model_name = md_name
    file_path = modules.get_module_resource(*dir_split)

    if not file_path:
        _logger.error(_('File %s not found' % content_path))
        return False

    content = open(file_path, 'rb').read()
    uid = SUPERUSER_ID
    if model_name == 'mail.channel':
        # todo: 创建mail.channel时，如果用root用户会报错
        uid = 2

    if file_extension.lower() in ['.csv', '.xls', '.xlsx']:
        if file_extension == '.csv':
            file_extension = 'text/csv'
        elif file_extension in ['.xls', '.xlsx']:
            file_extension = 'application/vnd.ms-excel'

        import_wizard = env['base_import.import'].with_context(context)
        import_wizard = import_wizard.create({
            'res_model': model_name,
            'file_name': filename,
            'file_type': file_extension,
            'file': content,
        })

        if file_extension == 'text/csv':
            preview = import_wizard.parse_preview({
                'separator': ',',
                'has_headers': True,
                'quoting': '"',
            })
        elif file_extension == 'application/vnd.ms-excel':
            preview = import_wizard.parse_preview({
                'has_headers': True,
            })
        else:
            preview = False

        if preview:
            import_wizard.execute_import(
                preview["headers"],
                preview["headers"],
                preview["options"]
            )

    elif file_extension.lower() == '.json':
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                if not content.strip():
                    _logger.error(_(f"File {filename} is empty"))
                    return False
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    _logger.error(_(f"Invalid JSON format in file {filename}: {e}"))
                    return False

            if hasattr(env, '_name') and env._name == model_name:
                model = env
            else:
                model = env[model_name]
            if not model._fields:
                _logger.error(_(f"Model {model_name} not found"))
                return False
            if not data:
                _logger.error(_(f"No records found in file {filename}"))
                return False

            import_fields = list(data[0].keys())
            merged_data = []
            for record in data:
                record_data = [record[field] for field in import_fields]
                merged_data.append(record_data)
            import_result = model.load(import_fields, merged_data)
        except FileNotFoundError:
            _logger.error(_(f"File not found: {content_path}"))
        except Exception as e:
            _logger.error(_(f"Unexpected error during import: {e}"))

    else:
        _logger.error(_(f"Unsupported file type: {file_extension}"))
        return False
