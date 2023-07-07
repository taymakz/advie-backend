from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from site_account.user_management.models import User
from site_account.user_management.serializers import UserSerializer, UserEditProfileSerializer
from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_notification.verification_notification.models import VerifyOTPService
from site_utils.validator.regexes import validate_phone, validate_email, validate_password


# Get Current User Detail
class RequestCurrentUserView(RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.serializer_class(user)

            return BaseResponse(data=serializer.data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except InvalidToken as e:
            return BaseResponse(status=status.HTTP_401_UNAUTHORIZED,
                                message=ResponseMessage.FAILED.value)


# User Authentication -------------------------

# User Authentication Check

class AuthenticationCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username').lower()

        if not username:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_EMAIL_OR_PHONE.value)

        if validate_phone(username):
            username = f"0{username}" if len(username) == 10 else username

            otp_service = VerifyOTPService.objects.filter(type='PHONE', to=username, usage='AUTHENTICATE').order_by(
                '-id').first()
            user = User.objects.filter(phone=username).first()

            if not user or not user.has_usable_password():
                if otp_service:
                    if otp_service.is_expired():
                        otp_service.delete()
                        otp_service = None

                if not otp_service:
                    new_otp_service = VerifyOTPService(type='PHONE', to=username, usage='AUTHENTICATE')
                    new_otp_service.save()
                    new_otp_service.send_otp()

                return BaseResponse(data={'section': 'OTP'}, status=status.HTTP_200_OK,
                                    message=ResponseMessage.PHONE_OTP_SENT.value.format(username=username))

            if otp_service and otp_service.is_expired():
                otp_service.delete()

            return BaseResponse(data={'section': 'PASSWORD'}, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        elif validate_email(username):
            otp_service = VerifyOTPService.objects.filter(type='EMAIL', to=username, usage='AUTHENTICATE').order_by(
                '-id').first()
            user = User.objects.filter(email=username).first()

            if not user or not user.has_usable_password():
                if otp_service:
                    if otp_service.is_expired():
                        otp_service.delete()
                        otp_service = None

                if not otp_service:
                    new_otp_service = VerifyOTPService(type='EMAIL', to=username, usage='AUTHENTICATE')
                    new_otp_service.save()
                    new_otp_service.send_otp()

                return BaseResponse(data={'section': 'OTP'}, status=status.HTTP_200_OK,
                                    message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=username))

            if otp_service and otp_service.is_expired():
                otp_service.delete()

            return BaseResponse(data={'section': 'PASSWORD'}, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_EMAIL_OR_PHONE.value)


# User Password Authentication

class PasswordAuthenticationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username', None).lower()
        password = request.data.get('password', None)

        if not username or not password:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        try:
            username_type = 'PHONE' if validate_phone(username) else 'EMAIL'
            username = f"0{username}" if username_type == 'PHONE' and len(username) == 10 else username

            user = User.objects.get(phone=username) if username_type == 'PHONE' else User.objects.get(
                email=username)
            if not user.check_password(password):
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.AUTH_WRONG_PASSWORD.value)
            # Logged in

            # Generate JWT token for the user
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)

            user_token = {
                'access': str(access_token),
                'refresh': str(refresh_token),
            }
            return BaseResponse(data=user_token, status=status.HTTP_200_OK,
                                message=ResponseMessage.AUTH_LOGIN_SUCCESSFULLY.value)

        except User.DoesNotExist:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.AUTH_WRONG_PASSWORD.value)


# User OTP Authentication

class OTPAuthenticationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username', None).lower()
        otp = request.data.get('otp', None)

        if not username or not otp:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
        username_type = 'PHONE' if validate_phone(username) else 'EMAIL'
        username = f"0{username}" if username_type == 'PHONE' and len(username) == 10 else username

        user = None
        try:

            user = User.objects.get(phone=username) if username_type == 'PHONE' else User.objects.get(
                email=username)

        except User.DoesNotExist:
            otp_service = VerifyOTPService.objects.filter(type=username_type, to=username, code=otp,
                                                          usage='AUTHENTICATE').order_by(
                '-id').first()
            if otp_service and not otp_service.is_expired():
                otp_service.delete()

                if username_type == 'PHONE':
                    user = User.objects.create_user(phone=username, password=None)

                elif username_type == 'EMAIL':
                    user = User.objects.create_user(email=username, password=None)

                # User Created successFully and logged in
            else:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.AUTH_WRONG_OTP.value)
        else:

            otp_service = VerifyOTPService.objects.filter(type=username_type, to=username, code=otp,
                                                          usage='AUTHENTICATE').order_by(
                '-id').first()
            if otp_service and not otp_service.is_expired():
                otp_service.delete()
                # logged in
            else:

                if otp_service and otp_service.is_expired():
                    otp_service.delete()
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.AUTH_WRONG_OTP.value)

        # Generate JWT token for the user
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        user_token = {
            'access': str(access_token),
            'refresh': str(refresh_token),
        }
        return BaseResponse(data=user_token, status=status.HTTP_200_OK,
                            message=ResponseMessage.AUTH_LOGIN_SUCCESSFULLY.value)


# User Reset Password -------------------------
class ForgotPasswordCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username').lower()

        if validate_phone(username):
            username = f"0{username}" if len(username) == 10 else username

            otp_type = 'PHONE'
            message = ResponseMessage.PHONE_OTP_SENT.value


        elif validate_email(username):
            otp_type = 'EMAIL'
            message = ResponseMessage.EMAIL_OTP_SENT.value
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_EMAIL_OR_PHONE.value)

        try:
            username_type = 'PHONE' if validate_phone(username) else 'EMAIL'
            user = User.objects.get(phone=username) if username_type == 'PHONE' else User.objects.get(
                email=username)
        except User.DoesNotExist:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.RESET_PASSWORD_USER_NOT_FOUND.value)

        otp_service, _ = VerifyOTPService.objects.get_or_create(
            type=otp_type, to=username, usage='RESET_PASSWORD')

        if otp_service.is_expired():
            otp_service.delete()
            otp_service = None

        if not otp_service:
            otp_service = VerifyOTPService.objects.create(type=otp_type, to=username, usage='RESET_PASSWORD')
            otp_service.send_otp()

        return BaseResponse(status=status.HTTP_200_OK,
                            message=message.format(username=username))


class ForgotPasswordOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username', None).lower()
        otp = request.data.get('otp', None)

        if not username or not otp:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        username_type = 'PHONE' if validate_phone(username) else 'EMAIL'
        username = f"0{username}" if username_type == 'PHONE' and len(username) == 10 else username
        user = User.objects.filter(phone=username).first() if username_type == 'PHONE' else User.objects.filter(
            email=username).first()

        if not user:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.RESET_PASSWORD_USER_NOT_FOUND.value)

        otp_service = VerifyOTPService.objects.filter(type=username_type, to=username, code=otp,
                                                      usage='RESET_PASSWORD').order_by('-id').first()

        if not otp_service or otp_service.is_expired():
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.AUTH_WRONG_OTP.value)

        otp_service.delete()
        user.generate_forgot_password_token()

        return BaseResponse(data={'token': user.forgot_password_token}, status=status.HTTP_200_OK)


class ForgotPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username').lower()
        token = request.data.get('token')
        token = token.strip('"')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        is_valid, message = validate_password(password)
        if not is_valid:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=message)
        if password != confirm_password:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PASSWORD_CONFIRM_MISMATCH.value)
        username_type = 'PHONE' if validate_phone(username) else 'EMAIL'
        username = f"0{username}" if username_type == 'PHONE' and len(username) == 10 else username

        user = User.objects.filter(phone=username).first() if username_type == 'PHONE' else User.objects.filter(
            email=username).first()

        if (user and token) and (str(user.forgot_password_token) == token):

            user.set_password(password)
            user.revoke_all_tokens()
            user.generate_forgot_password_token()
            user.save()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.RESET_PASSWORD_SUCCESSFULLY.value)
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


# Request OTP For User

class RequestOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        to = request.data.get('to', None).lower()
        otp_usage = request.data.get('otp_usage', None)

        if not to or not otp_usage:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        if validate_phone(to):
            phone = to

            phone = f"0{phone}" if len(phone) == 10 else phone

            otp_service = VerifyOTPService.objects.filter(type='PHONE', to=phone, usage=otp_usage).order_by(
                '-id').first()
            if otp_service:
                if otp_service.is_expired():
                    otp_service.delete()
                    new_otp_service = VerifyOTPService.objects.create(type='PHONE', to=phone, usage=otp_usage)
                    new_otp_service.send_otp()

                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
                else:
                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
            else:
                new_otp_service = VerifyOTPService.objects.create(type='PHONE', to=phone, usage=otp_usage)

                new_otp_service.send_otp()
                return BaseResponse(status=status.HTTP_200_OK,
                                    message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
        elif validate_email(to):
            email = to

            otp_service = VerifyOTPService.objects.filter(type='EMAIL', to=email, usage=otp_usage).order_by(
                '-id').first()
            if otp_service:
                if otp_service.is_expired():
                    otp_service.delete()
                    new_otp_service = VerifyOTPService.objects.create(type='EMAIL', to=email, usage=otp_usage)
                    new_otp_service.send_otp()

                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
                else:
                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
            else:
                new_otp_service = VerifyOTPService.objects.create(type='EMAIL', to=email, usage=otp_usage)

                new_otp_service.send_otp()
                return BaseResponse(status=status.HTTP_200_OK,
                                    message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


# Logout USer

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.AUTH_LOGOUT_SUCCESSFULLY.value)



        except Exception as e:

            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class UserUpdateDetailView(UpdateAPIView):
    serializer_class = UserEditProfileSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = BaseResponse(status=status.HTTP_204_NO_CONTENT,
                                message=ResponseMessage.SUCCESS.value)
        return response


class UserEditPhoneRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        phone = request.data.get('phone', None).lower()
        otp_usage = request.data.get('otp_usage', None)

        if not phone or not otp_usage:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        if validate_phone(phone):
            phone = f"0{phone}" if len(phone) == 10 else phone
            if User.objects.filter(phone=phone).exists():
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.USER_PANEL_PHONE_ALREADY_EXIST.value)
            otp_service = VerifyOTPService.objects.filter(type='PHONE', to=phone, usage=otp_usage).order_by(
                '-id').first()
            if otp_service:
                if otp_service.is_expired():
                    otp_service.delete()
                    new_otp_service = VerifyOTPService.objects.create(type='PHONE', to=phone, usage=otp_usage)
                    new_otp_service.send_otp()

                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
                else:
                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
            else:
                new_otp_service = VerifyOTPService.objects.create(type='PHONE', to=phone, usage=otp_usage)

                new_otp_service.send_otp()
                return BaseResponse(status=status.HTTP_200_OK,
                                    message=ResponseMessage.PHONE_OTP_SENT.value.format(username=phone))
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_PHONE.value)


class UserEditPhoneConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        phone = request.data.get('phone', None).lower()
        otp = request.data.get('otp', None)
        user = self.request.user

        phone = f"0{phone}" if len(phone) == 10 else phone

        if not phone or not otp or (phone == user.phone):
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        otp_service = VerifyOTPService.objects.filter(type='PHONE', to=phone, code=otp,
                                                      usage='VERIFY').order_by('-id').first()

        if not otp_service or otp_service.is_expired():
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.AUTH_WRONG_OTP.value)

        otp_service.delete()
        user.phone = phone

        user.save()
        return BaseResponse(status=status.HTTP_200_OK, message=ResponseMessage.SUCCESS.value)


class UserEditEmailRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        email = request.data.get('email', None).lower()
        otp_usage = request.data.get('otp_usage', None)

        if not email or not otp_usage:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        if validate_email(email):
            if User.objects.filter(email=email).exists():
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.USER_PANEL_EMAIL_ALREADY_EXIST.value)
            otp_service = VerifyOTPService.objects.filter(type='EMAIL', to=email, usage=otp_usage).order_by(
                '-id').first()
            if otp_service:
                if otp_service.is_expired():
                    otp_service.delete()
                    new_otp_service = VerifyOTPService.objects.create(type='EMAIL', to=email, usage=otp_usage)
                    new_otp_service.send_otp()

                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
                else:
                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
            else:
                new_otp_service = VerifyOTPService.objects.create(type='EMAIL', to=email, usage=otp_usage)

                new_otp_service.send_otp()
                return BaseResponse(status=status.HTTP_200_OK,
                                    message=ResponseMessage.EMAIL_OTP_SENT.value.format(username=email))
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_EMAIL.value)


class UserEditEmailConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        email = request.data.get('email', None).lower()
        otp = request.data.get('otp', None)
        user = self.request.user

        if not email or not otp or (email == user.email):
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        otp_service = VerifyOTPService.objects.filter(type='EMAIL', to=email, code=otp,
                                                      usage='VERIFY').order_by('-id').first()

        if not otp_service or otp_service.is_expired():
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.AUTH_WRONG_OTP.value)

        otp_service.delete()
        user.email = email

        user.save()
        return BaseResponse(status=status.HTTP_200_OK, message=ResponseMessage.SUCCESS.value)


class UserEditPassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        current_password = request.data.get('current_password')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        user = self.request.user

        if user.has_usable_password() and not user.check_password(current_password):
            return BaseResponse(data={'error_input_name': 'current_password'}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.USER_PANEL_CURRENT_PASSWORD_WRONG.value)
        is_valid, message = validate_password(password)
        if not is_valid:
            return BaseResponse(data={'error_input_name': 'password'}, status=status.HTTP_400_BAD_REQUEST,
                                message=message)
        if password != confirm_password:
            return BaseResponse(data={'error_input_name': 'confirm_password'}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PASSWORD_CONFIRM_MISMATCH.value)

        user.set_password(password)
        user.revoke_all_tokens()
        user.generate_forgot_password_token()
        user.save()

        # Generate JWT token for the user
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        user_token = {
            'access': str(access_token),
            'refresh': str(refresh_token),
        }
        return BaseResponse(data=user_token, status=status.HTTP_200_OK,
                            message=ResponseMessage.RESET_PASSWORD_SUCCESSFULLY.value)
