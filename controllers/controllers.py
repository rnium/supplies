# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
from . import utils

class SupplierRegistration(http.Controller):
    @http.route(['/supplies/register'], type='http', auth='public', website=True)
    def show_supplier_registration(self):
        """
        Renders the supplier registration page
        """
        return request.render('bjit_supplies.portal_supplier_registration')

    @http.route(['/supplies/register/send-otp'], type='json', auth='none', methods=['POST'])
    def send_otp(self):
        """
        Sends an OTP to the given mobile number
        """
        email = request.params.get('email')
        is_valid, message = utils.validate_email_address(request, email)
        if not is_valid:
            return utils.format_response('error', message)
        otp_obj = request.env['bjit_supplies.registration.otp'].sudo().create(
            {'email': email}
        )
        try:
            otp_obj.send_otp_email()
        except Exception as e:
            return utils.format_response('error', str(e))
        return utils.format_response('success', 'OTP sent successfully to your email address')
