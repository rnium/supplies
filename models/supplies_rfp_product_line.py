from email.policy import default

from odoo import models, fields, api

class SuppliesRfpProductLine(models.Model):
    _name = 'supplies.rfp.product.line'
    _description = 'Request for Purchase Product Line'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity')
    unit_price = fields.Monetary(string='Price')
    subtotal_price = fields.Monetary(string='Subtotal', compute='_compute_subtotal_price', store=True)
    delivery_charge = fields.Monetary(string='Delivery Charge')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def _compute_subtotal_price(self):
        for rec in self:
            rec.subtotal_price = (rec.product_qty * rec.unit_price) + rec.delivery_charge