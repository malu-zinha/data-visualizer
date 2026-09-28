"""Inserção no fim de uma lista encadeada."""
from vized.estruturas.lista_encadeada import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import nomes_no_topo
from vized.nucleo.vista import do_tipo
from vized.renderizadores.lista import caixa_no

VALOR_NOVO = 12


def desenhar(p):
    p = p.vista                     # objetos reconstruídos a partir do heap
    lista = p.estado["lista"]
    cadeia, no = [], lista.head
    while no is not None:                 # segue as referências a partir de head
        cadeia.append(no)
        no = getattr(no, "prox", None)
    na_cadeia = {id(n) for n in cadeia}
    soltos = []                           # nós que existem mas a lista não alcança
    for q in p.quadros:
        for v in q.locais.values():
            if do_tipo(v, "No") and id(v) not in na_cadeia \
                    and all(v is not s for s in soltos):
                soltos.append(v)
    nomes = nomes_no_topo(p, "No")

    def tag(n):
        novo = getattr(n, "valor", VALOR_NOVO) == VALOR_NOVO     # sem valor = em construção
        return "novo" if novo else "normal"

    cv = Canvas()
    cv.escrever(0, 1, "head", "ponteiro")
    cv.escrever(1, 2, "│", "ponteiro")
    cv.escrever(2, 2, "▼", "ponteiro")
    for k, n in enumerate(cadeia):
        prox = getattr(n, "prox", None)
        seta = "novo" if prox is not None and tag(prox) == "novo" else "ponteiro"
        caixa_no(cv, 3, k * 15, n, p, nomes, tag(n), seta)
    if soltos:
        cv.escrever(10, 0, "solto no heap (a lista não o alcança):", "fraco")
        for k, n in enumerate(soltos):
            caixa_no(cv, 11, k * 15, n, p, nomes, tag(n), "ponteiro")
    return cv


def preparar():
    lista = codigo.ListaEncadeada()
    for x in (3, 7, 9):
        lista.inserir_fim(x)
    return {"lista": lista}


CENARIOS = [
    Cenario(
        nome="Lista encadeada",
        operacao=f"lista.inserir_fim({VALOR_NOVO})",
        preparar=preparar,
        executar=lambda e: e["lista"].inserir_fim(VALOR_NOVO),
        desenhar=desenhar,
    ),
]
