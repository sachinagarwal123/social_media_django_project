from logging import getLogger

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from api.serializers.auth_serializer import AuthSerializer

logger = getLogger("django.request")


class LoginView(viewsets.ViewSet):

    @action(detail=False, methods=["POST"], url_path="login")
    def login(self, request):
        try:
            serializer = AuthSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data["email"]
                password = serializer.validated_data["password"]
                try:
                    user_obj = User.objects.get(username=username)
                    if not user_obj.is_active:
                        return Response(
                            data={"message": "Your account has been disabled"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except User.DoesNotExist:
                    return Response(
                        data={"message": "User with this email does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user = authenticate(request, username=username, password=password)
                if user:
                    refresh, access_token = self._generate_tokens(user)
                    logger.info(f"User {username} successfully logged in.")
                    return self._get_login_response(refresh, access_token)
            logger.error("Failed login attempt: Invalid credentials provided.")
            return Response(
                data={"message": "Please provide valid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"An error occurred during login: {e}")
            return Response(
                data={"message": "Please try again"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    def _generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return refresh, access_token

    @staticmethod
    def _get_login_response(refresh, access_token):
        return Response(
            data={
                "refresh_token": str(refresh),
                "access_token": str(access_token)
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["POST"], url_path="refresh")
    def get_refresh_token(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                data={"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response(
                data={'access_token': str(access_token)},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                data={"message": "Invalid Refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"An error occurred while refreshing token: {e}")
            return Response(
                data={"message": "Please try again"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
