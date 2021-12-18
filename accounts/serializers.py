from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'password']
        # https://www.django-rest-framework.org/api-guide/serializers/#additional-keyword-arguments
        extra_kwargs = {'password': {'write_only': True,
                                     'validators': [validate_password]}}

    def create(self, validated_data):
        user = Usuario(username=validated_data['username'])
        # seta a senha (faz o hash)
        user.set_password(validated_data['password'])
        user.save()
        return user
