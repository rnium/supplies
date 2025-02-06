from odoo import http
from odoo.http import request, route

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
        return request.render(
            'supplies.portal_supplies_rfp_form_view',
            {
                'rfp': rfp,
                'page_title': 'rfp_view'
            }
        )