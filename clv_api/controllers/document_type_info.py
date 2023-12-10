from enum import Enum


class BusinessLocationType(Enum):
    """
    Logical location type
    """
    SRC = 1  # SOURCE LOCATION
    DEST = 2  # DESTINATION LOCATION


class DocumentTypeInfo:
    """
    Information about document type
    """

    def __init__(self, odoo_sequence_code: str,
                 clv_api_name: str,
                 main_location_type: BusinessLocationType,
                 can_ignore_scan_locations: bool,
                 generate_fake_serial_if_empty: bool,
                 actual_lines_ignores_zero_qty_done: bool,
                 can_overwrite_fake_serial_numbers: bool):
        self.odoo_sequence_code = odoo_sequence_code
        self.clv_api_name = clv_api_name
        self.main_location_type = main_location_type
        self.can_ignore_scan_locations = can_ignore_scan_locations
        self.generate_fake_serial_if_empty = generate_fake_serial_if_empty
        self.actual_lines_ignores_zero_qty_done = actual_lines_ignores_zero_qty_done
        self.can_overwrite_fake_serial_numbers = can_overwrite_fake_serial_numbers
