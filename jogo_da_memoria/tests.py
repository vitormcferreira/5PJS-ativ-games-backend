from typing import OrderedDict
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.db.models.query import F

from accounts.models import Usuario
from .models import JogoDaMemoria, Ranking


class JogoAPIViewTest(APITestCase):
    URL = '/jogo_da_memoria/'

    def faz_todas_as_jogadas(self, erros=0):
        self.client.post(self.URL, {'carta': '10000'})
        self.client.post(self.URL, {'carta': '10001'})
        self.client.post(self.URL, {'carta': '20000'})
        self.client.post(self.URL, {'carta': '20001'})
        self.client.post(self.URL, {'carta': '30000'})
        self.client.post(self.URL, {'carta': '30001'})
        self.client.post(self.URL, {'carta': '40000'})
        self.client.post(self.URL, {'carta': '40001'})
        self.client.post(self.URL, {'carta': '50000'})
        self.client.post(self.URL, {'carta': '50001'})
        self.client.post(self.URL, {'carta': '60000'})
        self.client.post(self.URL, {'carta': '60001'})

        JogoDaMemoria.objects.filter(usuario=self.usuario).update(
            jogadas=F('jogadas') + erros)

    def reinicia_jogo_da_memoria(self):
        cartas_map = {
            '10000': 0,
            '10001': 0,
            '20000': 1,
            '20001': 1,
            '30000': 2,
            '30001': 2,
            '40000': 3,
            '40001': 3,
            '50000': 4,
            '50001': 4,
            '60000': 5,
            '60001': 5,
        }

        JogoDaMemoria.objects.update_or_create(
            usuario=self.usuario,
            defaults={
                'cartas_map': cartas_map,
                'jogadas': 0,
                'acertos': 0,
                'cartas': [
                    {'carta': '10000', 'valor_carta': None},
                    {'carta': '10001', 'valor_carta': None},
                    {'carta': '20000', 'valor_carta': None},
                    {'carta': '20001', 'valor_carta': None},
                    {'carta': '30000', 'valor_carta': None},
                    {'carta': '30001', 'valor_carta': None},
                    {'carta': '40000', 'valor_carta': None},
                    {'carta': '40001', 'valor_carta': None},
                    {'carta': '50000', 'valor_carta': None},
                    {'carta': '50001', 'valor_carta': None},
                    {'carta': '60000', 'valor_carta': None},
                    {'carta': '60001', 'valor_carta': None},
                ],
                'carta_anterior': None,
            }
        )

    def setUp(self):
        self.maxDiff = 10000
        # cria usuario
        usuario = Usuario.objects.create(
            username='test123', password='test123')
        self.usuario = usuario

        # cria jogo
        self.reinicia_jogo_da_memoria()

        # AUTENTICAÇÃO
        token = Token.objects.create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_GET_quando_existe_um_jogo_criado_deve_retornar_o_jogo(self):
        esperado = {
            'jogadas': 0,
            'acertos': 0,
            'cartas': [
                {'carta': '10000', 'valor_carta': None},
                {'carta': '10001', 'valor_carta': None},
                {'carta': '20000', 'valor_carta': None},
                {'carta': '20001', 'valor_carta': None},
                {'carta': '30000', 'valor_carta': None},
                {'carta': '30001', 'valor_carta': None},
                {'carta': '40000', 'valor_carta': None},
                {'carta': '40001', 'valor_carta': None},
                {'carta': '50000', 'valor_carta': None},
                {'carta': '50001', 'valor_carta': None},
                {'carta': '60000', 'valor_carta': None},
                {'carta': '60001', 'valor_carta': None},
            ],
            'carta_anterior': None,
        }
        response = self.client.get(self.URL)
        self.assertDictEqual(response.data, esperado)

    def test_GET_quando_NAO_existe_um_jogo_criado_deve_criar_um_jogo(self):
        # apaga a instancia de jogo criada
        JogoDaMemoria.objects.filter(usuario=self.usuario).delete()

        # testes
        response = self.client.get(self.URL)

        jogo = response.data
        self.assertIsInstance(jogo, dict)
        self.assertIn('jogadas', jogo)
        self.assertIn('acertos', jogo)
        self.assertIn('cartas', jogo)
        self.assertIn('carta_anterior', jogo)

        cartas = jogo['cartas']
        self.assertIsInstance(cartas, list)
        for obj in cartas:
            carta, valor_carta = obj.values()
            self.assertIsInstance(carta, str)
            self.assertIsNone(valor_carta)

    def test_POST_se_nao_enviar_carta_deve_retornar_erro_404(self):
        response = self.client.post(self.URL, {})
        self.assertEqual(response.status_code, 404)

    def test_POST_se_o_jogo_nao_existe_deve_retornar_erro_404(self):
        # apaga a instancia de jogo criada
        JogoDaMemoria.objects.filter(usuario=self.usuario).delete()

        entrada = {'carta': '10000'}

        response = self.client.post(
            self.URL, entrada)
        self.assertEqual(response.status_code, 404)

    def test_POST_se_a_carta_nao_existe_em_cartas_map_deve_retornar_erro_404(self):
        entrada = {'carta': '123'}

        response = self.client.post(self.URL, entrada)
        self.assertEqual(response.status_code, 404)

    def test_POST_enviar_primeira_carta_deve_salvar_como_carta_anterior(self):
        entradas = ({'carta': '10000'}, {'carta': '60001'})
        esperados = ({'carta': '10000', 'valor_carta': 0},
                     {'carta': '60001', 'valor_carta': 5})

        for entrada, esperado in zip(entradas, esperados):
            with self.subTest(carta=entrada):
                self.client.post(self.URL, entrada)

                jogo = JogoDaMemoria.objects.filter(
                    usuario=self.usuario)

                self.assertEqual(jogo.get().carta_anterior, esperado)

                jogo.update(carta_anterior=None)

    def test_POST_enviar_segunda_carta_deve_setar_carta_anterior_para_None(self):
        entrada = {'carta': '20000'}

        # envia primeira
        self.client.post(self.URL, entrada)

        entrada = {'carta': '30000'}

        # envia segunda
        self.client.post(self.URL, entrada)

        jogo: JogoDaMemoria = JogoDaMemoria.objects.get(usuario=self.usuario)

        self.assertIsNone(jogo.carta_anterior)

    def test_POST_enviar_carta_deve_retornar_json_com_valor_carta(self):
        entrada = {'carta': '10000'}
        esperado = {'valor_carta': 0}

        with self.subTest(msg='Primeira carta'):
            response = self.client.post(self.URL, entrada)
            self.assertDictEqual(response.data, esperado)

        entrada = {'carta': '20000'}
        esperado = {'valor_carta': 1}

        with self.subTest(msg='Segunda carta'):
            response = self.client.post(self.URL, entrada)
            self.assertDictEqual(response.data, esperado)

    def test_POST_enviar_a_mesma_carta_deve_retornar_erro_404(self):
        entrada = {'carta': '10000'}
        self.client.post(self.URL, entrada)
        response = self.client.post(self.URL, entrada)

        self.assertEqual(response.status_code, 404)

    def test_POST_se_as_cartas_forem_um_par_remover_elas_de_cartas_map_e_registrar_o_valor_carta_das_duas_em_cartas(self):
        entrada_1 = {'carta': '10000'}
        self.client.post(self.URL, entrada_1)

        entrada_2 = {'carta': '10001'}
        self.client.post(self.URL, entrada_2)

        jogo: JogoDaMemoria = JogoDaMemoria.objects.get(usuario=self.usuario)

        with self.subTest(msg='Remover cartas de cartas_map'):
            self.assertNotIn(entrada_1['carta'], jogo.cartas_map)
            self.assertNotIn(entrada_2['carta'], jogo.cartas_map)

        with self.subTest(msg='Registrar valor_carta em cartas'):
            for obj in jogo.cartas:
                if obj['carta'] == entrada_1['carta'] or obj['carta'] == entrada_2['carta']:
                    self.assertIsNotNone(obj['valor_carta'])

    def test_POST_jogadas_deve_ser_incrementado_depois_de_enviar_a_segunda_carta_diferente(self):
        entradas = (
            ({'carta': '10000'}, {'carta': '10001'}),
            ({'carta': '20000'}, {'carta': '40001'}),
        )

        for jogadas, entrada in enumerate(entradas, 1):
            self.client.post(self.URL, entrada[0])
            self.client.post(self.URL, entrada[1])

            jogo: JogoDaMemoria = JogoDaMemoria.objects.get(
                usuario=self.usuario)

            self.assertEqual(jogadas, jogo.jogadas)

    def test_POST_acertos_deve_ser_incrementado_depois_de_enviar_duas_cartas_corretas(self):
        entradas = (
            ({'carta': '10000'}, {'carta': '10001'}),
            ({'carta': '20000'}, {'carta': '20001'}),
            ({'carta': '30000'}, {'carta': '30001'}),
        )

        for acertos, entrada in enumerate(entradas, 1):
            self.client.post(self.URL, entrada[0])
            self.client.post(self.URL, entrada[1])

            jogo: JogoDaMemoria = JogoDaMemoria.objects.get(
                usuario=self.usuario)

            self.assertEqual(acertos, jogo.acertos)

    def test_POST_ranking_do_jogador_deve_ser_atualizado_apos_o_jogo_acabar(self):
        self.faz_todas_as_jogadas()
        existe_ranking = Ranking.objects.filter(usuario=self.usuario).exists()

        self.assertTrue(existe_ranking)

    def test_POST_ranking_do_jogador_deve_ser_atualizado_se_a_quantidade_de_erros_do_jogador_for_menor_que_a_ultima(self):
        self.faz_todas_as_jogadas(erros=5)
        self.reinicia_jogo_da_memoria()
        self.faz_todas_as_jogadas()

        ranking: Ranking = Ranking.objects.get(usuario=self.usuario)
        self.assertEqual(ranking.erros, 0)

    def test_POST_ranking_do_jogador_NAO_deve_ser_atualizado_se_a_quantidade_de_erros_do_jogador_for_MAIOR_que_a_ultima(self):
        self.faz_todas_as_jogadas()
        self.reinicia_jogo_da_memoria()
        self.faz_todas_as_jogadas(erros=5)

        ranking: Ranking = Ranking.objects.get(usuario=self.usuario)
        self.assertEqual(ranking.erros, 0)

    def test_POST_quando_for_enviado_um_par_incorreto_deve_retornar_o_status_200(self):
        entradas = (
            ({'carta': '20000'}, {'carta': '10001'}),
            ({'carta': '30000'}, {'carta': '20001'}),
            ({'carta': '40000'}, {'carta': '30001'}),
            ({'carta': '50000'}, {'carta': '40001'}),
            ({'carta': '60000'}, {'carta': '50001'}),
        )

        for entrada in entradas:
            self.client.post(self.URL, entrada[0])
            response = self.client.post(self.URL, entrada[1])

            self.assertEqual(response.status_code, 200)

    def test_POST_quando_for_enviado_um_par_correto_deve_retornar_o_status_240_quando_nao_for_a_ultima_carta(self):
        entradas = (
            ({'carta': '10000'}, {'carta': '10001'}),
            ({'carta': '20000'}, {'carta': '20001'}),
            ({'carta': '30000'}, {'carta': '30001'}),
            ({'carta': '40000'}, {'carta': '40001'}),
            ({'carta': '50000'}, {'carta': '50001'}),
        )

        for entrada in entradas:
            self.client.post(self.URL, entrada[0])
            response = self.client.post(self.URL, entrada[1])

            self.assertEqual(response.status_code, 240)

    def test_POST_quando_o_jogo_acabar_deve_retornar_o_status_250(self):
        self.client.post(self.URL, {'carta': '10000'})
        self.client.post(self.URL, {'carta': '10001'})
        self.client.post(self.URL, {'carta': '20000'})
        self.client.post(self.URL, {'carta': '20001'})
        self.client.post(self.URL, {'carta': '30000'})
        self.client.post(self.URL, {'carta': '30001'})
        self.client.post(self.URL, {'carta': '40000'})
        self.client.post(self.URL, {'carta': '40001'})
        self.client.post(self.URL, {'carta': '50000'})
        self.client.post(self.URL, {'carta': '50001'})
        self.client.post(self.URL, {'carta': '60000'})
        response = self.client.post(self.URL, {'carta': '60001'})
        self.assertEqual(response.status_code, 250)

    # [TALVEZ] testar se esta sendo retornado o valor_carta correto

    def test_DELETE_deletar_jogo(self):
        self.client.delete(self.URL)

        self.assertFalse(JogoDaMemoria.objects.filter(
            usuario=self.usuario).exists())


class RankingListAPIViewTest(APITestCase):
    URL = '/jogo_da_memoria/ranking/'

    def setUp(self):
        # ['user0', 'user1' ... 'user98', 'user99']
        usernames = [f'user{i}' for i in range(100)]
        # cria usuarios
        Usuario.objects.bulk_create(
            [*[Usuario(username=x, password=x) for x in usernames],
             Usuario(username='especial', password='especial')]
        )

        # o queryset retornado por bulk_create() não possui o atribute id,
        # necessário para o bulk_create() de Ranking
        usuarios = Usuario.objects.exclude(username='especial')

        especial = Usuario.objects.get(username='especial')

        # cria rankings
        Ranking.objects.bulk_create(
            [*[Ranking(usuario=x, erros=10) for x in usuarios],
             Ranking(
                usuario=especial,
                erros=9
            )]
        )

    def test_GET_deve_retornar_ranking_com_um_list_de_results_de_OrderedDict(self):
        response = self.client.get(self.URL)

        ranking = response.data

        self.assertIsInstance(ranking['results'], list)

        results = ranking.get('results')
        for r in results:
            self.assertIsInstance(r, OrderedDict)

    def test_GET_deve_retornar_results_com_10_objetos(self):
        response = self.client.get(self.URL)
        self.assertEqual(len(response.data['results']), 10)

    def test_GET_deve_retornar_results_com_os_valores_ordenados(self):
        response = self.client.get(self.URL)

        r1 = response.data['results']
        r2 = [*response.data['results']]
        r2.sort(key=lambda x: x['erros'])

        self.assertEquals(r1, r2)

    def test_GET_deve_retornar_results_com_as_keys_erros_e_username(self):
        esperados = ('erros', 'username')

        response = self.client.get(self.URL)

        ranking = response.data['results']

        for k1, k2 in ranking:
            self.assertCountEqual((k1, k2), esperados)
