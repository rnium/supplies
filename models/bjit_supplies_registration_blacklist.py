from odoo import models, fields, api

class BlackList(models.Model):
    _name = 'bjit_supplies.registration.blacklist'
    _description = 'BJIT Supplies Blacklist'

    email = fields.Char(string='Email', required=True)
    reason = fields.Text(string='Reason', required=True)
    active = fields.Boolean(string='Active', default=True)