from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password


from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    admin = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "confirm_password", "date_joined", "admin")
        read_only_fields = ("id", "date_joined")

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        attrs.pop('confirm_password')
        attrs['password'] = make_password(attrs['password'])
        return attrs
    
    def create(self, validated_data):
        admin = validated_data.pop('admin', False)
        user = super().create(validated_data)
        if admin:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    default_error_messages = {
        'inactive_account': 'User account is disabled.',
        'invalid_credentials': 'Unable to login with provided credentials.'
    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'])


class UserSerializer(serializers.ModelSerializer):
    """Serializer for read-only user model"""
    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined", "is_superuser")
        read_only_fields = fields

class UserWithTokenSerializer(serializers.Serializer):
    """Serializer for user with token"""
    auth_token = serializers.CharField()
    user = UserSerializer()

    class Meta:
        fields = ['auth_token', 'user']
