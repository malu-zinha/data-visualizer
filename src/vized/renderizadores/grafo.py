"""Grafo: matriz de adjacência (ou qualquer matriz) e lista de adjacência.

         A  B  C             A → [B] [C]
      A  ·  1  1             B → [A]
      B  1  ·  ·             C → [A]
      C  1  ·  ·
"""


def matriz(cv, lin, col, rotulos, linhas, tag_rotulo, tag_celula, texto=None, espaco=3):
    """Cabeçalho na linha `lin`, uma linha por vértice abaixo dele.

    tag_rotulo(i)          → tag do rótulo da linha/coluna i
    tag_celula(i, j, v)    → tag da célula
    texto(v)               → texto da célula (padrão: 0/1 vira "·"/"1")
    """
    texto = texto or (lambda v: "1" if v else "·")
    for j, r in enumerate(rotulos):
        cv.escrever(lin, col + 3 + j * espaco, str(r), tag_rotulo(j))   # colunas
    for i, r in enumerate(rotulos):
        cv.escrever(lin + 1 + i, col, str(r), tag_rotulo(i))           # rótulo da linha
        for j, v in enumerate(linhas[i]):
            cv.escrever(lin + 1 + i, col + 3 + j * espaco, texto(v), tag_celula(i, j, v))


def adjacencia(cv, lin, col, adj, tag_vertice, tag_vizinho):
    """Uma linha por vértice: 'A → [B] [C]'."""
    for i, (v, vizinhos) in enumerate(adj.items()):
        pedacos = [(str(v), tag_vertice(v)), (" →", "fraco")]
        for u in vizinhos:
            pedacos += [(" ", "normal"), (f"[{u}]", tag_vizinho(v, u))]
        cv.trechos(lin + i, col, pedacos)
