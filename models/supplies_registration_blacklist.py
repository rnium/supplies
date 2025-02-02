from odoo import models, fields, api

class BlackList(models.Model):
    _name = 'supplies.registration.blacklist'
    _description = 'Supplies Blacklist'

    email = fields.Char(string='Email', required=True)
    reason = fields.Text(string='Reason', required=True)
    active = fields.Boolean(string='Active', default=True)