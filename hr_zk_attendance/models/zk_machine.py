# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
import sys
import datetime
import logging
import binascii
from operator import itemgetter
from itertools import groupby
import datetime as dt

from . import zklib
from .zkconst import *
from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
try:
    from zk import ZK, const
except ImportError:
    _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')


class ZkMachine(models.Model):
    _name = 'zk.machine'
    
    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)


    def _group_attendance(self, attendance):
        date = datetime(2023, 6, 1, 0, 0, 0)
        g_list = []
        js_list = []
        # att_list = [(att.user_id, att.timestamp.date(), att.timestamp.time()) for att in attendance if att.timestamp >= date]
        att_list = [(att.user_id, att.timestamp.date(), att.timestamp.time()) for att in attendance]
        att_list.sort(key=itemgetter(0))
        att_group = groupby(att_list, itemgetter(0))
        for k, g in att_group:
            g_list.append(list(g))
        if g_list:
            for j in g_list:
                j.sort(key=itemgetter(1))
                js_group = groupby(j, itemgetter(1))
                for k, g in js_group:
                    js_list.append(list(g))
        return js_list

    def device_connect(self, zk):
        try:
            print("DDDDDDDD",type(zk))
            conn = zk.connect()
            return conn
        except:
            return False
    
    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                timeout = 30
                try:
                    zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                except NameError:
                    raise UserError(_("Please install it with 'pip3 install pyzk'."))
                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # conn.clear_attendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                        conn.disconnect()
                        raise UserError(_('Attendance Records Deleted.'))
                    else:
                        raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
                else:
                    raise UserError(
                        _('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
            except:
                raise ValidationError(
                    'Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty.')

    def getSizeUser(self, zk):
        """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent"""
        command = unpack('HHHH', zk.data_recv[:8])[0]
        if command == CMD_PREPARE_DATA:
            size = unpack('I', zk.data_recv[8:12])[0]
            print("size", size)
            return size
        else:
            return False

    def zkgetuser(self, zk):
        """Start a connection with the time clock"""
        try:
            users = zk.get_users()
            print(users)
            return users
        except:
            return False

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines :
            machine.download_attendance()
        
    def download_attendance(self):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance']
        date = datetime(2023, 6, 1, 0, 0, 0)
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = 15
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                print("00000000000000000000", zk)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
            conn = self.device_connect(zk)
            print("111111111111111",conn)
            if conn:
                # conn.disable_device() #Device Cannot be used during this time.
                try:
                    user = conn.get_users()
                except:
                    user = False
                try:
                    attendance = conn.get_attendance()
                except:
                    attendance = False
                if attendance:
                    for each in attendance:
                        print("@@@@@@@@@@@@@@@@@@@@@@", each)
                        # if each.timestamp >= date:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time)
                        # if user:
                        #     for uid in user:
                        #         if uid.user_id == each.user_id:
                        get_user_id = self.env['hr.employee'].search([('device_id', '=', each.user_id)])
                        if get_user_id:
                            duplicate_atten_ids = zk_attendance.search(
                                [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
                            if duplicate_atten_ids:
                                continue
                            else:
                                zk_attendance.create({'employee_id': get_user_id.id,
                                                      'device_id': each.user_id,
                                                      'attendance_type': str(each.status),
                                                      'punch_type': str(each.punch),
                                                      'punching_time': atten_time,
                                                      'address_id': info.address_id.id})
                        # else:
                        #     print('ddfcd', str(each.status))
                        #     employee = self.env['hr.employee'].create(
                        #         {'device_id': each.user_id, 'name': uid.name})
                        #     zk_attendance.create({'employee_id': employee.id,
                        #                           'device_id': each.user_id,
                        #                           'attendance_type': str(each.status),
                        #                           'punch_type': str(each.punch),
                        #                           'punching_time': atten_time,
                        #                           'address_id': info.address_id.id})


                    # zk.enableDevice()
                    att_list = self._group_attendance(attendance)
                    for att in att_list:
                        if len(att) == 1:
                            device_emp_id = att[0][0]
                            min_ts = datetime.combine(att[0][1], att[0][2])
                            # min time zone start
                            min_ts = datetime.strptime(min_ts.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                            local_dt = local_tz.localize(min_ts, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                            min_ts = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                            user_id = self.env['hr.employee'].search([('device_id', '=', device_emp_id)])
                            if user_id:
                                duplicate_atten_ids = att_obj.search([('employee_id', '=', user_id.id), ('check_in', '=', min_ts)])
                                if duplicate_atten_ids:
                                    continue
                                else:
                                    att_obj.create({'employee_id': user_id.id, 'check_in': min_ts, 'first_half_status': 'present'})
                        else:
                            device_emp_id = att[0][0]
                            user_id = self.env['hr.employee'].search(
                                [('device_id', '=', device_emp_id)])
                            min_att = min(att, key=itemgetter(2))
                            max_att = max(att, key=itemgetter(2))
                            min_ts = datetime.combine(min_att[1], min_att[2])
                            max_ts = datetime.combine(max_att[1], max_att[2])
                            # min time zone start
                            min_ts = datetime.strptime(min_ts.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                            local_dt = local_tz.localize(min_ts, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                            min_ts = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                            # min time zone end

                            # max time zone start
                            max_ts = datetime.strptime(max_ts.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                            local_dt = local_tz.localize(max_ts, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                            max_ts = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                            # max time zone end
                            if user_id:
                                duplicate_atten_ids = att_obj.search([('employee_id', '=', user_id.id), ('check_in', '=', min_ts)])
                                write_atten_ids = att_obj.search([('employee_id', '=', user_id.id), ('check_in', '=', min_ts), ('check_out', '=', False)])
                                if write_atten_ids:
                                    write_atten_ids.write({'check_out': max_ts, 'second_half_status': 'present'})
                                if duplicate_atten_ids:
                                    continue
                                else:
                                    att_obj.create({'employee_id': user_id.id, 'check_in': min_ts,
                                                    'first_half_status': 'present', 'check_out': max_ts, 'second_half_status': 'present'})

                    conn.disconnect
                    return True
                else:
                    raise UserError(_('Unable to get the attendance log, please try again later.'))

            else:
                raise UserError(_('Unable to connect, please check the parameters and network connections.'))


