from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.rfp_utils import rfp_state_flow
from ..utils.mail_utils import get_smtp_server_email, get_approver_emails, get_supplier_emails


class SuppliesRfp(models.Model):
    _name = 'supplies.rfp'
    _inherit = ['mail.thread']
    _description = 'Request for Purchase'
    _rec_name = 'rfp_number'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    rfp_number = fields.Char(string='RFP Number', readonly=True, index=True, copy=False, default='New')
    required_date = fields.Date(string='Required Date', tracking=True, default=lambda self: fields.Date.add(fields.Date.today(), days=7))
    approved_supplier_id = fields.Many2one('res.partner', string='Approved Supplier')
    product_line_ids = fields.One2many('supplies.rfp.product.line', 'rfp_id', string='Product Lines')
    rfq_ids = fields.One2many('purchase.order', 'rfp_id', string='RFQs', domain=lambda self: self._get_rfq_domain())
    num_rfq = fields.Integer(string='Number of RFQs', compute='_compute_num_rfq', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    date_approve = fields.Date(string='Reviewed On', readonly=True) # when an approver either approves or rejects
    review_by = fields.Many2one('res.users', string='Review By', readonly=True) # an approver either approves or rejects
    date_accept = fields.Date(string='Accepted On', readonly=True)

    @api.depends('product_line_ids', 'product_line_ids.subtotal_price')
    def _compute_total_amount(self):
        for rfp in self:
            rfp.total_amount = sum(rfp.product_line_ids.mapped('subtotal_price'))

    @api.model
    def _get_rfq_domain(self):
        aprrover_states = ['recommendation', 'accepted']
        if self.env.user.has_group('supplies.group_supplies_approver'):
            return [('recommended', '=', True)] if self.state in aprrover_states else [('id', '=', -1)]
        return []

    def create(self, vals_list):
        if isinstance(vals_list, list):
            for vals in vals_list:
                if vals.get('rfp_number', 'New') == 'New':
                    vals['rfp_number'] = self.env['ir.sequence'].next_by_code('supplies.rfp.number') or 'New'
        else:
            if vals_list.get('rfp_number', 'New') == 'New':
                vals_list['rfp_number'] = self.env['ir.sequence'].next_by_code('supplies.rfp.number') or 'New'
        return super(SuppliesRfp, self).create(vals_list)

    @api.depends('rfq_ids')
    def _compute_num_rfq(self):
        for rfp in self:
            rfp.num_rfq = len(rfp.rfq_ids)

    @rfp_state_flow('draft')
    def action_submit(self):
        if not self.product_line_ids:
            raise UserError('Please add product lines before submitting.')
        self.write({'state': 'submitted'})
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': get_approver_emails(self.env),
            'subject': f'New RFP Submitted {self.rfp_number}',
        }
        contexts = {
            'reviwer_name': self.env.user.name,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('supplies.email_template_model_supplies_rfp_submission').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    @rfp_state_flow('submitted')
    def action_return_to_draft(self):
        self.state = 'draft'

    @rfp_state_flow('submitted')
    def action_approve(self):
        self.write({'state': 'approved', 'date_approve': fields.Date.today(), 'review_by': self.env.user.id})
        # notify reviewer
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': self.create_uid.login,
            'subject': f'RFP Approved {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('supplies.email_template_model_supplies_rfp_approved_reviewer').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)
        # notify suppliers
        template = self.env.ref('supplies.email_template_model_supplies_rfp_approved_supplier').sudo()
        supplier_emails = get_supplier_emails(self.env)
        email_values['subject'] = f"New Request for Purchase Available {self.rfp_number}"
        for email in supplier_emails:
            email_values['email_to'] = email
            template.with_context(**contexts).send_mail(self.id, email_values=email_values)


    @rfp_state_flow('submitted')
    def action_reject(self):
        self.write({'state': 'rejected', 'review_by': self.env.user.id, 'date_approve': fields.Date.today()})
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': self.create_uid.login,
            'subject': f'RFP Rejected {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
            'approver_name': self.env.user.name,
        }
        template = self.env.ref('supplies.email_template_model_supplies_rfp_rejected_reviewer').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    @rfp_state_flow('approved')
    def action_close(self):
        self.state = 'closed'

    @rfp_state_flow('closed')
    def action_recommendation(self):
        approved_rfqs = self.rfq_ids.filtered(lambda rfq: rfq.recommended)
        if not approved_rfqs:
            raise UserError('Please approve at least one RFQ before recommending.')
        self.state = 'recommendation'
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': get_approver_emails(self.env),
            'subject': f'RFQ Recommendation for {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('supplies.email_template_model_supplies_rfp_recommended').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    def action_view_purchase_order(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('rfp_id', '=', self.id), ('recommended', '=', True), ('partner_id', '=', self.approved_supplier_id.id)]
        return action