from logging import getLogger

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api.serializers.user_serializer import UserSerializer

logger = getLogger("django.request")

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserView(viewsets.ViewSet):
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def list(self, request):
        queryset = User.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def create(self, request):
        try:
            data = request.data
            data['username'] = data.get("email")
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                user = User.objects.create_user(**validated_data)
                return Response(
                    data={"message": "User registered successfully"},
                    status=status.HTTP_201_CREATED
                )
            else:
                error_message = "Registration failed: "
                errors = serializer.errors
                for field, error in errors.items():
                    error_message += f"{field}: {error[0]}."
                logger.error(error_message)
                return Response(
                    data={"message": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.exception(f"An error occurred during registration: {e}")
            return Response(
                data={"message": "An error occurred during registration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["GET"], url_path="search")
    def search(self, request):
        keyword = request.query_params.get('keyword', '')
        if not keyword:
            return Response(
                data={"message": "Keyword parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Search by exact email match or partial username match
        queryset = User.objects.filter(email=keyword) | User.objects.filter(first_name__icontains=keyword)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
