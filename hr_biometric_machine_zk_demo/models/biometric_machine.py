# -*- coding: utf-8 -*-

from odoo import models,fields,api,exceptions,SUPERUSER_ID,_
from odoo.exceptions import UserError

from datetime import datetime , timedelta
import pytz
import time

from . import const
from .base import ZK

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


class zkMachine(models.Model):
    _name= 'zk.machine.demo.udp'
    
    name =  fields.Char("Machine IP")
    port =  fields.Integer("Port Number")
    
    def try_connection(self):
        for r in self:
            machine_ip = r.name
            port = r.port
            zk = ZK(machine_ip, port=port, timeout=10, password=0, force_udp=False, ommit_ping=False)
            conn = ''
            try:
                conn = zk.connect()
                users = conn.get_users()
            except Exception as e:
                raise UserError('The connection has not been achieved')
            finally:
                if conn:
                    conn.disconnect()
                    raise UserError(_('successful connection:  "%s".') %
                            (users))
                    
                    
