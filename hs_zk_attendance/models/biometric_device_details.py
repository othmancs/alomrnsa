# -*- coding: utf-8 -*-
import datetime
import logging
from collections import defaultdict

import pytz

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, time

from odoo.tools import attrgetter

_logger = logging.getLogger(__name__)
try:
    from zk import ZK, const
except ImportError:
    _logger.error("Please Install pyzk library.")


class BiometricDeviceDetails(models.Model):
    """Model for configuring and connect the biometric device with odoo"""
    _name = 'biometric.device.details'
    _description = 'Biometric Device Details'

    name = fields.Char(string='Name', required=True, help='Record Name')
    device_ip = fields.Char(string='Device IP', required=True,
                            help='The IP address of the Device')
    port_number = fields.Integer(string='Port Number 1', required=True,
                                 help="The Port Number of the Device")
    port_number2 = fields.Integer(string='Port Number 2', required=True,
                                  help="The Port Number of the Device")
    port_number3 = fields.Integer(string='Port Number 3', required=True,
                                  help="The Port Number of the Device")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda
                                     self: self.env.user.company_id.id,
                                 help='Current Company')
    date_to = fields.Date(string="Date Range", default=fields.Date.today)
    date_from = fields.Date(string="Date from", default=fields.Date.today)

    def device_connect(self, zk):
        """Function for connecting the device with Odoo"""
        try:
            conn = zk.connect()
            return conn
        except Exception:
            return False

    @api.model
    def cron_download_attendance(self):
        """cron_download method: Perform a cron job to download attendance data for all machines.

          This method iterates through all the machines in the 'zk.machine' model and
          triggers the download_attendance method for each machine."""
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        machines = self.env['biometric.device.details'].search([])
        for machine in machines:
            machine.action_download_attendance()

    def action_test_connection(self):
        """Checking the connection status"""
        success_ports = []
        error_ports = []

        if self.port_number:
            zk_1 = ZK(self.device_ip, port=self.port_number, timeout=30,
                      password=False, ommit_ping=False)
            try:
                if zk_1.connect():
                    success_ports.append(self.port_number)
                else:
                    error_ports.append(self.port_number)
            except Exception as e:
                error_ports.append(self.port_number)

        if self.port_number2:
            zk_2 = ZK(self.device_ip, port=self.port_number2, timeout=30,
                      password=False, ommit_ping=False)
            try:
                if zk_2.connect():
                    success_ports.append(self.port_number2)
                else:
                    error_ports.append(self.port_number2)
            except Exception as e:
                error_ports.append(self.port_number2)

        if self.port_number3:
            zk_3 = ZK(self.device_ip, port=self.port_number3, timeout=30,
                      password=False, ommit_ping=False)
            try:
                if zk_3.connect():
                    success_ports.append(self.port_number3)
                else:
                    error_ports.append(self.port_number3)
            except Exception as e:
                error_ports.append(self.port_number3)

        message = ""
        if success_ports:
            message += f'Successfully connected to ports: {success_ports}. '
        if error_ports:
            message += f'Failed to connect to ports: {error_ports}.'

        if success_ports:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': False
                }
            }
        else:
            raise ValidationError(message)

    def action_download_attendance(self):
        """Function to download attendance records from the device"""

        zk_attendance = self.env['zk.machine.attendance']
        hr_attendance = self.env['hr.attendance']
        for info in self:
            machine_ip = info.device_ip
            zk_port_1 = info.port_number
            zk_port_2 = info.port_number2
            zk_port_5 = info.port_number3
            try:
                # Connecting with the device with the ip and port provided
                zk_1 = ZK(machine_ip, port=zk_port_1, timeout=30,
                          password=0,
                          force_udp=False, ommit_ping=False)
                zk_2 = ZK(machine_ip, port=zk_port_2, timeout=30,
                          password=0,
                          force_udp=False, ommit_ping=False)
                zk_3 = ZK(machine_ip, port=zk_port_5, timeout=30,
                          password=0,
                          force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(
                    _("Pyzk module not Found. Please install it"
                      "with 'pip3 install pyzk'."))
            conn_1 = self.device_connect(zk_1)
            conn_2 = self.device_connect(zk_2)
            conn_5 = self.device_connect(zk_3)
            if conn_1 and conn_2 and conn_5:
                conn_1.disable_device()
                conn_2.disable_device()
                conn_5.disable_device()
                attendance_1 = conn_1.get_attendance()
                attendance_2 = conn_2.get_attendance()
                attendance_5 = conn_5.get_attendance()
                if attendance_1 or attendance_2 or attendance_5:
                    attendance_dict = defaultdict(list)
                    for attendance in [attendance_1, attendance_2, attendance_5]:
                        if attendance:
                            for each in attendance:
                                atten_time = each.timestamp
                                local_tz = pytz.timezone(
                                    self.env.user.partner_id.tz or 'GMT')
                                local_dt = local_tz.localize(atten_time, is_dst=None)
                                utc_dt = local_dt.astimezone(pytz.utc)
                                attendance_time = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                                atten_time_datetime = datetime.strptime(attendance_time, "%Y-%m-%d %H:%M:%S")
                                atten_date = atten_time_datetime.date()
                                if info.date_to <= atten_date <= info.date_from:
                                    attendance_dict[each.user_id].append(atten_time_datetime)
                    for user_id, atten_times in attendance_dict.items():
                        dates = {}
                        for atten_time in atten_times:
                            atten_date = atten_time.date()
                            if atten_date not in dates:
                                dates[atten_date] = []
                            dates[atten_date].append(atten_time)

                        for atten_date, times in dates.items():
                            times.sort()
                            if len(times) > 2:
                                times = [times[0], times[-1]]
                                dates[atten_date] = times
                            if len(times) == 1 and atten_date != datetime.now().date():
                                employee = self.env['hr.employee'].search([('device_id_num', '=', user_id)])
                                if employee:
                                    if employee.shift_id:
                                        shift_out = employee.shift_id.shift_out
                                        if shift_out:
                                            shift_out_time = time(int(shift_out-5), int(((shift_out + 5) % 1) * 60))
                                            checkout_datetime = datetime.combine(atten_date, shift_out_time)
                                            times.append(checkout_datetime)
                                            times.sort()
                                            dates[atten_date] = times

                        updated_atten_times = [time for times in dates.values() for time in times]
                        updated_atten_times.sort()
                        attendance_dict[user_id] = updated_atten_times

                        employee = self.env['hr.employee'].search([('device_id_num', '=', user_id)])
                        if len(employee) == 1:
                            for atten_time in updated_atten_times:
                                existing_attendance = zk_attendance.search(
                                    [('device_id_num', '=', user_id), ('check_out','=', False)], limit=1)
                                existing_hr_attendance = hr_attendance.search(
                                    [('employee_id', '=', employee.id),('check_out','=', False)], limit=1)
                                if existing_attendance:
                                    for exist in existing_attendance:
                                        if not exist.check_in == atten_time:
                                            if exist.check_in.date() == atten_time.date():
                                                if exist.check_in > atten_time:
                                                    exist.write({
                                                        'check_in': atten_time,
                                                        'check_out': exist.check_in,
                                                        'o_check': 'o',
                                                    })
                                                else:
                                                    if exist.check_out:
                                                        if not exist.check_out > atten_time:
                                                            exist.write({
                                                                'check_out': atten_time,
                                                                'o_check': 'o',
                                                            })
                                                            if existing_hr_attendance:
                                                                existing_hr_attendance.write({
                                                                    'employee_id': employee.id,
                                                                    'check_out':atten_time
                                                                })
                                                    else:
                                                        exist.write({
                                                            'check_out': atten_time,
                                                            'o_check': 'o',
                                                        })
                                                        if existing_hr_attendance:
                                                            existing_hr_attendance.write({
                                                                'employee_id': employee.id,
                                                                'check_out': atten_time
                                                            })
                                            else:
                                                if not exist.check_in == atten_time:
                                                    check_in_atten = zk_attendance.search([('check_in','=',atten_time), ('device_id_num','=',user_id)])
                                                    check_out_atten = zk_attendance.search([('check_out','=',atten_time), ('device_id_num','=',user_id)])
                                                    if not check_in_atten and not check_out_atten:
                                                        zk_attendance.create({
                                                            'employee_id': employee.id,
                                                            'check_in': atten_time,
                                                            'check_out': False,
                                                            'i_check': 'i',
                                                            'device_id_num': user_id
                                                        })
                                                        hr_attendance.create({
                                                            'employee_id':employee.id,
                                                            'check_in': atten_time
                                                        })
                                else:
                                    check_in_atten = zk_attendance.search(
                                        [('check_in', '=', atten_time), ('device_id_num', '=', user_id)])
                                    check_out_atten = zk_attendance.search(
                                        [('check_out', '=', atten_time), ('device_id_num', '=', user_id)])
                                    if not check_in_atten and not check_out_atten:
                                        zk_attendance.create({
                                            'employee_id': employee.id,
                                            'check_in': atten_time,
                                            'check_out': False,
                                            'device_id_num': user_id,
                                            'i_check': 'i',
                                        })
                                        hr_attendance.create({
                                            'employee_id': employee.id,
                                            'check_in': atten_time
                                        })

                        elif len(employee) > 1:
                            raise ValidationError(
                                "More Than One Employee Is Found With The Same Device Id" + user_id)

                conn_1.disconnect()
                conn_2.disconnect()
                conn_5.disconnect()
                return True
            else:
                raise UserError(_('Unable to connect, please check the parameters and network connections.'))
        else:
            raise UserError(_('Unable to get the attendance log, please'
                              'try again later.'))

    def action_restart_device(self):
        """For restarting the device"""
        try:

            zk_1 = ZK(self.device_ip, port=self.port_number, timeout=30,
                      password=0,
                      force_udp=False, ommit_ping=False)
            zk_2 = ZK(self.device_ip, port=self.port_number2, timeout=30,
                      password=0,
                      force_udp=False, ommit_ping=False)
            zk_5 = ZK(self.device_ip, port=self.port_number3, timeout=30,
                      password=0,
                      force_udp=False, ommit_ping=False)
            self.device_connect(zk_1).restart()
            self.device_connect(zk_2).restart()
            self.device_connect(zk_5).restart()
        except Exception as error:
            raise ValidationError(f'{error}')
