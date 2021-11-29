from django.db import models
from random import randint
from accounts.models import Usuario


class Ranking(models.Model):
    usuario = models.ForeignKey(to=Usuario, on_delete=models.CASCADE)
    jogadas = models.IntegerField()
    erros = models.IntegerField()


class JogoDaMemoria(models.Model):
    usuario = models.OneToOneField(
        to=Usuario, on_delete=models.CASCADE, unique=True)
    cartas = models.JSONField()
    parsed_cartas = models.JSONField()
    jogadas = models.IntegerField()
    acertos = models.IntegerField()

    @classmethod
    def novo_jogo(cls, usuario, linhas=3):
        cartas = cls._novas_cartas(linhas)

        instance = cls.objects.create(
            usuario=usuario,
            cartas=cartas,
            jogadas=0,
            acertos=0,
            parsed_cartas=cls.__parse_cartas(cartas),
        )

        return instance

    def faz_movimento(self, h1, h2):
        self.jogadas += 1

        carta1 = self.cartas.get(h1)
        carta2 = self.cartas.get(h2)

        if carta1 == carta2 and carta1 != None and carta2 != None:
            self.acertos += 1
            del self.cartas[h1]
            del self.cartas[h2]

        self.save()
        return carta1, carta2

    @classmethod
    def _novas_cartas(cls, linhas):
        qtd_cartas = linhas + 1
        cartas = dict()
        for i in range(qtd_cartas):
            cartas[cls._gera_aleatorio()] = i
            cartas[cls._gera_aleatorio()] = i
        return cartas

    @staticmethod
    def _gera_aleatorio():
        return str(randint(0, 9999999999))

    def jogo_encerrado(self):
        return len(self.cartas) == 0

    @staticmethod
    def __parse_cartas(cartas):
        parsed_cartas = []
        for x in cartas:
            parsed_cartas.append(x)
        parsed_cartas.sort()  # coloca em ordem crescente embaralhando tudo

        return parsed_cartas
