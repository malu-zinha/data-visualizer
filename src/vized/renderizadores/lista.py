"""Nós de lista encadeada: a caixa [valor | prox] com endereço e referências.

Os nomes dos campos são parâmetros (padrão: "valor" e "prox"); no fluxo
genérico eles vêm da detecção.
"""

SEM_ATRIBUTO = object()                   # marca "o atributo ainda não existe"
LARGURA_NO = 15                           # caixa (10) + seta (5): distância entre nós


def caixa_no(cv, lin, col, no, passo, nomes, tag, tag_seta, valor="valor", prox="prox"):
    """Desenha [valor | prox], o endereço, o prox e as variáveis que apontam para o nó."""
    borda = "novo" if tag == "novo" else "fraco"
    cv.escrever(lin, col, "┌────┬───┐", borda)
    cv.escrever(lin + 1, col, "│", borda)
    cv.escrever(lin + 1, col + 1, f"{str(getattr(no, valor, '?')):^4}", tag)
    cv.escrever(lin + 1, col + 5, "│", borda)
    seguinte = getattr(no, prox, SEM_ATRIBUTO)
    if seguinte is SEM_ATRIBUTO:          # __init__ ainda não criou o campo
        cv.escrever(lin + 1, col + 6, " ? │", "fraco")
        texto_prox = f"{prox} não existe"
    elif seguinte is None:
        cv.escrever(lin + 1, col + 6, " ∅ │", "fraco")
        texto_prox = f"{prox}=None"
    else:
        cv.escrever(lin + 1, col + 6, " ●─┼────▶", tag_seta)
        texto_prox = f"{prox}={passo.endereco(seguinte)}"
    cv.escrever(lin + 2, col, "└────┴───┘", borda)
    cv.escrever(lin + 3, col + 1, passo.endereco(no), "fraco")
    cv.escrever(lin + 4, col + 1, texto_prox, "fraco")
    if id(no) in nomes:
        cv.escrever(lin + 5, col + 1, "▲ " + ", ".join(nomes[id(no)]), "foco")
