"""Inserção na árvore binária de busca."""
from vized.estruturas.bst import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import lado_a_lado, legenda_variaveis, nomes_no_topo
from vized.renderizadores.arvore import desenhar_arvore, floresta

VALOR_NOVO = 13


def desenhar(p):
    p = p.vista                     # objetos reconstruídos a partir do heap
    raizes, _ = floresta(p, [p.estado["raiz"]], "NoArvore")
    # a pilha de recursão É o caminho percorrido na árvore
    caminho = {id(q.locais["raiz"]) for q in p.quadros
               if q.funcao == "inserir_bst" and q.locais.get("raiz") is not None}
    nomes = nomes_no_topo(p, "NoArvore")

    def tag(n):
        if id(n) in nomes:
            return "foco"
        if getattr(n, "valor", VALOR_NOVO) == VALOR_NOVO:
            return "novo"
        return "destaque" if id(n) in caminho else "normal"

    def aresta(a, b):
        return "destaque" if id(a) in caminho and tag(b) != "normal" else "fraco"

    def rotulo(n):
        return [(f"({getattr(n, 'valor', '?')})", tag(n))]

    cv = Canvas()
    cv.colar(lado_a_lado([desenhar_arvore(r, rotulo, aresta) for r in raizes]), 0, 2)
    base = cv.altura + 1
    legenda_variaveis(cv, base, p, "NoArvore")
    cv.trechos(base + 1, 2, [("amarelo", "destaque"),
                             (" = nós com inserir_bst aberto na pilha", "fraco")])
    if len(raizes) > 1:
        cv.escrever(base + 2, 2, "o nó novo existe, mas nenhum pai o aponta", "fraco")
    return cv


def preparar():
    raiz = None
    for x in (8, 3, 10, 1, 6, 14, 4, 7):
        raiz = codigo.inserir_bst(raiz, x)
    return {"raiz": raiz}


CENARIOS = [
    Cenario(
        nome="Árvore binária de busca",
        operacao=f"inserir_bst(raiz, {VALOR_NOVO})",
        preparar=preparar,
        executar=lambda e: codigo.inserir_bst(e["raiz"], VALOR_NOVO),
        desenhar=desenhar,
    ),
]
