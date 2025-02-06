from odoo import http
from odoo.http import request, route
from ..utils import schemas
from pydantic import ValidationError

class SuppliesPortal(http.Controller):
    @http.route('/my/supplies', auth='user', website=True)
    def supplies_portal(self, **kw):
        rfps = request.env['supplies.rfp'].search([('state', '=', 'approved')])
        return request.render(
            'supplies.portal_supplies_rfp_tree_view',
            {
                'rfps': rfps,
                'page_title': 'rfp_list'
            }
        )

    @http.route('/my/supplies/<string:rfp_number>', auth='user', website=True)
    def supplies_portal_rfp(self, rfp_number, **kw):
        rfp = request.env['supplies.rfp'].search([('rfp_number', '=', rfp_number)])
        success_list = []
        error_list = []

        if request.httprequest.method == 'POST':
            try:
                rfq_schema = schemas.PurchaseOrderSchema(
                    **dict(
                        request.httprequest.form.items(),
                        rfp_id=rfp.id,
                        partner_id=request.env.user.partner_id.id,
                    )
                )
            except ValidationError as e:
                errors = e.errors()
                for error in errors:
                    error_list.append(error['msg'])
            else:
                rfq = request.env['purchase.order'].create(rfq_schema.get_new_purchase_order_data())
                success_list.append('RFQ submitted successfully.')
        return request.render(
            'supplies.portal_supplies_rfp_form_view',
            {
                'rfp': rfp,
                'page_title': 'rfp_view',
                'success_list': success_list,
                'error_list': error_list
            }
        )