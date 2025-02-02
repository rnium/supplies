# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
from ..utils import controller_utils as utils
from ..utils import schemas
from pydantic import ValidationError
from odoo import fields
import json


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
        print("OTP: ", otp_obj.otp)
        # try:
        #     otp_obj.send_otp_email()
        # except Exception as e:
        #     return utils.format_response('error', str(e))
        return utils.format_response('success', 'OTP sent successfully to your email address')

    @http.route(['/supplies/register/verify-otp'], type='json', auth='none', methods=['POST'])
    def verify_otp(self):
        """
        Verifies the OTP
        """
        email = request.params.get('email')
        otp = request.params.get('otp')
        otp_obj = request.env['bjit_supplies.registration.otp'].sudo().search(
            [('email', '=', email), ('otp', '=', otp), ('expiry_time', '>=', fields.Datetime.now())]
        )
        if not otp_obj or not otp_obj.verify_otp():
            return utils.format_response('error', 'Invalid OTP')
        return utils.format_response('success', 'OTP verified successfully')

    @http.route(['/supplies/register/submit'], type='http', auth='public', methods=['POST'])
    def submit_registration(self, **post):
        """
        Handles the submission of the supplier registration form
        """
        form_data = request.httprequest.form
        files = request.httprequest.files
        
        print("Form Data: ", form_data)
        print("Files: ", files)
        print("Post Data: ", post)
        data = json.dumps(utils.format_response('success', 'Registration submitted successfully'))
        try:
            reg_data_schema = schemas.SupplierRegistrationSchema(**form_data, **files)
        except ValidationError as e:
            data = json.dumps(
                utils.format_response(
                    'error',
                    'Data validation failed',
                    e.errors(include_input=False, include_context=False, include_url=False)
                )
            )
        return request.make_response(data, headers={'Content-Type': 'application/json'})