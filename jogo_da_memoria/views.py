from django.db.models.query import QuerySet
from rest_framework import views, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import force_authenticate

from .models import Ranking, JogoDaMemoria
from .serializers import RankingSerializer, JogoDaMemoriaSerializer
from accounts.models import Usuario


class JogoAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        user = Usuario.objects.get(username='admin')
        force_authenticate(request, user=user)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: Request):
        """
        Caso não exista nenhum jogo instanciado pelo jogador, cria um novo, 
        salva na sessão e retorna os números das cartas.
        Caso já exista um jogo instanciado, retorna o jogo.
        """
        try:
            jogo = JogoDaMemoria.objects.get(usuario=self.request.user)
        except JogoDaMemoria.DoesNotExist:
            jogo = JogoDaMemoria.novo_jogo(self.request.user)

        serializer = JogoDaMemoriaSerializer(jogo)

        return Response({
            'jogo': serializer.data
        })

    def post(self, request: Request):
        """
        Recebe um par de cartas e faz um movimento.
        Retorna as cartas enviadas, os valores das cartas, acertos e jogadas.
        Caso o jogo tenha encerrado, registra a pontuação do jogador.
        """
        try:
            jogo: JogoDaMemoria = JogoDaMemoria.objects.get(
                usuario=self.request.user)
            carta1 = request.data['carta1']
            carta2 = request.data['carta2']

            valor_carta1, valor_carta2 = jogo.faz_movimento(carta1, carta2)

            serializer = JogoDaMemoriaSerializer(jogo)
            # resposta padrão
            dict_response = {
                'jogo': serializer.data,
            }

            # salva o ranking do usuario
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
                return Response(dict_response, status=406)
        except:
            return Response(status=404)

    def delete(self, request: Request):
        JogoDaMemoria.objects.filter(usuario=self.request.user).delete()
        return Response()


class RankingListAPIView(generics.ListAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer

    def normalizar_dados(self, data):
        result = [{
            'id': obj['id'],
            'jogadas': obj['jogadas'],
            'erros': obj['erros'],
            'user_data': {
                'id': obj['usuario']['id'],
                'username': obj['usuario']['username'],
            }
        } for obj in data]
        return result

    def list(self, request, *args, **kwargs):
        """
        Retorna uma lista com o ranking.
        """
        queryset: QuerySet = self.filter_queryset(self.get_queryset())

        queryset = queryset.select_related('usuario')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.normalizar_dados(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(self.normalizar_dados(serializer.data))
