"""Buckets de tabela hash: uma cadeia por índice.

    [0] ─▶ [ana] ─▶ [leo]
    [1] ─▶ ∅
"""


def buckets(cv, lin, col, cadeias, tag_indice, tag_item, texto=str):
    """tag_indice(k) → tag do "[k]"; tag_item(k, item) → tag de cada item."""
    for k, cadeia in enumerate(cadeias):
        x = cv.escrever(lin + k, col, f"[{k}]", tag_indice(k))
        x = cv.escrever(lin + k, x, " ─▶ " if cadeia else " ─▶ ∅", "fraco")
        for n, item in enumerate(cadeia):
            if n:
                x = cv.escrever(lin + k, x, " ─▶ ", "ponteiro")
            x = cv.escrever(lin + k, x, f"[{texto(item)}]", tag_item(k, item))
