from django.urls import path
from authentication.views import UserRegistrationAPIView, UserLoginAPIView

app_name = 'authentication'

urlpatterns = [
    path('authentication/register', UserRegistrationAPIView.as_view(), name="register"),
    path('authentication/login', UserLoginAPIView.as_view(), name="login"),
]
