from typing import List, Tuple
from odoo.api import Environment
from urllib.parse import urlencode

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
    blacklist = request.env['mail.blacklist'].sudo().search(
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
    # check if already applied
    registration = request.env['supplies.registration'].sudo().search(
        [('email', '=', email)]
    )
    if registration:
        return False, 'You have already applied'
    return True, ''

def create_supplier_registration(env: Environment, data: dict):
    # create the contacts first
    contact_names = ['primary_contact_id', 'finance_contact_id', 'authorized_contact_id']
    for name in contact_names:
        contact_data = data.pop(name, {})
        existing_contact = env['supplies.contact'].sudo().search(
            [('email', '=', contact_data.get('email'))]
        )
        if existing_contact:
            data[name] = existing_contact.id
        else:
            new_contact = env['supplies.contact'].sudo().create(contact_data)
            data[name] = new_contact.id
    # create the client references
    client_refs = data.pop('client_ref_ids', [])
    client_ref_ids = []
    for client_ref in client_refs:
        existing_client_ref = env['supplies.contact'].sudo().search(
            [('email', '=', client_ref.get('email'))]
        )
        if existing_client_ref:
            client_ref_ids.append((4, existing_client_ref.id))
        else:
            client_ref_ids.append((0, 0, client_ref))
    data['client_ref_ids'] = client_ref_ids
    # create the registration
    return env['supplies.registration'].sudo().create(data)

def render_qweb_template(env: Environment, template_name: str, data: dict = {}):
    """
    Renders a QWeb template
    """
    return env['ir.qweb']._render(template_name, data)

def format_labels(*labels):
    formatted_labels = []

    for label in labels:
        # Replace underscores with spaces and capitalize each word
        if isinstance(label, str):
            formatted_label = label.replace('_', ' ').title()
        else:
            formatted_label = str(label)
        formatted_labels.append(formatted_label)

    return ", ".join(formatted_labels)

def format_errors(errors: List[dict]):
    out = []
    for error_dict in errors:
        # value: {'loc': ('field_name',), 'msg': 'Field required', 'type': 'missing'}
        # we want to change the field_name (loc) to a more readable format
        error_copy = error_dict.copy()
        error_copy['loc'] = format_labels(*error_copy['loc'])
        out.append(error_copy)
    return out

def render_registration_error_html(env: Environment, errors: List[dict]):
    """
    Renders the error HTML for the registration form modal
    """
    formatted_erros = format_errors(errors)
    template_name = 'supplies.supplier_registration_error'
    html = render_qweb_template(env, template_name, {'errors': formatted_erros})
    return str(html)


def check_unique_tin_trade_lic(env: Environment, formdata):
    """
    Checks if the tin and trade license are unique
    """
    tin = formdata.get('vat')
    trade_lic = formdata.get('trade_license_number')
    if tin and env['res.partner'].sudo().search([('vat', '=', tin)]):
        return False
    if trade_lic and env['res.partner'].sudo().search([('trade_license_number', '=', trade_lic)]):
        return False
    return True


def generate_registration_url(env: Environment, registration_id: int) -> str:
    """
    Generates the registration URL
    """
    model_name = 'supplies.registration'
    
    action = env.ref('supplies.supplies_registration_reviewer_action', raise_if_not_found=False)
    action_id = action.id if action else 340
    
    cids = env.company.id
    
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
    
    params = {
        'id': registration_id,
        'model': model_name,
        'action': action_id,
        'view_type': 'form',
        'cids': cids,
    }
    fragment = urlencode(params)
    url = f"{base_url}/web#{fragment}"
    return url