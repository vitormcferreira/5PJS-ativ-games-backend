from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .serializers import UsuarioSerializer

from .models import Usuario


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """
        Recebe username e senha, retorna um token caso autenticado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.validated_data['user']

        token, _ = Token.objects.get_or_create(user=usuario)

        return Response({
            'user_data': {
                'username': usuario.username,
            },
            'token': token.key,
        })


class UserCreateAPIView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def post(self, request, *args, **kwargs):
        """
        Recebe username e senha do usuário e efetua o cadastro.
        """
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # usuario = Usuario.objects.get(
        #     username=serializer.initial_data['username'],
        # )
        # token, _ = Token.objects.get_or_create(user=usuario)

        return Response({
            'user_data': {
                'username': {
                    'username': serializer.data['username']
                }
            },
            # 'token': token.key,
        })
