from odoo import models, fields, api
from zk import ZK, const
import logging

_logger = logging.getLogger(__name__)

class ZKDevice(models.Model):
    _name = 'zk.device'
    _description = 'ZKTeco Device'

    name = fields.Char('Device Name', required=True)
    ip_address = fields.Char('IP Address', required=True)
    port = fields.Integer('Port', default=4370)
    device_type = fields.Selection([('zk', 'ZKTeco')], string='Device Type', default='zk')

    def connect_device(self):
        """Connect to the ZKTeco device and fetch attendance logs."""
        zk = ZK(self.ip_address, port=self.port, timeout=5)

        try:
            conn = zk.connect()
            conn.disable_device()
            _logger.info(f"Connected to device {self.name} at {self.ip_address}")

            # Fetch attendance logs
            attendances = conn.get_attendance()
            for att in attendances:
                employee_id = self._get_employee_from_attendance(att.user_id)
                if employee_id:
                    self.env['hr.attendance'].create({
                        'employee_id': employee_id,
                        'check_in': att.timestamp,
                        # Add additional attendance data if necessary
                    })
                    _logger.info(f"Recorded attendance for employee ID {employee_id} at {att.timestamp}")
                else:
                    _logger.warning(f"Employee not found for user ID {att.user_id}")

        except Exception as e:
            _logger.error(f"Error connecting to device {self.name}: {e}")

        finally:
            if conn:
                conn.enable_device()
                conn.disconnect()
                _logger.info(f"Disconnected from device {self.name}")

    def _get_employee_from_attendance(self, user_id):
        """Map ZKTeco user_id to Odoo employee"""
        employee = self.env['hr.employee'].search([('barcode', '=', str(user_id))], limit=1)
        return employee.id if employee else None
