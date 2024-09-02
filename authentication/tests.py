import json
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestUserRegistrationAPIView:
    url = reverse("authentication:register")

    def test_invalid_password_validation(self):
        """
        Test to verify that a post call with invalid passwords fails
        """
        user_data = {
            "username": "testuser",
            "email": "test@testuser.com",
            "password": "123123",
            "confirm_password": "123123"
        }
        client = APIClient()
        response = client.post(self.url, user_data)
        assert 400 == response.status_code
    
    def test_invalid_confirm_password(self):
        """
        Test to verify that a post call with invalid confirm password fails
        """
        user_data = {
            "username": "testuser",
            "email": "test@testuser.com",
            "password": "123123@sdD",
            "confirm_password": "123123@sdDD"
        }
        client = APIClient()
        response = client.post(self.url, user_data)
        assert 400 == response.status_code

    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data is successful
        """
        user_data = {
            "username": "testuser",
            "email": "test@testuser.com",
            "password": "123123@sdD",
            "confirm_password": "123123@sdD"
        }
        client = APIClient()
        response = client.post(self.url, user_data)
        assert 201 == response.status_code
        assert "auth_token" in json.loads(response.content)
        user = User.objects.get(username="testuser")
        assert user.is_superuser == False
        assert user.is_staff == False

    def test_user_registration_as_admin(self):
        """
        Test to verify that a post call with user valid data and admin=True is successful
        """
        user_data = {
            "username": "adminuser",
            "email": "admin@testuser.com",
            "password": "123123@sdD",
            "confirm_password": "123123@sdD",
            "admin": True
        }
        client = APIClient()
        response = client.post(self.url, user_data)
        assert 201 == response.status_code
        assert "auth_token" in json.loads(response.content)
        user = User.objects.get(username="adminuser")
        assert user.is_superuser == True
        assert user.is_staff == True

    def test_unique_username_validation(self):
        """
        Test to verify that a post call with already existing username fails
        """
        user_data_1 = {
            "username": "testuser",
            "email": "test@testuser.com",
            "password": "123123@sdD",
            "confirm_password": "123123@sdD"
        }
        client = APIClient()
        response = client.post(self.url, user_data_1)
        assert 201 == response.status_code

        user_data_2 = {
            "username": "testuser",
            "email": "test2@testuser.com",
            "password": "123123@sdD",
            "confirm_password": "123123@sdD"
        }
        response = client.post(self.url, user_data_2)
        assert 400 == response.status_code


@pytest.mark.django_db
class TestUserLoginAPIView:
    url = reverse("authentication:login")

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_user(self.username, self.email, self.password)

    def test_authentication_without_password(self):
        client = APIClient()
        response = client.post(self.url, {"username": "snowman"})
        assert 400 == response.status_code

    def test_authentication_with_wrong_password(self):
        client = APIClient()
        response = client.post(self.url, {"username": self.username, "password": "I_know"})
        assert 400 == response.status_code

    def test_authentication_with_valid_data(self):
        client = APIClient()
        response = client.post(self.url, {"username": self.username, "password": self.password})
        assert 200 == response.status_code
        assert "auth_token" in json.loads(response.content)
