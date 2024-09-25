from odoo import models, fields, api


class ZKDevice(models.Model):
    _name = 'zk.device'
    _description = 'ZKTeco Device'

    name = fields.Char('Device Name', required=True)
    ip_address = fields.Char('IP Address', required=True)
    port = fields.Integer('Port', default=4370)
    device_type = fields.Selection([('zk', 'ZKTeco')], string='Device Type', default='zk')

    def connect_device(self):
        """Connect to the ZKTeco device and fetch attendance logs."""
        from zk import ZK, const

        zk = ZK(self.ip_address, port=self.port, timeout=5)
        conn = zk.connect()
        conn.disable_device()

        # Fetch attendance logs
        attendances = conn.get_attendance()
        for att in attendances:
            self.env['hr.attendance'].create({
                'employee_id': self._get_employee_from_attendance(att.user_id),
                'check_in': att.timestamp,
                # Add additional attendance data if necessary
            })

        conn.enable_device()
        conn.disconnect()

    def _get_employee_from_attendance(self, user_id):
        """Map ZKTeco user_id to Odoo employee"""
        employee = self.env['hr.employee'].search([('barcode', '=', str(user_id))], limit=1)
        return employee.id if employee else None
