# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
from . import utils

class SupplierRegistration(http.Controller):
    @http.route(['/supplier-registration'], type='http', auth='public', website=True)
    def show_supplier_registration(self):
        """
        Renders the supplier registration page
        """
        return request.render('supplier_management.portal_supplier_registration')

    @http.route(['/supplier-registration/send-otp'], type='json', auth='none', methods=['POST'])
    def send_otp(self):
        """
        Sends an OTP to the given mobile number
        """
        otp = utils.generate_otp()
        print(f"Generated OTP: {otp}")
        return utils.format_response('success', 'OTP sent successfully')
