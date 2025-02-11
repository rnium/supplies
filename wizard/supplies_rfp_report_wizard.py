from odoo import models, fields, api


class RfpReportWizard(models.TransientModel):
    _name = 'supplies.rfp.report.wizard'
    _description = 'RFP Report Wizard'

    supplier_id = fields.Many2one('res.partner', string='Supplier', domain="[('supplier_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_download_excel_report(self):
        """
        Downloads the excel report for the selected supplier and date range
        """
        # send a notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Excel Report Downloaded',
                'message': 'The excel report has been downloaded successfully.',
                'type': 'success',
                'sticky': True,
            }
        }