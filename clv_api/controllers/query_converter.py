from dateutil.parser import parser


class QueryConverter:
    """
    Used to convert InventoryAPI query structure object to odoo's domain query list
    """

    # all integer-mapped types of filter
    _plain_int_types = {
        'Char' : True,
        'SByte' : True,
        'Byte': True,
        'Int16': True,
        'UInt16': True,
        'Int32': True,
        'UInt32': True,
        'Int64': True,
        'UInt64': True,
    }

    # maps api operation name to odoo domain operation
    _odoo_operations_map = {
        'Equal': '=',
        'NotEqual': '!=',
        'Less': '<',
        'Greater': '>',
        'LessOrEqual': '<=',
        'GreaterOrEqual': '>=',
        'Contains': 'ilike',
        'StartsWith': 'ilike', # simplification StartsWith works like contains for now
        'Or': '|',
        'And': '&',
        'Not': '!'
    }

    def convert_api_where_expression_to_domain_filter(self, where_root, field_name_map):
        """
        Converts filter where expression do domain list query in ODOO
        @param where_root: the root of the where expression
        @param field_name_map: filed map
        @return:
        """
        return self._convert_node(where_root, field_name_map)

    def _convert_node(self, where_root, api_to_odoo_field_map):
        if not where_root:
            return []
        node_type = where_root.get('nodeType')
        value = where_root.get('value')
        operands = where_root.get('operands')

        if node_type == 'Field':
            field_info = api_to_odoo_field_map.get(value.get('value').lower())
            if not field_info:
                raise RuntimeError('Unknown field name for the query: ' + str(value.get('value')))
            return [field_info.odoo_name]
        if node_type == 'Value':
            return [self._convert_plain_value(value.get('value'), value.get('valueType'))]

        result = []
        if node_type == 'Not':
            arg = self._convert_node(operands[0], api_to_odoo_field_map)
            result.append('!')
            result.extend(arg)
        elif node_type == 'Or' or node_type == 'And':
            arg1 = self._convert_node(operands[0], api_to_odoo_field_map)
            arg2 = self._convert_node(operands[1], api_to_odoo_field_map)
            result.append(self._odoo_operations_map[node_type])
            result.extend(arg1)
            result.extend(arg2)
        else:
            mapped_operation = self._odoo_operations_map.get(node_type)
            if not mapped_operation:
                raise RuntimeError('Unknown where expression node type ' + str(node_type))
            arg1 = self._convert_node(operands[0], api_to_odoo_field_map)
            arg2 = self._convert_node(operands[1], api_to_odoo_field_map)
            if len(arg1) != 1 or len(arg2) != 1:
                raise RuntimeError('Invalid operands of binary operation in query filter')
            if operands[0].get('nodeType') == 'Field' and operands[1].get('nodeType') == 'Value':
                field_name = operands[0].get('value').get('value')
                field_info = api_to_odoo_field_map.get(field_name.lower())
                if not field_info:
                    raise RuntimeError('Unknown field name for the query: ' + str(field_name))
                if field_info.odoo_type:
                    arg2[0] = field_info.odoo_type(arg2[0])

            result = [(arg1[0], mapped_operation, arg2[0])]
        return result

    def _convert_plain_value(self, plain_value, plain_type):
        if plain_type == 'String':
            return str(plain_value)
        if plain_type == 'DateTime':
            #  the date-time notation as defined by RFC 3339, section 5.6, for example, 2017-07-21T17:32:28Z
            return parser.parse(plain_value)
        if plain_type in self._plain_int_types:
            return int(plain_value)
        if plain_type == 'Boolean':
            return bool(plain_value)
        if plain_type == 'Single' or plain_type == 'Double' or 'Decimal':
            return float(plain_value)
        raise RuntimeError('Unknown plain value type in query')