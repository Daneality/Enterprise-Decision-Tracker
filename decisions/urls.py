from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DecisionViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'decisions', DecisionViewSet, basename='decision')

urlpatterns = [
    path('', include(router.urls)),
]
