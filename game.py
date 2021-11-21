from random import randint


class JogoDaMemoria:
    valores = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    def __init__(self, linhas):
        self.cartas = self.novas_cartas(linhas)
        self.jogadas = 0
        self.acertos = 0
        self.objetivo = linhas + 1  # quantidade de acertos final

    @staticmethod
    def novo_jogo(linhas):
        return JogoDaMemoria(linhas)

    def novas_cartas(self, linhas):
        '''
        linhas = 2
        colunas = linhas + 1 = 3
        qtd_cartas = ((linhas * colunas) / linhas) = colunas = 3
        cartas={
            (hash1,hash2):a,
            (hash1,hash2):b,
            (hash1,hash2):c,
        }
        '''
        qtd_cartas = linhas + 1
        cartas = {
            # TODO: fazer com que nunca ocorra chaves iguais
            (self.gera_aleatorio(), self.gera_aleatorio()): carta
            for carta in self.valores[:qtd_cartas]
        }
        return cartas

    def faz_movimento(self, h1, h2):
        self.jogadas += 1
        carta = None
        try:
            # deixei carta em variavel para ser possivel usar depois
            carta = self.cartas.pop((h1, h2))
            self.acertos += 1
        except:
            return False

        if self.acertos == self.objetivo:
            raise Exception('Fim de jogo')

        return True

    def parse_cartas(self):
        cartas = []
        for x, y in self.cartas:
            cartas.extend([x, y])
        cartas.sort()  # coloca em ordem crescente embaralhando tudo
        return cartas

    def gera_aleatorio(self):
        return str(randint(0, 9999999999))

    def jogo_encerrado(self):
        return self.acertos == self.objetivo


if __name__ == '__main__':
    from pprint import pprint

    game = JogoDaMemoria.novo_jogo(2)

    while True:
        print('jogadas: ', game.jogadas)
        print('acertos: ', game.acertos)
        pprint(game.cartas)

        entrada = input('insira dois numeros n1 n2: ')
        n1, n2 = entrada.split(' ')

        print(game.faz_movimento(n1, n2))
