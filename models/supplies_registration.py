from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ..utils import schemas
from ..utils import supplier_registration_utils as utils
from ..utils.mail_utils import get_smtp_server_email
import random

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
            ('rejected', 'Rejected'),
            ('blacklisted', 'Blacklisted'),
            ('approved', 'Approved'),
            ('finalized', 'Finalized'),
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
    street = fields.Char(string='Address Line 1', required=True)
    street2 = fields.Char(string='Address Line 2')
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
    comments = fields.Text(string='Comments')

    def action_approve(self):
        if self.state == 'submitted':
            return self.write({'state': 'approved'})
        else:
            raise ValidationError('Invalid state change')

    def action_finalize(self):
        if self.state != 'approved':
            raise ValidationError('Invalid state change')
        company_schema = schemas.CompanySchema.model_validate(self)
        bank_schema = schemas.BankSchema.model_validate(self)
        bank_ids_schema = schemas.BankAccountSchema.model_validate(self)
        user_schema = schemas.UserSchema.model_validate(self)
        company_data = company_schema.model_dump()
        bank = utils.get_or_create_bank(self.env, bank_schema.model_dump())
        bank_data = bank_ids_schema.model_dump(bank_id=bank.id)
        child_ids = utils.get_child_contacts(self)
        company_data['bank_ids'] = [(0, 0, bank_data)]
        company_data['child_ids'] = child_ids
        company = self.env['res.partner'].sudo().create(company_data)
        user_data = user_schema.model_dump(
            partner_id=company.id,
            company_id=self.env.company.id,
            groups_id=[(6, 0, self.env.ref('base.group_portal').ids)]
        )
        self.env['res.users'].sudo().create(user_data)
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': self.email,
            'subject': 'Supplier Registration Confirmation',
        }
        contexts = {
            'email': self.email,
            'password': self.email,
        }
        self.env.ref(
            'supplies.email_template_model_supplies_vendor_registration_confirmation'
        ).with_context(**contexts).send_mail(self.id, email_values=email_values)
        return self.write({'state': 'finalized'})

    def action_blacklist(self):
        wizard = self.env['blacklist.wizard'].create({'email': self.email, 'registration_id': self.id})
        return {
            'name': 'Blacklist',
            'type': 'ir.actions.act_window',
            'res_model': 'blacklist.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reject(self):
        wizard = self.env['supplies.reject.application.wizard'].create({'registration_id': self.id})
        return {
            'name': 'Reject Application',
            'type': 'ir.actions.act_window',
            'res_model': 'supplies.reject.application.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def cleanup_registrations(self):
        # delete all registrations that is not in 'submitted' state and it's created more than 30 days ago
        thirty_days_ago = fields.Date.subtract(fields.Date.today(), days=30)
        registrations = self.search([('state', '!=', 'submitted'), ('create_date', '<', thirty_days_ago)])
        registrations.unlink()
