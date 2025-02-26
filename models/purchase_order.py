from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', index=True, copy=False)
    warrenty_period = fields.Integer(string='Warrenty Period (in months)')
    score = fields.Float(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended', default=False)

    def action_accept(self):
        self.rfp_id.write({'state': 'accepted', 'approved_supplier_id': self.partner_id.id, 'date_accept': fields.Date.today()})
        self.button_confirm()
        # updating RFP product line prices
        for line in self.rfp_id.product_line_ids:
            rfq_line = self.order_line.filtered(lambda x: x.product_id == line.product_id)
            line.write({
                'unit_price': rfq_line.price_unit,
                'delivery_charge': rfq_line.delivery_charge,
            })
        # cancelling other RFQs
        other_rfqs = self.env['purchase.order'].search(
            [
                ('rfp_id', '=', self.rfp_id.id),
                ('id', '!=', self.id),
            ]
        )
        other_rfqs.button_cancel()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'supplies.rfp',
            'view_mode': 'form',
            'res_id': self.rfp_id.id,
            'target': 'current',
        }

    @api.constrains('recommended')
    def _check_recommended(self):
        for order in self:
            if order.recommended:
                existing_recommendation = self.env['purchase.order'].search(
                    [
                        ('recommended', '=', True),
                        ('rfp_id', '=', order.rfp_id.id),
                        ('partner_id', '=', order.partner_id.id),
                        ('id', '!=', order.id),
                    ]
                )
                if len(existing_recommendation):
                    raise UserError(f'The supplier {order.partner_id.name} is recommended multiple times for the same RFP.')

    @api.depends_context('lang')
    @api.depends('order_line.taxes_id', 'order_line.price_unit', 'order_line.delivery_charge', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            line_dicts = []
            for line in order_lines:
                line_dict = line._convert_to_tax_base_line_dict()
                line_dict['price_unit'] += line.delivery_charge / line.product_qty if line.product_qty else line.delivery_charge
                line_dicts.append(line_dict)
            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                line_dicts,
                order.currency_id or order.company_id.currency_id,
            )

    @api.model
    def get_purchase_order_sudo(self, domain, fields):
        return self.sudo().search_read(domain, fields)
