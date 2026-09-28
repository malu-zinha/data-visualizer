"""Array: células lado a lado com o índice embaixo.

    ┌────┬────┬────┐
    │ 5  │ 2  │ 9  │
    └────┴────┴────┘
      0    1    2
"""


def celulas(cv, lin, col, textos, tags, largura=4):
    """Desenha as células a partir de (lin, col); ocupa 4 linhas (a última = índices).

    Devolve a coluna do centro de cada célula (para marcar ▲ embaixo).
    """
    cv.escrever(lin, col, "┌" + "┬".join("─" * largura for _ in textos) + "┐", "fraco")
    cv.escrever(lin + 2, col, "└" + "┴".join("─" * largura for _ in textos) + "┘", "fraco")
    centros = []
    for i, (texto, tag) in enumerate(zip(textos, tags)):
        c = col + i * (largura + 1)
        cv.escrever(lin + 1, c, "│", "fraco")                 # parede da célula
        cv.escrever(lin + 1, c + 1, f"{texto:^{largura}}", tag)   # valor centralizado
        cv.escrever(lin + 3, c + 1, f"{i:^{largura}}", "fraco")   # índice embaixo
        centros.append(c + 1 + largura // 2)
    cv.escrever(lin + 1, col + len(textos) * (largura + 1), "│", "fraco")
    return centros
