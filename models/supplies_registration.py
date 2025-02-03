from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SuppliesRegistrationContact(models.Model):
    _name = 'supplies.contact'
    _description = 'Supplies Registration Contact'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Char(string='Address')


class SuppliesRegistration(models.Model):
    _name = 'supplies.registration'
    _description = 'Supplies Registration'

    state = fields.Selection(
        [
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('finalized', 'Finalized'),
            ('rejected', 'Rejected'),
            ('blacklisted', 'Blacklisted'),
        ],
        default='submitted',
        string='Application State',
    )
    # company info fields
    name = fields.Char(string='Company Name', required=True)
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
    primary_contact_id = fields.Many2one('supplies.contact', string='Primary Contact', required=True)
    finance_contact_id = fields.Many2one('supplies.contact', string='Finance Contact', required=True)
    authorized_contact_id = fields.Many2one('supplies.contact', string='Authorized Contact', required=True)
    expiry_date = fields.Date(string='Expiry Date')
    # Bank info fields
    bank_name = fields.Char(string='Bank Name', required=True)
    swift_code = fields.Char(string='Bank SWIFT Code') # custom field
    iban = fields.Char(string='IBAN') # custom field
    branch_address = fields.Char(string='Branch Address', required=True) # custom field
    acc_holder_name = fields.Char(string='Account Name')
    acc_number = fields.Char(string='Account Number', required=True)
    # Certification fields (all are custom fields)
    certification_name = fields.Char(string='Certification')
    certificate_number = fields.Char(string='Certificate Number')
    certifying_body = fields.Char(string='Certifying Body')
    certification_award_date = fields.Date(string='Certification Award Date')
    certification_expiry_date = fields.Date(string='Certification Expiry Date')
    # Client References
    client_ref_ids = fields.Many2many('supplies.contact', string='Client References')
    # Document fields (all are custom fields)
    trade_license_doc = fields.Binary(string='Trade License / Business Registration')
    certificate_of_incorporation_doc = fields.Binary(string='Certificate of Incorporation')
    certificate_of_good_standing_doc = fields.Binary(string='Certificate of Good Standing')
    establishment_card_doc = fields.Binary(string='Establishment Card')
    vat_tax_certificate_doc = fields.Binary(string='VAT / Tax Certificate')
    memorandum_of_association_doc = fields.Binary(string='Memorandum of Association')
    identification_of_authorised_person_doc = fields.Binary(string='Identification of Authorised Person')
    bank_letter_doc = fields.Binary(string='Bank Letter indicating Bank Account Information')
    past_2_years_financial_statement_doc = fields.Binary(string='Past 2 Years of Financial Statement')
    other_certification_doc = fields.Binary(string='Other Certification / Accreditation')

    def action_approve(self):
        if self.state == 'draft':
            return self.write({'state': 'approved'})
        else:
            raise ValidationError('Invalid state change')

    def action_finalize(self):
        if self.state == 'approved':
            return self.write({'state': 'finalized'})
        else:
            raise ValidationError('Invalid state change')
