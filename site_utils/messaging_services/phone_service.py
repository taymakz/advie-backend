import os

from dotenv import load_dotenv
from ippanel import Client

load_dotenv()

api_key = os.environ.get('FARAZ_SMS_API')
sms = Client(api_key)


def send_otp_phone(to, code):
    pattern_values = {
        "code": str(code),
    }

    bulk_id = sms.send_pattern(
        "2k3wp5r73wans40",  # pattern code
        "983000505",  # originator
        to,  # recipient
        pattern_values,  # pattern values
    )


def send_order_status_phone(to, pattern, number, track_code=None):
    pattern_values = {
        "order_number": str(number),
    }

    if track_code:
        pattern_values["track_code"] = track_code

    bulk_id = sms.send_pattern(
        pattern,  # pattern code
        "983000505",  # originator
        to,  # recipient
        pattern_values,  # pattern values
    )
