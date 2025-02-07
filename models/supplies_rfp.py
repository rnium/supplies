from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.fields import apply_required


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

    def action_submit(self):
        if not self.product_line_ids:
            raise UserError('Please add product lines before submitting.')
        return self.write({'state': 'submitted', 'submitted_date': fields.Date.today()})

    def action_return_to_draft(self):
        if self.state == 'submitted':
            return self.write({'state': 'draft'})
        else:
            raise UserError('Only submitted RFPs can be returned to draft.')

    def action_approve(self):
        return self.write({'state': 'approved'})

    def action_reject(self):
        return self.write({'state': 'rejected'})

    def action_close(self):
        return self.write({'state': 'closed'})

    def action_recommendation(self):
        if self.state != 'closed':
            raise UserError('Only closed RFPs can be recommended.')
        approved_rfqs = self.rfq_ids.filtered(lambda rfq: rfq.recommended)
        if not approved_rfqs:
            raise UserError('Please approve at least one RFQ before recommending.')
        return self.write({'state': 'recommendation'})

    def action_accept(self):
        return self.write({'state': 'accepted'})