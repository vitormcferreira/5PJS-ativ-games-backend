from rest_framework import serializers

from accounts.serializers import UsuarioSerializer
from jogo_da_memoria.models import Ranking


class RankingSerializer(serializers.ModelSerializer):
    # https://stackoverflow.com/questions/50996306/show-and-serialize-the-results-of-select-related-model-method
    usuario = UsuarioSerializer()

    class Meta:
        model = Ranking
        fields = '__all__'
