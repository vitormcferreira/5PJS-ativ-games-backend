from django.db import transaction
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from rest_framework import views, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Ranking, JogoDaMemoria
from .serializers import RankingSerializer, JogoDaMemoriaSerializer


class JogoAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    QTD_CARTAS = 6

    PAR_CORRETO_STATUS_CODE = 240
    JOGO_ENCERRADO_STATUS_CODE = 250

    def get(self, request: Request):
        """
        Retorna um jogo existente ou um novo.
        """
        try:
            jogo = JogoDaMemoria.objects.get(usuario=self.request.user)
        except JogoDaMemoria.DoesNotExist:
            jogo = JogoDaMemoria.novo_jogo(self.request.user, self.QTD_CARTAS)

        serializer = JogoDaMemoriaSerializer(jogo)

        return Response({
            **serializer.data
        })

    def post(self, request: Request):
        status_code = 200
        try:
            # obter carta
            carta = request.data['carta']

            jogo: JogoDaMemoria = JogoDaMemoria.objects.get(
                usuario=self.request.user)

            valor_carta = jogo.cartas_map[carta]

            if jogo.carta_anterior:
                if jogo.carta_anterior['carta'] == carta:
                    # são a mesma carta
                    raise

                jogo.jogadas += 1

                # se as cartas forem um par
                if jogo.cartas_map[jogo.carta_anterior['carta']] == valor_carta:
                    # remove o par
                    del jogo.cartas_map[carta]
                    del jogo.cartas_map[jogo.carta_anterior['carta']]

                    # incrementa acertos
                    jogo.acertos += 1
                    status_code = self.PAR_CORRETO_STATUS_CODE

                    # atualiza valor_carta de jogo.cartas com o valor correto
                    for obj in jogo.cartas:
                        if obj['carta'] == jogo.carta_anterior['carta'] or \
                                obj['carta'] == carta:
                            obj['valor_carta'] = valor_carta

                    # se o jogo acabou, atualiza o ranking do jogador
                    if jogo.is_jogo_encerrado():
                        status_code = self.JOGO_ENCERRADO_STATUS_CODE

                        # https://qastack.com.br/programming/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom
                        with transaction.atomic():
                            ranking = Ranking.objects.filter(
                                usuario=self.request.user)

                            # se possui ranking cadastrado
                            if ranking.exists():
                                # se a pontuação foi melhor, então atualiza
                                if ranking.get().erros > jogo.jogadas:
                                    ranking.update(
                                        erros=jogo.jogadas - self.QTD_CARTAS)
                            else:
                                # se nao possui ranking cadastrado,
                                # entao cadastra
                                Ranking.objects.create(
                                    usuario=self.request.user,
                                    erros=jogo.jogadas - self.QTD_CARTAS,
                                )

                jogo.carta_anterior = None
            else:
                jogo.carta_anterior = {
                    'carta': carta, 'valor_carta': valor_carta}

            jogo.save()

            response = {
                'valor_carta': valor_carta,
            }
            return Response(response, status_code)
        except Exception as e:
            return Response(status=404)

    def delete(self, request: Request):
        """
        Apaga o jogo atual.
        """
        JogoDaMemoria.objects.filter(usuario=self.request.user).delete()
        return Response()


class RankingListAPIView(generics.ListAPIView):
    queryset = Ranking.objects.all().annotate(
        username=F('usuario__username'),
    ).order_by('erros').values('erros', 'username')[:10]
    serializer_class = RankingSerializer

    def list(self, request: Request, *args, **kwargs):
        """
        Retorna uma lista com o ranking.
        """
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data
        })
