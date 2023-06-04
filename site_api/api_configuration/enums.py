from enum import Enum


class ResponseMessage(Enum):
    # Result Messages
    SUCCESS = "عملیات با موفقیت انجام شد"
    FAILED = "خطایی در انجام عملیات رخ داده است"

    # Validation Messages
    NOT_VALID_EMAIL_OR_PHONE = "شماره موبایل و یا ایمیل وارد شده نامعتبر میباشد"
    NOT_VALID_EMAIL = "ایمیل وارد شده نامعتبر میباشد"
    NOT_VALID_PHONE = "شماره موبایل شده نامعتبر میباشد"

    # Notification Messages
    PHONE_OTP_SENT = "کد تایید به شماره {username} پیامک شد"
    EMAIL_OTP_SENT = "کد تایید به ایمیل {username} ارسال شد"

    # Authentication
    AUTH_WRONG_PASSWORD = "کلمه عبور نادرست میباشد"
    AUTH_WRONG_OTP = "کد تایید نادرست میباشد"
    AUTH_LOGIN_SUCCESSFULLY = "با موفقیت وارد شدید"
    AUTH_LOGOUT_SUCCESSFULLY = "با موفقیت خارج شدید"

    # Reset Password
    RESET_PASSWORD_USER_NOT_FOUND = "کاربری با مشخصات وارد شده یافت نشد"
    RESET_PASSWORD_SUCCESSFULLY = "کلمه عبور جدید با موفقیت ثبت شد"
    PASSWORD_LENGTH_INVALID = "کلمه عبور باید حداقل 6 و حداکثر 16 حرف باشد"
    PASSWORD_CONFIRM_MISMATCH = "کلمه های عبور یکسان نمیباشند"
