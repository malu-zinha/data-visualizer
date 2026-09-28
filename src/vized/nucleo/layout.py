"""Funções de apoio aos desenhos: ler o passo e compor canvases.

Recebem a Vista do passo (objetos reconstruídos do heap); tipos são
indicados pelo NOME da classe, ex.: "NoAVL" (ver vista.do_tipo).
Os desenhos de cada forma (árvore, lista...) ficam em vized/renderizadores/.
"""
from vized.nucleo.canvas import Canvas
from vized.nucleo.vista import do_tipo


# ───────────────────────────── leitura do passo ────────────────────────────

def locais_de(passo, funcao):
    """Variáveis do frame mais recente com esse nome, ou {} se não estiver na pilha."""
    for q in reversed(passo.quadros):
        if q.funcao == funcao:
            return q.locais
    return {}


def nomes_no_topo(passo, tipo):
    """id(objeto) → nomes das variáveis do frame do topo que apontam para ele."""
    nomes = {}
    for nome, valor in passo.topo.locais.items():
        if do_tipo(valor, tipo):
            nomes.setdefault(id(valor), []).append(nome)
    return nomes


def legenda_variaveis(cv, lin, passo, tipo):
    """Escreve 'variáveis: y → 40  x → 30' com as referências do frame do topo."""
    pedacos = []
    for nome, v in passo.topo.locais.items():
        if do_tipo(v, tipo):
            pedacos += [(nome, "foco"), (f" → {getattr(v, 'valor', '?')}    ", "fraco")]
    if pedacos:
        cv.trechos(lin, 2, [("variáveis: ", "titulo")] + pedacos)


# ───────────────────────────── composição ──────────────────────────────────

def lado_a_lado(canvases, espaco=6):
    cv, col = Canvas(), 0
    for c in canvases:
        cv.colar(c, 0, col)               # cola cada desenho à direita do anterior
        col += c.largura + espaco
    return cv
