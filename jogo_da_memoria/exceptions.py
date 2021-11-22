from rest_framework.exceptions import APIException


class JogoInexistenteError(APIException):
    status_code = 450
    default_detail = 'jogo inexistente'


class CartaEmFaltaError(APIException):
    status_code = 451
    default_detail = 'carta em falta'


class MovimentoIncorretoError(APIException):
    status_code = 452
    default_detail = 'movimento incorreto'
