from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriberViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'subscribers', SubscriberViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]