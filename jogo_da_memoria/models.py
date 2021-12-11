from django.db import models
from random import randint, shuffle
from accounts.models import Usuario


class Ranking(models.Model):
    usuario = models.ForeignKey(to=Usuario, on_delete=models.CASCADE)
    jogadas = models.IntegerField()
    erros = models.IntegerField()


class JogoDaMemoria(models.Model):
    usuario = models.OneToOneField(
        to=Usuario, on_delete=models.CASCADE, unique=True)
    cartas = models.JSONField()
    # par (valor_carta, numero, encontrado)
    parsed_cartas = models.JSONField()
    jogadas = models.IntegerField()
    acertos = models.IntegerField()

    @classmethod
    def novo_jogo(cls, usuario, qtd_pares=6):
        cartas = cls._novas_cartas(qtd_pares)

        instance = cls.objects.create(
            usuario=usuario,
            cartas=cartas,
            jogadas=0,
            acertos=0,
            parsed_cartas=cls.__parse_cartas(cartas),
        )

        return instance

    def faz_movimento(self, h1, h2):
        """
        Recebe h1 e h2, que são os numeros das cartas.

        Se for um par correto, seta os valores do par em self.parsed_cartas, 
        apaga o par de self.cartas, marca o par como encontrado, incrementa 
        self.acertos e salva as alterações na base de dados.

        Caso for um par errado, seta os valores do par em self.parsed_cartas e 
        retorna.
        """
        self.jogadas += 1
        self.save()

        carta1 = self.cartas.get(h1)
        carta2 = self.cartas.get(h2)

        pos_carta1 = None
        pos_carta2 = None

        for carta in self.parsed_cartas:
            if carta[0] == h1:
                carta[1] = carta1
                pos_carta1 = carta
            elif carta[0] == h2:
                carta[1] = carta2
                pos_carta2 = carta

        if carta1 == carta2 and carta1 != None and carta2 != None and h1 != h2:
            self.acertos += 1

            pos_carta1[2] = True
            pos_carta2[2] = True

            del self.cartas[h1]
            del self.cartas[h2]

            self.save()

        return carta1, carta2

    @classmethod
    def _novas_cartas(cls, qtd_pares):
        cartas = dict()
        for i in range(qtd_pares):
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
            parsed_cartas.append((x, None, False))
        shuffle(parsed_cartas)

        return parsed_cartas
