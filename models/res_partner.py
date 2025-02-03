from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
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
    trade_license_doc = fields.Binary(string='Trade License Document')
    trade_license_number = fields.Char(string='Trade License Number')
    tax_identification_number = fields.Char(string='Tax Identification Number')
    commencement_date = fields.Date(string='Commencement Date')
    expiry_date = fields.Date(string='Expiry Date')
    client_ref_ids = fields.Many2many('res.partner', string='Client References')
    certificate_of_incorporation_doc = fields.Binary(string='Certificate of Incorporation Document')
    certificate_of_good_standing_doc = fields.Binary(string='Certificate of Good Standing Document')
    establishment_card_doc = fields.Binary(string='Establishment Card Document')
    vat_tax_certificate_doc = fields.Binary(string='VAT Tax Certificate Document')
    memorandum_of_association_doc = fields.Binary(string='Memorandum of Association Document')
    identification_of_authorised_person_doc = fields.Binary(string='Identification of Authorized Person Document')
    bank_letter_doc = fields.Binary(string='Bank Letter Document')
    past_2_years_financial_statement_doc = fields.Binary(string='Past 2 Years Financial Statement Document')
    other_certification_doc = fields.Binary(string='Other Certification Document')