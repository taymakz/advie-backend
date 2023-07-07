from ippanel import Client

api_key = "tiFfLmfYlgQDqrclxgMyx2DnGx9nrSZZBfpLnbd_EQc="
sms = Client(api_key)


def send_otp_phone(to, code):
    pattern_values = {
        "code": str(code),
    }

    bulk_id = sms.send_pattern(
        "vuduuykm0qdri4w",  # pattern code
        "983000505",  # originator
        to,  # recipient
        pattern_values,  # pattern values
    )


def send_order_status_phone(to, id, pattern):
    pattern_values = {
        "id": id,
    }

    bulk_id = sms.send_pattern(
        pattern,  # pattern code
        "983000505",  # originator
        to,  # recipient
        pattern_values,  # pattern values
    )
