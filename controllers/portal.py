from odoo import http
from odoo.http import request, route
from ..utils import schemas
from ..utils import mail_utils
from pydantic import ValidationError

class SuppliesPortal(http.Controller):
    @http.route('/my/supplies', auth='user', website=True)
    def supplies_portal(self, **kw):
        rfps = request.env['supplies.rfp'].sudo().search([('state', '=', 'approved')])
        return request.render(
            'supplies.portal_supplies_rfp_tree_view',
            {
                'rfps': rfps,
                'page_name': 'rfp_list'
            }
        )

    @http.route('/my/supplies/<string:rfp_number>', auth='user', website=True)
    def supplies_portal_rfp(self, rfp_number, **kw):
        rfp = request.env['supplies.rfp'].sudo().search(
            [
                ('rfp_number', '=', rfp_number),
                ('state', '=', 'approved')
            ]
        )
        success_list = []
        error_list = []

        if request.httprequest.method == 'POST':
            try:
                rfq_schema = schemas.PurchaseOrderSchema(
                    **dict(
                        request.httprequest.form.items(),
                        rfp_id=rfp.id,
                        partner_id=request.env.user.partner_id.id,
                        user_id=rfp.write_uid.id
                    )
                )
            except ValidationError as e:
                errors = e.errors()
                for error in errors:
                    error_list.append(error['msg'])
            else:
                data = rfq_schema.model_dump(exclude_none=True)
                order_line = data.pop('order_line')
                rfq = request.env['purchase.order'].sudo().create(data)
                for line in order_line:
                    line['order_id'] = rfq.id
                    request.env['purchase.order.line'].sudo().create(line)
                success_list.append('RFQ submitted successfully.')
                # send email to reviewer
                template = request.env.ref('supplies.email_template_model_purchase_order_rfq_submission').sudo()
                email_values = {
                    'email_from': mail_utils.get_smtp_server_email(request.env),
                    'email_to': rfp.create_uid.login,
                    'subject': f'New RFQ Submission for {rfp.rfp_number}',
                }
                contexts = {'rfp_number': rfp.rfp_number, 'company_name': rfq.company_id.name}
                template.with_context(**contexts).send_mail(rfq.id, email_values=email_values)

        return request.render(
            'supplies.portal_supplies_rfp_form_view',
            {
                'rfp': rfp,
                'page_name': 'rfp_view',
                'success_list': success_list,
                'error_list': error_list
            }
        )

    @http.route('/my/supplies/rfq', auth='user', website=True)
    def supplies_portal_rfq(self, **kw):
        rfqs = request.env['purchase.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        return request.render(
            'supplies.portal_supplies_rfq_tree_view',
            {
                'rfqs': rfqs,
                'page_name': 'rfq_list'
            }
        )

    @http.route('/my/supplies/rfq/<string:rfq_ref>', auth='user', website=True)
    def supplies_portal_rfq_view(self, rfq_ref, **kw):
        rfq = request.env['purchase.order'].sudo().search(
            [
                ('name', '=', rfq_ref),
                ('partner_id', '=', request.env.user.partner_id.id)
            ]
        )
        return request.render(
            'supplies.portal_supplies_rfq_form_view',
            {
                'rfq': rfq,
                'page_name': 'rfq_detail'
            }
        )