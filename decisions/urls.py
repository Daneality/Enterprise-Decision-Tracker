from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DecisionViewSet

router = DefaultRouter()
router.register(r'decisions', DecisionViewSet, basename='decision')

print(router.urls)

urlpatterns = [
    path('', include(router.urls)),
]