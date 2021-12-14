from django.db import models
from random import randint, shuffle
from accounts.models import Usuario


class Ranking(models.Model):
    usuario = models.OneToOneField(to=Usuario, on_delete=models.CASCADE)
    erros = models.IntegerField()


class JogoDaMemoria(models.Model):
    usuario = models.OneToOneField(
        to=Usuario, on_delete=models.CASCADE, unique=True)
    # todas as cartas e seus pares
    cartas_map = models.JSONField()
    # { carta: string, valor_carta: int }
    cartas = models.JSONField()
    jogadas = models.IntegerField()
    acertos = models.IntegerField()
    carta_anterior = models.JSONField(null=True)

    @classmethod
    def novo_jogo(cls, usuario, qtd_pares=6):
        cartas_map = cls._novas_cartas(qtd_pares)

        instance = cls.objects.create(
            usuario=usuario,
            cartas_map=cartas_map,
            jogadas=0,
            acertos=0,
            cartas=cls._parse_cartas(cartas_map),
            carta_anterior=None
        )

        return instance

    @classmethod
    def _novas_cartas(cls, qtd_pares):
        cartas = dict()
        for i in range(qtd_pares):
            # chaves como string porque se colocar int, quando salvar como
            # json ele converte para string gerando problemas
            cartas[cls._gera_aleatorio()] = i
            cartas[cls._gera_aleatorio()] = i
        return cartas

    @staticmethod
    def _gera_aleatorio():
        return str(randint(0, 9999999999))

    def is_jogo_encerrado(self):
        return len(self.cartas_map) == 0

    @staticmethod
    def _parse_cartas(cards):
        cartas = []
        for x in cards:
            cartas.append({
                'carta': x,
                'valor_carta': None,
            })
        shuffle(cartas)

        return cartas
