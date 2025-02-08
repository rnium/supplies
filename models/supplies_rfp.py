from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.rfp_utils import rfp_state_flow


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
    submitted_date = fields.Date(string='Submitted On', readonly=True)

    @api.model
    def _get_rfq_domain(self):
        aprrover_states = ['recommendation', 'accepted']
        if self.env.user.has_group('supplies.group_supplies_approver'):
            return [('recommended', '=', True)] if self.state in aprrover_states else [('id', '=', -1)]
        return []

    def create(self, vals_list):
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
        return self.write({'state': 'submitted', 'submitted_date': fields.Date.today()})

    @rfp_state_flow('submitted')
    def action_return_to_draft(self):
        self.state = 'draft'

    @rfp_state_flow('submitted')
    def action_approve(self):
        self.state = 'approved'

    @rfp_state_flow('submitted')
    def action_reject(self):
        self.state = 'rejected'

    @rfp_state_flow('approved')
    def action_close(self):
        self.state = 'closed'

    @rfp_state_flow('closed')
    def action_recommendation(self):
        approved_rfqs = self.rfq_ids.filtered(lambda rfq: rfq.recommended)
        if not approved_rfqs:
            raise UserError('Please approve at least one RFQ before recommending.')
        self.state = 'recommendation'