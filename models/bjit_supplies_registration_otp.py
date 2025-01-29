from odoo import models, fields, api
import random

class RegistrationOTP(models.Model):
    _name = 'bjit_supplies.registration.otp'
    _description = 'BJIT Supplies Registration OTP'

    email = fields.Char(string='Email', required=True)
    otp = fields.Char(
        string='OTP', 
        readonly=True,
        default=lambda self: str(random.randint(100000, 999999))              
    )
    is_verified = fields.Boolean(string='Is Verified', default=False)
    expiry_time = fields.Datetime(
        string='Expiry Time',
        default=lambda self: fields.Datetime.add(fields.Datetime.now(), minutes=5),
        readonly=True
    )
    
    def send_otp_email(self):
        self.env.ref(
            'bjit_supplies.email_template_model_bjit_supplies_registration_otp'
        ).send_mail(self.id, force_send=True)
        

    def verify_otp(self, otp):
        """
        Verifies the given OTP
        """
        pass
    
    