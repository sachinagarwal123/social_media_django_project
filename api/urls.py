from django.http import JsonResponse
from django.urls import path
from rest_framework.routers import DefaultRouter
from api.views import (auth_view, user_view,friendship_view)

router = DefaultRouter()

router.register(r'auth', auth_view.LoginView, basename='login')
router.register(r'user', user_view.UserView, basename='user')
router.register(r'friendship', friendship_view.FriendshipView, basename='friendship')

urlpatterns = [

]

urlpatterns += router.urls