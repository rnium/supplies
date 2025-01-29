import random


def generate_otp() -> int:
    """
    Generates a 6 digit OTP
    """
    return random.randint(100000, 999999)


def format_response(status: str, message: str, data: dict = None) -> dict:
    """
    Formats the response
    """
    return {
        'status': status,
        'message': message,
        'data': data
    }