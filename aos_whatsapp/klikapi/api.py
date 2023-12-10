from odoo import _
from odoo.exceptions import Warning, UserError
from odoo.http import request, Response
import json
import requests
import html2text
import datetime

class KlikApi(object):
    def __init__(self, klik_key, klik_secret, **kwargs):
        self.APIUrl = 'https://klikodoo.id/api/wa/'
        self.klik_key = klik_key or ''
        self.klik_secret = klik_secret or ''
    
    def auth(self):
        #if not self.klik_key and not self.klik_secret:
        #    raise UserError(_('Warning! Please add Key and Secret Whatsapp API on General Settings'))
        try:
            requests.get(self.APIUrl+'status/'+self.klik_key+'/'+self.klik_secret, headers={'Content-Type': 'application/json'})
        except (requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
                requests.exceptions.ConnectionError) as err:
            raise Warning(_('Error! Could not connect to Whatsapp account. %s')% (err))
    
    def logout(self):
        url = self.APIUrl + 'logout'
        data = {}
        data['instance'] = self.klik_key
        data['key'] = self.klik_secret
        #get_version = request.env["ir.module.module"].sudo().search([('name','=','base')], limit=1)
        #data['get_version'] = get_version and get_version.latest_version
        data_s = {
            'params' : data
        }
        req = requests.post(url, json=data_s, headers={'Content-Type': 'application/json'})
        res = json.loads(req.text)
        return res['result']
    
    
    def get_count(self):
        data = {}
        url = self.APIUrl + 'count/' + self.klik_key +'/' + self.klik_secret
        data_req = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = json.loads(data_req.text)
        #print ('===res===',res)
        return res.get('result') and res['result'] or {}
    
    def get_limit(self):
        data = {}
        url = self.APIUrl + 'limit/' + self.klik_key +'/' + self.klik_secret
        data_req = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = json.loads(data_req.text)
        #print ('===res===',res)
        return res.get('result') and res['result'] or {}
    
    def get_number(self):
        data= {}
        url = self.APIUrl + 'check/' + self.klik_key +'/' + self.klik_secret
        data_req = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = json.loads(data_req.text)
        print ('===get_number===',res)
        return res.get('result') and res['result'] or {}
    
    def get_request(self, method, data):
        url = self.APIUrl + 'get/' + self.klik_key +'/' + self.klik_secret + '/' + method
        print ('--get_request--',url)
        data_req = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = json.loads(data_req.text)
        return res.get('result') and res['result'] or {}
    
    def post_request(self, method, data):
        url = self.APIUrl + 'post/'
        data= json.loads(data)
        data['instance'] = self.klik_key
        data['key'] = self.klik_secret
        data['method'] = method
        #get_version = request.env["ir.module.module"].sudo().search([('name','=','base')], limit=1)
        #data['get_version'] = get_version and get_version.latest_version
        data_s = {
            'params' : data
        }
        response = requests.post(url, json=data_s, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            message1 = json.loads(response.text)
            print ('===message1=',message1)
            message = message1.get('result').get('message')
            chatID = message.get('id') and message.get('id').split('_')[1]
            return {'chatID': chatID, 'message': message}
        else:
            return {'message': {'sent': False, 'message': 'Error'}}
    
    
    def get_phone(self, method, phone):
        data = {}
        url = self.APIUrl + 'phone/' + self.klik_key + '/'+self.klik_secret +'/'+ method + '/' + phone
        data = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = json.loads(data.text)
        return res.get('result') and res['result'] or {}