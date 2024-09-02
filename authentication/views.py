from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from authentication.serializers import UserRegistrationSerializer, UserLoginSerializer, UserWithTokenSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

COMMON_RESPONSES = {
    401: openapi.Response(description="Unauthorized"),
    400: openapi.Response(description="Bad Request"),
    500: openapi.Response(description="Internal Server Error"),
}

class UserRegistrationAPIView(CreateAPIView):
    """User registration view"""

    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: openapi.Response(description="User registered", schema=UserWithTokenSerializer),
            **COMMON_RESPONSES
    })
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            data=UserWithTokenSerializer({
                'auth_token': str(token),
                'user': user
            }).data,
            status=status.HTTP_201_CREATED
        )


class UserLoginAPIView(GenericAPIView):
    """User login view"""

    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="Login a new user",
        responses={
            200: openapi.Response(description="User logged in", schema = UserWithTokenSerializer),
            **COMMON_RESPONSES
    })
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            data=UserWithTokenSerializer({
                'auth_token': str(token),
                'user': user
            }).data,
            status=status.HTTP_200_OK,
        )
