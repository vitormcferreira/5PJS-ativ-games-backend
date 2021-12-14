from rest_framework import serializers

from .models import JogoDaMemoria
from jogo_da_memoria.models import Ranking


class RankingSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Ranking
        fields = [
            'username',
            'erros',
        ]


class JogoDaMemoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JogoDaMemoria
        fields = [
            'cartas',
            'jogadas',
            'acertos',
            'carta_anterior',
        ]
