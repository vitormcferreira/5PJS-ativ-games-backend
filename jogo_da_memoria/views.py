from django.db.models.query import QuerySet
from game import JogoDaMemoria
from rest_framework import views, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from . import exceptions
from .models import Ranking
from .serializers import RankingSerializer


class JogoAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        jogo: JogoDaMemoria = self.request.session.get('jogo')

        if not jogo or jogo.jogo_encerrado():
            jogo = JogoDaMemoria.novo_jogo(3)

        self.request.session['jogo'] = jogo

        return Response({
            'jogo': jogo.parsed_cartas
        })

    def post(self, request: Request):
        jogo: JogoDaMemoria = self.request.session.get('jogo')

        if not jogo:
            raise exceptions.JogoInexistenteError()

        carta1 = request.data.get('carta1')
        carta2 = request.data.get('carta2')

        if not carta1 or not carta2:
            raise exceptions.CartaEmFaltaError()

        valor_carta1, valor_carta2 = jogo.faz_movimento(carta1, carta2)

        self.request.session['jogo'] = jogo

        dict_response = {
            'carta1': carta1,
            'carta2': carta2,
            'valor_carta1': valor_carta1,
            'valor_carta2': valor_carta2,
            'jogadas': str(jogo.jogadas),
            'acertos': str(jogo.acertos),
        }

        if jogo.jogo_encerrado():
            erros = jogo.jogadas - jogo.acertos
            try:
                ranking_usuario = Ranking.objects.get(
                    usuario=self.request.user)
                if ranking_usuario.erros > erros:
                    ranking_usuario.erros = erros
                    ranking_usuario.save()
            except:
                ranking_usuario = Ranking.objects.create(
                    usuario=self.request.user,
                    jogadas=jogo.jogadas,
                    erros=erros,
                )
            return Response(dict_response, status=250)

        if valor_carta1 == valor_carta2:
            return Response(dict_response)
        else:
            raise exceptions.MovimentoIncorretoError(dict_response)

    def delete(self, request: Request):
        if self.request.session.get('jogo'):
            del self.request.session['jogo']
        return True


class RankingListAPIView(generics.ListAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer

    def normalizar_dados(self, data):
        result = [{
            'jogadas': obj['jogadas'],
            'erros': obj['erros'],
            'user_data': {
                'id': obj['usuario']['id'],
                'username': obj['usuario']['username'],
            }
        } for obj in data]
        return result

    def list(self, request, *args, **kwargs):
        queryset: QuerySet = self.filter_queryset(self.get_queryset())

        queryset = queryset.select_related('usuario')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.normalizar_dados(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(self.normalizar_dados(serializer.data))
