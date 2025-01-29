from typing import List, Tuple
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