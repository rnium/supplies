from odoo import models, fields, api

class SuppliesRfp(models.Model):
    _name = 'supplies.rfp'
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
    required_date = fields.Date(string='Required Date', default=lambda self: fields.Date.add(fields.Date.today(), days=7))
    approved_supplier_id = fields.Many2one('res.partner', string='Approved Supplier')
    product_line_ids = fields.One2many('supplies.rfp.product.line', 'rfp_id', string='Product Lines')
    rfq_ids = fields.One2many('purchase.order', 'rfp_id', string='RFQs')

    def create(self, vals_list):
        if vals_list.get('rfp_number', 'New') == 'New':
            vals_list['rfp_number'] = self.env['ir.sequence'].next_by_code('supplies.rfp.number') or 'New'
        return super(SuppliesRfp, self).create(vals_list)