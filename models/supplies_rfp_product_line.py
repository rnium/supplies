from email.policy import default

from odoo import models, fields, api

class SuppliesRfpProductLine(models.Model):
    _name = 'supplies.rfp.product.line'
    _description = 'Request for Purchase Product Line'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_name = fields.Char(string='Product Name', related='product_id.name')
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')
    description = fields.Text(string='Description')
    product_qty = fields.Integer(string='Quantity')
    unit_price = fields.Monetary(string='Price')
    product_uom = fields.Many2one('uom.uom', string='UOM')
    subtotal_price = fields.Monetary(string='Subtotal', compute='_compute_subtotal_price', store=True)
    delivery_charge = fields.Monetary(string='Delivery Charge')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('product_qty', 'unit_price', 'delivery_charge')
    def _compute_subtotal_price(self):
        for rec in self:
            rec.subtotal_price = (rec.product_qty * rec.unit_price) + rec.delivery_charge