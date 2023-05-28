import re

email_regex = r'^\S+@\S+\.\S+$'
phone_regex = r'^(\+98|0)?9\d{9}$'


def validate_phone(phone):
    return re.match(phone_regex, phone)


def validate_email(email):
    return re.match(email_regex, email)
