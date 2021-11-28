from random import randint


class JogoDaMemoria:
    valores_cartas = [i for i in range(50)]

    def __init__(self, linhas):
        self.cartas = self._novas_cartas(linhas)
        self.jogadas = 0
        self.acertos = 0
        self.parsed_cartas = self.__parse_cartas()

    @staticmethod
    def novo_jogo(linhas):
        return JogoDaMemoria(linhas)

    def _novas_cartas(self, linhas):
        qtd_cartas = linhas + 1
        cartas = dict()
        for i in range(qtd_cartas):
            carta = self.valores_cartas[i]
            cartas[self._gera_aleatorio()] = carta
            cartas[self._gera_aleatorio()] = carta
        return cartas

    def faz_movimento(self, h1, h2):
        if self.jogo_encerrado():
            return None

        self.jogadas += 1

        carta1 = self.cartas.get(h1)
        carta2 = self.cartas.get(h2)

        if carta1 == carta2 and carta1 != None and carta2 != None:
            self.acertos += 1
            del self.cartas[h1]
            del self.cartas[h2]

        return carta1, carta2

    def __parse_cartas(self):
        cartas = []
        for x in self.cartas:
            cartas.append(x)
        cartas.sort()  # coloca em ordem crescente embaralhando tudo

        return cartas

    def _gera_aleatorio(self):
        return str(randint(0, 9999999999))

    def jogo_encerrado(self):
        return len(self.cartas) == 0


if __name__ == '__main__':
    from pprint import pprint

    game = JogoDaMemoria.novo_jogo(2)

    while True:
        print('jogadas: ', game.jogadas)
        print('acertos: ', game.acertos)
        pprint(game.cartas)
        print(game.parsed_cartas)

        entrada = input('insira dois numeros n1 n2: ')
        n1, n2 = entrada.split(' ')

        print(game.faz_movimento(n1, n2))
