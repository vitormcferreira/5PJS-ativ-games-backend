from rest_framework import serializers

from accounts.serializers import UsuarioSerializer
from .models import JogoDaMemoria
from jogo_da_memoria.models import Ranking


class RankingSerializer(serializers.ModelSerializer):
    # https://www.django-rest-framework.org/api-guide/relations/#nested-relationships
    usuario = UsuarioSerializer()

    class Meta:
        model = Ranking
        fields = '__all__'


class JogoDaMemoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JogoDaMemoria
        fields = [
            'parsed_cartas',
            'jogadas',
            'acertos',
        ]
