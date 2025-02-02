from typing import List, Tuple
from odoo.api import Environment

def format_response(status: str, message: str, data: dict = None) -> dict:
    """
    Formats the response
    """
    return {
        'status': status,
        'message': message,
        'data': data
    }
    
def validate_email_address(request, email: str) -> Tuple[bool, str]:
    """
    Validates the given email address
    """
    # First check if its blacklisted
    blacklist = request.env['bjit_supplies.registration.blacklist'].sudo().search(
        [('email', '=', email), ('active', '=', True)]
    )
    if blacklist:
        return False, 'Email address is blacklisted'
    # check if user is already registered
    user = request.env['res.users'].sudo().search(
        [('login', '=', email)]
    )
    if user:
        return False, 'Email address is already registered'
    return True, ''


def create_supplier_registration(env: Environment, data: dict):
    # create the contacts first
    contact_names = ['primary_contact_id', 'finance_contact_id', 'authorized_contact_id']
    for name in contact_names:
        contact_data = data.pop(name, {})
        existing_contact = env['bjit_supplies.contact'].sudo().search(
            [('email', '=', contact_data.get('email'))]
        )
        if existing_contact:
            data[name] = existing_contact.id
        else:
            new_contact = env['bjit_supplies.contact'].sudo().create(contact_data)
            data[name] = new_contact.id
    # create the client references
    client_refs = data.pop('client_ref_ids', [])
    client_ref_ids = []
    for client_ref in client_refs:
        existing_client_ref = env['bjit_supplies.contact'].sudo().search(
            [('email', '=', client_ref.get('email'))]
        )
        if existing_client_ref:
            client_ref_ids.append((4, existing_client_ref.id))
        else:
            client_ref_ids.append((0, 0, client_ref))
    data['client_ref_ids'] = client_ref_ids
    # create the registration
    env['bjit_supplies.registration'].sudo().create(data)
        