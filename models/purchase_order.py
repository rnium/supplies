from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', ondelete='cascade', index=True, copy=False)
    warrenty_period = fields.Integer(string='Warrenty Period (in months)')
    score = fields.Float(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended', default=False)
