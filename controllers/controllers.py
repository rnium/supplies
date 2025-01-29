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
        otp = utils.generate_otp()
        print(f"Generated OTP: {otp}")
        return utils.format_response('success', 'OTP sent successfully to your email address')
