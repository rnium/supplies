from odoo.api import Environment

def get_smtp_server_email(env: Environment):
    mail_server = env['ir.mail_server'].sudo().search([], order='sequence', limit=1)
    return mail_server.smtp_user

def get_approver_emails(env: Environment) -> str:
    group = env.ref('supplies.group_supplies_approver')
    approvers = env['res.users'].sudo().search([('groups_id', 'in', group.id)])
    email_list = approvers.mapped('login')
    return ','.join(email_list)

def get_supplier_emails(env: Environment) -> list:
    suppliers = env['res.users'].search([]).filtered(lambda u: u.partner_id and u.partner_id.supplier_rank >= 1)
    email_list = suppliers.mapped('login')
    return email_list
