from datetime import datetime, timedelta
from logging import getLogger

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from api.models.friend_request_model import FriendRequest
from api.serializers.friends_request_serializer import FriendRequestSerializer, UserSerializer

logger = getLogger("django.request")

class FriendRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FriendshipView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = FriendRequestPagination

    @action(detail=False, methods=["POST"], url_path="send-request")
    def send_request(self, request):
        try:
            data = request.data
            recipient_username = data.get('recipient')
            if not recipient_username:
                return Response(
                    data={"message": "Recipient parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipient = User.objects.get(username=recipient_username)
            sender = request.user

            # Check if sender has sent more than 3 friend requests in the last minute
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_requests_count = FriendRequest.objects.filter(
                sender=sender, created_at__gte=one_minute_ago
            ).count()

            if recent_requests_count >= 3:
                return Response(
                    data={"message": "You cannot send more than 3 friend requests within a minute"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            friend_request, created = FriendRequest.objects.get_or_create(sender=sender, recipient=recipient)

            if not created:
                return Response(
                    data={"message": "Friend request already sent"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                data={"message": "Friend request sent successfully"},
                status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            return Response(
                data={"message": "Recipient user does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"An error occurred while sending friend request: {e}")
            return Response(
                data={"message": "An error occurred while sending friend request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["POST"], url_path="respond-request")
    def respond_request(self, request):
        try:
            data = request.data
            request_id = data.get('request_id')
            action = data.get('action')

            if not request_id or not action:
                return Response(
                    data={"message": "Request ID and action parameters are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                friend_request = FriendRequest.objects.get(id=request_id)
            except FriendRequest.DoesNotExist:
                return Response(
                    data={"message": "Friend request not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if action == 'accept':
                friend_request.status = 'accepted'
                friend_request.save()
                return Response(
                    data={"message": "Friend request accepted"},
                    status=status.HTTP_200_OK
                )
            elif action == 'reject':
                friend_request.status = 'rejected'
                friend_request.save()
                return Response(
                    data={"message": "Friend request rejected"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={"message": "Invalid action"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.exception(f"An error occurred while responding to friend request: {e}")
            return Response(
                data={"message": "An error occurred while responding to friend request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["GET"], url_path="friends")
    def list_friends(self, request):
        try:
            user = request.user
            friends = User.objects.filter(
                friend_requests_received__sender=user,
                friend_requests_received__status='accepted'
            ) | User.objects.filter(
                friend_requests_sent__recipient=user,
                friend_requests_sent__status='accepted'
            )

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(friends, request)
            serializer = UserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.exception(f"An error occurred while listing friends: {e}")
            return Response(
                data={"message": "An error occurred while listing friends"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["GET"], url_path="pending-requests")
    def list_pending_requests(self, request):
        try:
            user = request.user
            pending_requests = FriendRequest.objects.filter(recipient=user, status='pending')

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(pending_requests, request)
            serializer = FriendRequestSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.exception(f"An error occurred while listing pending friend requests: {e}")
            return Response(
                data={"message": "An error occurred while listing pending friend requests"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
