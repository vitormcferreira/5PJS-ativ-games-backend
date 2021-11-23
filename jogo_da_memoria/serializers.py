from rest_framework import serializers

from accounts.serializers import UsuarioSerializer
from jogo_da_memoria.models import Ranking


class RankingSerializer(serializers.ModelSerializer):
    # https://www.django-rest-framework.org/api-guide/relations/#nested-relationships
    usuario = UsuarioSerializer()

    class Meta:
        model = Ranking
        fields = '__all__'
