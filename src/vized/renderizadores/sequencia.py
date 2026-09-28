"""Vetor com índices em cima e marcadores embaixo (fila circular, deque).

      0     1     2
    ┌─────┬─────┬─────┐
    │  A  │  B  │  ·  │
    └─────┴─────┴─────┘
       ▲ ini       ▲ fim
"""


def vetor(cv, lin, col, textos, tags, largura=5):
    """Índices na linha `lin`, células nas 3 linhas seguintes."""
    passo = largura + 1                                    # distância entre paredes
    cv.escrever(lin + 1, col, "┌" + "┬".join("─" * largura for _ in textos) + "┐", "fraco")
    cv.escrever(lin + 3, col, "└" + "┴".join("─" * largura for _ in textos) + "┘", "fraco")
    for i, (texto, tag) in enumerate(zip(textos, tags)):
        c = col + i * passo
        cv.escrever(lin, c + 1 + largura // 2, str(i), "fraco")   # índice em cima
        cv.escrever(lin + 2, c, "│", "fraco")
        cv.escrever(lin + 2, c + 1, f"{texto:^{largura}}", tag)
    cv.escrever(lin + 2, col + len(textos) * passo, "│", "fraco")


def marcar(cv, lin, col, indice, nome, largura=5, tag="ponteiro"):
    """"▲ nome" embaixo da célula `indice` de um vetor desenhado em `col`."""
    x = col + indice * (largura + 1) + 1 + largura // 2
    cv.escrever(lin, x, "▲", tag)
    cv.escrever(lin, x + 2, nome, tag)
