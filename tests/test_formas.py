"""Detecção de forma + desenhos especializados (etapa 4 do ROADMAP).

Snapshots do fluxo automático em tests/snapshots/automatico/. Para regravar
após mudança INTENCIONAL:
    VIZED_ATUALIZAR=1 pytest tests/test_formas.py
"""
import os
import re
from pathlib import Path

import pytest

from vized.cli import cenario_do_arquivo
from vized.deteccao.formas import detectar, tipos_de_no
from vized.estruturas import CENARIOS
from vized.renderizadores.automatico import Desenhista

RAIZ = Path(__file__).parent.parent
EXEMPLOS = sorted((RAIZ / "exemplos").glob("*.py"))
PASTA = Path(__file__).parent / "snapshots" / "automatico"
ATUALIZAR = os.environ.get("VIZED_ATUALIZAR") == "1"


def programa(tmp_path, codigo):
    arquivo = tmp_path / "programa.py"
    arquivo.write_text(codigo)
    return cenario_do_arquivo(str(arquivo))


def formas_no_fim(c):
    """Formas detectadas no último passo do programa."""
    return [e.forma for e in detectar(c.passos[-1], c.desenhar.tipos)]


NO = "class No:\n    def __init__(s, v):\n        s.v = v\n"


@pytest.mark.parametrize("codigo, esperado", [
    # nomes propositalmente estranhos: a detecção olha o grafo, não os nomes
    (NO + "        s.zz = None\n"
          "a = No(1)\na.zz = No(2)\na.zz.zz = No(3)\nfim = 1\n", ["lista"]),
    (NO + "        s.p = None\n        s.q = None\n"
          "a = No(1)\nb = No(2)\na.p = b\nb.q = a\nfim = 1\n", ["lista_dupla"]),
    (NO + "        s.e = None\n        s.d = None\n"
          "r = No(2)\nr.e = No(1)\nr.d = No(3)\nfim = 1\n", ["arvore"]),
    ("m = [[0, 1], [1, 0]]\nfim = 1\n", ["matriz_adjacencia"]),
    ("m = [[1, 2, 3], [4, 5, 6]]\nfim = 1\n", ["matriz"]),
    ("g = {'a': ['b'], 'b': ['a', 'c'], 'c': []}\nfim = 1\n", ["lista_adjacencia"]),
    ("b = [[], ['x', 'y'], ['z']]\nfim = 1\n", ["buckets"]),
    ("v = [3, 1, 2]\nfim = 1\n", ["array"]),
    ("from collections import deque\nq = deque([1, 2])\nfim = 1\n", ["fila"]),
])
def test_detecta_cada_forma(tmp_path, codigo, esperado):
    assert formas_no_fim(programa(tmp_path, codigo)) == esperado


def test_casos_sem_forma_ficam_no_generico(tmp_path):
    c = programa(tmp_path, (
        "class Aluna:\n    def __init__(s, n):\n        s.nome = n\n        s.notas = [9]\n"
        "turma = {'a': [Aluna('Ana')]}\n"        # dict de listas de OBJETOS: sem forma
        "fim = 1\n"))
    assert formas_no_fim(c) == []


def test_lista_dentro_de_objeto_nao_vira_array(tmp_path):
    c = programa(tmp_path, "class P:\n    def __init__(s):\n        s.itens = [1, 2]\n"
                           "p = P()\nfim = 1\n")
    assert formas_no_fim(c) == []               # já sai deitada no genérico


def test_tipo_de_no_vale_para_a_linha_do_tempo_inteira(tmp_path):
    # no 1º passo com nó, ele ainda não aponta para ninguém; mesmo assim é "arvore"
    c = programa(tmp_path, NO + "        s.e = None\n        s.d = None\n"
                           "r = No(2)\nr.e = No(1)\nr.d = No(3)\nfim = 1\n")
    primeiro = next(p for p in c.passos if "r" in p.globais)
    assert [e.forma for e in detectar(primeiro, c.desenhar.tipos)] == ["arvore"]


def test_cenarios_a_mao_sao_detectados():
    esperado = {
        "Array": {"array"}, "Lista encadeada": {"lista"}, "Árvore binária de busca": {"arvore"},
        "AVL": {"arvore"}, "Grafo e BFS": {"matriz_adjacencia", "lista_adjacencia"},
        "Tabela hash": {"buckets"},
    }
    for c in CENARIOS:
        tipos = tipos_de_no(c.passos)
        vistas = {e.forma for p in c.passos for e in detectar(p, tipos)}
        assert esperado.get(c.nome, set()) <= vistas, c.nome


def test_todos_os_passos_desenham_no_fluxo_automatico():
    for c in CENARIOS:
        d = Desenhista(lambda c=c: c.passos)
        for p in c.passos:
            d(p)
    for arquivo in EXEMPLOS:
        c = cenario_do_arquivo(str(arquivo))
        for p in c.passos:
            c.desenhar(p)


def test_gabarito_avl_mostra_a_rotacao():
    """O fluxo genérico mostra a árvore em pedaços no meio da rotação, como a aba AVL."""
    c = cenario_do_arquivo(str(RAIZ / "exemplos" / "avl.py"))
    textos = [c.desenhar(p).texto_puro() for p in c.passos
              if p.topo.funcao in ("rot_esq", "rot_dir")]
    assert any("árvore em 2 pedaços" in t for t in textos)
    final = c.desenhar(c.passos[-1]).texto_puro()
    assert "pedaços" not in final and "30(3)" in final    # rebalanceada, 30 no meio


def test_ciclo_na_lista_e_marcado(tmp_path):
    c = programa(tmp_path, NO + "        s.p = None\n"
                           "a = No(1)\na.p = No(2)\na.p.p = a\nfim = 1\n")
    assert "↺ " in c.desenhar(c.passos[-1]).texto_puro()


def test_indices_do_array(tmp_path):
    c = programa(tmp_path, "v = [5, 6, 7]\ni = 2\nfim = True\n")   # bool não é índice
    texto = c.desenhar(c.passos[-1]).texto_puro()
    assert re.search(r"▲\s*\n\s*i", texto)      # "▲" e embaixo dele o nome "i"


def normalizar(texto):
    return re.sub(r"@[0-9a-f]{4}", "@····", texto) + "\n"


@pytest.mark.parametrize("arquivo", EXEMPLOS, ids=lambda a: a.stem)
def test_snapshots(arquivo):
    c = cenario_do_arquivo(str(arquivo))
    n = len(c.passos)
    for k in sorted({0, n // 4, n // 2, 3 * n // 4, n - 1}):   # cinco pontos da linha do tempo
        atual = normalizar(c.desenhar(c.passos[k]).texto_puro())
        caminho = PASTA / f"{arquivo.stem}_{k:03d}.txt"
        if ATUALIZAR or not caminho.exists():
            PASTA.mkdir(parents=True, exist_ok=True)
            caminho.write_text(atual)
        assert atual == caminho.read_text(), f"desenho mudou: {caminho.name}"
