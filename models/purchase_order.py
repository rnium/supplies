from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', ondelete='cascade', index=True, copy=False)
    warrenty_period = fields.Integer(string='Warrenty Period (in months)')
    score = fields.Float(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended', default=False)
    rfp_state = fields.Selection(related='rfp_id.state', string='RFP State')

    def action_accept(self):
        self.rfp_id.write({'state': 'accepted', 'approved_supplier_id': self.partner_id.id})
        self.write({'state': 'purchase'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'supplies.rfp',
            'view_mode': 'form',
            'res_id': self.rfp_id.id,
            'target': 'current',
        }

    @api.onchange('recommended')
    def _onchange_recommended(self):
        if not self.recommended:
            return
        existing_recommendation = self.env['purchase.order'].search(
            [
                ('recommended', '=', True),
                ('rfp_id', '=', self.rfp_id.id.origin),
                ('partner_id', '=', self.partner_id.id),
                ('id', '!=', self.id.origin),
            ]
        )
        if len(existing_recommendation):
            raise UserError('This supplier is already recommended for this RFP.')
