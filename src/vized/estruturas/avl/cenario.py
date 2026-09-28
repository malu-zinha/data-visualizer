"""Inserção na AVL, com a rotação acontecendo linha a linha."""
from vized.estruturas.avl import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import desenhar_arvore, floresta, lado_a_lado, legenda_variaveis, nomes_no_topo

VALOR_NOVO = 25


def fb_guardado(n):
    """Fator de balanceamento com as alturas GUARDADAS nos nós (o que o código vê)."""
    def alt(f):
        return getattr(f, "altura", 0) if f else 0
    return alt(getattr(n, "esq", None)) - alt(getattr(n, "dir", None))


def desenhar(p):
    raizes, compartilhados = floresta(p, [p.estado["raiz"]], codigo.NoAVL)
    nomes = nomes_no_topo(p, codigo.NoAVL)

    def rotulo(n):
        if not hasattr(n, "altura"):                     # ainda no __init__
            return [(str(getattr(n, "valor", "?")), "novo")]
        b = fb_guardado(n)
        if id(n) in nomes:
            tag = "foco"
        elif abs(b) > 1:
            tag = "alerta"
        else:
            tag = "novo" if n.valor == VALOR_NOVO else "normal"
        return [(str(n.valor), tag),
                (f"({b:+d})" if b else "(0)", "alerta" if abs(b) > 1 else "fraco")]

    cv = Canvas()
    arvores = [desenhar_arvore(r, rotulo, lambda a, b: "fraco") for r in raizes]
    cv.colar(lado_a_lado(arvores), 0, 2)
    base = cv.altura + 1
    legenda_variaveis(cv, base, p, codigo.NoAVL)
    cv.escrever(base + 1, 2, "entre parênteses: fator de balanceamento", "fraco")
    if len(raizes) > 1:
        cv.escrever(base + 2, 2, "rotação em andamento: árvore em pedaços", "fraco")
        for k, n in enumerate(compartilhados):
            cv.escrever(base + 3 + k, 2, f"o nó {n.valor} tem DOIS pais agora", "alerta")
    return cv


def preparar():
    raiz = None
    for x in (10, 20, 30, 40, 50):        # já provoca duas rotações RR
        raiz = codigo.inserir_avl(raiz, x)
    return {"raiz": raiz}


CENARIOS = [
    Cenario(
        nome="AVL",
        operacao=f"inserir_avl(raiz, {VALOR_NOVO})",
        preparar=preparar,
        executar=lambda e: codigo.inserir_avl(e["raiz"], VALOR_NOVO),
        desenhar=desenhar,
        pular=("altura", "fator"),        # "step over" nas funções triviais
    ),
]
