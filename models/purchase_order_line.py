from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    delivery_charge = fields.Monetary(string='Delivery Charge')
    product_name = fields.Char(string='Product Name', related='product_id.name')
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')
    rfp_id = fields.Many2one('supplies.rfp', related="order_id.rfp_id")

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'delivery_charge')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = next(iter(tax_results['totals'].values()))
            amount_untaxed = totals['amount_untaxed']
            if line.delivery_charge:
                amount_untaxed += line.delivery_charge
            amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })