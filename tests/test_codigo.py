"""Os exemplos funcionam? (independe do visualizador)

Cada exemplo é um programa completo; aqui ele roda uma vez (runpy) e os
testes usam as funções e classes que ele define.
"""
import random
import runpy
from pathlib import Path

random.seed(0)                                  # testes reprodutíveis

EXEMPLOS = Path(__file__).parent.parent / "exemplos"


def carregar(nome):
    """Roda exemplos/<nome>.py e devolve o que ele definiu (funções, classes...)."""
    return runpy.run_path(str(EXEMPLOS / f"{nome}.py"))


bubble_sort = carregar("bubble")["bubble_sort"]
inserir_avl = carregar("avl")["inserir_avl"]
inserir_bst = carregar("bst")["inserir_bst"]
_grafo = carregar("grafo")
Grafo, bfs = _grafo["Grafo"], _grafo["bfs"]
TabelaHash = carregar("hash")["TabelaHash"]
ListaEncadeada = carregar("lista_encadeada")["ListaEncadeada"]
_pf = carregar("pilha_fila")
FilaCircular, Pilha = _pf["FilaCircular"], _pf["Pilha"]


def em_ordem(n):
    """Percurso em ordem: numa árvore de busca, sai ordenado."""
    return em_ordem(n.esq) + [n.valor] + em_ordem(n.dir) if n else []


def test_bubble_sort_ordena():
    for _ in range(50):
        v = [random.randint(-100, 100) for _ in range(random.randint(0, 30))]
        assert bubble_sort(list(v)) == sorted(v)


def test_lista_mantem_ordem_de_insercao():
    lista = ListaEncadeada()
    for x in (3, 7, 9, 12):
        lista.inserir_fim(x)
    valores, no = [], lista.head
    while no:                                   # percorre seguindo prox
        valores.append(no.valor)
        no = no.prox
    assert valores == [3, 7, 9, 12]


def test_pilha_e_lifo():
    p = Pilha()
    for x in (1, 2, 3):
        p.empilhar(x)
    assert [p.desempilhar() for _ in range(3)] == [3, 2, 1]


def test_fila_circular_e_fifo_e_da_a_volta():
    f = FilaCircular(3)
    saida = []
    for x in range(10):                         # bem mais que a capacidade
        f.enfileirar(x)
        if f.tamanho == 3:
            saida.append(f.desenfileirar())
    while f.tamanho:
        saida.append(f.desenfileirar())
    assert saida == list(range(10))


def test_bst_em_ordem_sai_ordenado():
    raiz, valores = None, random.sample(range(1000), 200)
    for v in valores:
        raiz = inserir_bst(raiz, v)
    assert em_ordem(raiz) == sorted(valores)


def test_avl_fica_balanceada_e_alturas_corretas():
    raiz, valores = None, random.sample(range(10_000), 500)
    for v in valores:
        raiz = inserir_avl(raiz, v)

    def verificar(n):
        """Devolve a altura real e confere o nó."""
        if n is None:
            return 0
        he, hd = verificar(n.esq), verificar(n.dir)
        assert abs(he - hd) <= 1                # invariante da AVL
        assert n.altura == 1 + max(he, hd)      # altura guardada = altura real
        return n.altura

    verificar(raiz)
    assert em_ordem(raiz) == sorted(valores)


def test_bfs_visita_por_camadas():
    g = Grafo("ABCDEF")
    for a, b in ("AB", "AC", "BD", "CD", "CE", "DF", "EF"):
        g.aresta(a, b)
    assert bfs(g, "A") == ["A", "B", "C", "D", "E", "F"]


def test_hash_coloca_cada_chave_no_bucket_de_h():
    t = TabelaHash(7)
    for k in ("ana", "bia", "caio", "iza"):
        t.inserir(k)
    for k in ("ana", "bia", "caio", "iza"):
        assert k in t.buckets[t.h(k)]
