from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BJITSuppliesRegistrationContact(models.Model):
    _name = 'bjit_supplies.registration.contact'
    _description = 'BJIT Supplies Registration Contact'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    address = fields.Char(string='Address')


class BJITSuppliesRegistration(models.Model):
    _name = 'bjit_supplies.registration'
    _description = 'BJIT Supplies Registration'

    company_name = fields.Char(string='Company Name', required=True)
    company_category_type = fields.Selection(
        [
            ('LLC', 'LLC'),
            ('PLC', 'PLC'),
            ('Limited', 'Limited'),
            ('Partnership', 'Partnership'),
            ('Sole Proprietorship', 'Sole Proprietorship'),
            ('Others', 'Others'),
        ]
    )
    image_1920 = fields.Binary(string='Logo')
    email = fields.Char(string='Email', required=True)
    address_line_1 = fields.Char(string='Address Line 1', required=True)
    address_line_2 = fields.Char(string='Address Line 2')
    trade_license_number = fields.Char(string='Trade License Number')
    tax_identification_number = fields.Char(string='Tax Identification Number')
    commencement_date = fields.Date(string='Commencement Date')
    primary_contact_id = fields.Many2one('bjit_supplies.registration.contact', string='Primary Contact', required=True)
    finance_contact_id = fields.Many2one('bjit_supplies.registration.contact', string='Finance Contact', required=True)
    authorized_contact_id = fields.Many2one('bjit_supplies.registration.contact', string='Authorized Contact', required=True)
    expiry_date = fields.Date(string='Expiry Date')

