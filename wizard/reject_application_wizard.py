from odoo import models, fields, api

class RejectApplicationWizard(models.TransientModel):
    _name = 'supplies.reject.application.wizard'
    _description = 'Reject Application Wizard'

    reason = fields.Text(string='Reason')
    registration_id = fields.Many2one('supplies.registration', string='Registration')

    def action_reject_application(self):
        self.registration_id.write({'state': 'rejected', 'comments': self.reason})
        return {'type': 'ir.actions.act_window_close'}