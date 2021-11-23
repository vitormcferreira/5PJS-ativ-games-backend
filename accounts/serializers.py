from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'password']
        # https://www.django-rest-framework.org/api-guide/serializers/#additional-keyword-arguments
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario(username=validated_data['username'])
        # seta a senha (faz o hash)
        user.set_password(validated_data['password'])
        user.save()
        return user

    # https://www.django-rest-framework.org/api-guide/serializers/#validation
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as err:
            raise ValidationError

        return value
