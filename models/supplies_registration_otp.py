from ..utils.mail_utils import get_smtp_server_email
from odoo import models, fields, api
import random

class RegistrationOTP(models.TransientModel):
    _name = 'supplies.registration.otp'
    _description = 'Supplies Registration OTP'
    _transient_max_hours = 1

    email = fields.Char(string='Email', required=True)
    otp = fields.Char(
        string='OTP', 
        readonly=True,
        default=lambda self: str(random.randint(100000, 999999))              
    )
    is_verified = fields.Boolean(string='Is Verified', default=False)
    company = fields.Many2one('res.company', string='Company', default=lambda self: self._get_company())
    expiry_time = fields.Datetime(
        string='Expiry Time',
        default=lambda self: fields.Datetime.add(fields.Datetime.now(), minutes=5),
        readonly=True
    )

    def _get_company(self):
        company = self.env['res.company'].search([], limit=1)
        return company
    
    def send_otp_email(self):
        email_values = {
            'email_from': get_smtp_server_email(self.env)
        }
        print("company: ", self.company)
        self.env.ref(
            'supplies.email_template_model_bjit_supplies_registration_otp'
        ).send_mail(self.id, force_send=True, email_values=email_values)
        

    def verify_otp(self):
        """
        Verifies the given OTP
        """
        if not self.is_verified and self.expiry_time >= fields.Datetime.now():
            self.write({'is_verified': True})
            return True
        return False
    
    