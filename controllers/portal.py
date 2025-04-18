from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http
from odoo import _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from odoo.http import request, route
from ..utils import schemas
from ..utils import mail_utils
from pydantic import ValidationError

class SuppliesPortal(CustomerPortal):
    @http.route(['/my/supplies', '/my/supplies/page/<int:page>'], auth='user', website=True)
    def supplies_portal(self, page=1, sortby=None, search=None, search_in=None, groupby=None, **kw):
        limit = 5
        searchbar_sortings = {
            'date': {'label': 'Newest', 'order': 'date_approve desc'},
            'name': {'label': 'Name', 'order': 'rfp_number'},
        }
        groupby_list = {
            'required_date': {'input': 'required_date', 'label': _('Required Date')},
            'state': {'input': 'state', 'label': _('Status')},
        }
        search_in = search_in or 'name'
        order = searchbar_sortings[sortby]['order'] if sortby else 'date_approve desc'
        groupby = groupby or 'state'
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('Name'), 'input': 'rfp_number', 'domain': [('rfp_number', 'ilike', search)]},
        }
        sortby = sortby or 'date'
        search_domain = [('state', '=', 'approved')]
        search_domain += search_list[search_in]['domain']
        rfp_count = request.env['supplies.rfp'].sudo().search_count(search_domain)
        pager = portal_pager(
            url="/my/supplies",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby},
            total=rfp_count,
            page=page,
            step=limit
        )
        rfps = request.env['supplies.rfp'].sudo().search(search_domain, order=order, limit=limit, offset=pager['offset'])
        group_by_rfp = groupby_list.get(groupby, {})
        if groupby_list[groupby]['input']:
            rfp_group_list =  [{group_by_rfp['input']: i, 'rfps': list(j)} for i, j in groupbyelem(rfps, itemgetter(group_by_rfp['input']))]
        else:
            rfp_group_list = [{'rfps': rfps}]

        return request.render(
            'supplies.portal_supplies_rfp_tree_view',
            {
                'rfps': rfps,
                'page_name': 'rfp_list',
                'pager': pager,
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': search_list,
                'sortby': sortby,
                'search_in': search_in,
                'search': search,
                'groupby': groupby,
                'searchbar_groupby': groupby_list,
                'default_url': '/my/supplies',
                'group_rfps': rfp_group_list
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
        all_rfps = request.env['supplies.rfp'].sudo().search(
            [
                ('state', '=', 'approved')
            ]
        )
        rfp_index = all_rfps.ids.index(rfp.id)
        prev_record = all_rfps[rfp_index - 1].rfp_number if rfp_index > 0 else False
        next_record = all_rfps[rfp_index + 1].rfp_number if rfp_index < len(all_rfps) - 1 else False
        success_list = []
        error_list = []
        page_contexts = {}

        if request.httprequest.method == 'POST':
            try:
                partner_id = request.env.user.partner_id
                if partner_id.supplier_rank < 1:
                    raise AttributeError('You are not a supplier.')
                rfq_schema = schemas.PurchaseOrderSchema(
                    **dict(
                        request.httprequest.form.items(),
                        rfp_id=rfp.id,
                        partner_id=partner_id.id,
                        user_id=rfp.review_by.id
                    )
                )
            except ValidationError as e:
                errors = e.errors()
                for error in errors:
                    error_list.append(error['msg'])
            except AttributeError as e:
                error_list.append(str(e))
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
                page_contexts['submitted_rfq'] = rfq

        return request.render(
            'supplies.portal_supplies_rfp_form_view',
            {
                'rfp': rfp,
                'page_name': 'rfp_view',
                'success_list': success_list,
                'error_list': error_list,
                'prev_record': "/my/supplies/" + prev_record if prev_record else False,
                'next_record': "/my/supplies/" + next_record if next_record else False,
                **page_contexts
            }
        )

    @http.route(['/my/supplies/rfq', '/my/supplies/rfq/page/<int:page>'], auth='user', website=True)
    def supplies_portal_rfq(self, page=1, sortby=None, search=None, search_in=None, groupby=None, **kw):
        limit = 5
        searchbar_sortings = {
            'date': {'label': 'Newest', 'order': 'create_date desc'},
            'name': {'label': 'Name', 'order': 'name'},
            'state': {'label': 'Status', 'order': 'state desc'},
        }
        search_in = search_in or 'name'
        order = searchbar_sortings[sortby]['order'] if sortby else 'create_date desc'
        groupby = groupby or 'state'
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]},
        }
        sortby = sortby or 'date'
        search_domain = [('partner_id', '=', request.env.user.partner_id.id)]
        search_domain += search_list[search_in]['domain']
        rfq_count = request.env['purchase.order'].sudo().search_count(search_domain)
        pager = portal_pager(
            url="/my/supplies/rfq",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby},
            total=rfq_count,
            page=page,
            step=limit
        )
        rfqs = request.env['purchase.order'].sudo().search(search_domain, order=order, limit=limit, offset=pager['offset'])

        return request.render(
            'supplies.portal_supplies_rfq_tree_view',
            {
                'rfqs': rfqs,
                'page_name': 'rfq_list',
                'pager': pager,
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': search_list,
                'sortby': sortby,
                'search_in': search_in,
                'search': search,
                'default_url': '/my/supplies/rfq',
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