from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', index=True, copy=False)
    warrenty_period = fields.Integer(string='Warrenty Period (in months)')
    score = fields.Float(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended', default=False)
    rfp_state = fields.Selection(related='rfp_id.state', string='RFP State')

    def action_accept(self):
        self.rfp_id.write({'state': 'accepted', 'approved_supplier_id': self.partner_id.id})
        self.write({'state': 'purchase'})
        other_rfqs = self.env['purchase.order'].search(
            [
                ('rfp_id', '=', self.rfp_id.id),
                ('id', '!=', self.id),
            ]
        )
        other_rfqs.write({'state': 'cancel'})
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

