from game import JogoDaMemoria
from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import exceptions


class JogoAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        jogo: JogoDaMemoria = self.request.session.get('jogo')

        if not jogo or jogo.jogo_encerrado():
            jogo = JogoDaMemoria.novo_jogo(3)

        self.request.session['jogo'] = jogo

        return Response({
            'jogo': jogo.parse_cartas()
        })

    def post(self, request: Request):
        jogo: JogoDaMemoria = self.request.session.get('jogo')

        if not jogo:
            raise exceptions.JogoInexistenteError()

        carta1 = request.data.get('carta1')
        carta2 = request.data.get('carta2')

        if not carta1 or not carta2:
            raise exceptions.CartaEmFaltaError()

        valor_carta = jogo.faz_movimento(carta1, carta2)

        self.request.session['jogo'] = jogo

        dict_response = {
            'carta1': carta1,
            'carta2': carta2,
            'jogadas': str(jogo.jogadas),
            'acertos': str(jogo.acertos),
            'valor_carta': valor_carta,
        }

        if jogo.jogo_encerrado():
            return Response(dict_response, status=250)

        if valor_carta:
            return Response(dict_response)
        else:
            raise exceptions.MovimentoIncorretoError(dict_response)
