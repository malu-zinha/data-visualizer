"""Buckets de tabela hash: uma cadeia por índice.

    [0] ─▶ [ana] ─▶ [leo]
    [1] ─▶ ∅
"""
from vized.nucleo.canvas import Canvas
from vized.renderizadores.comum import indices_do_topo, nomes_por_endereco, texto, titulo



def buckets(cv, lin, col, cadeias, tag_indice, tag_item, texto=str):
    """tag_indice(k) → tag do "[k]"; tag_item(k, item) → tag de cada item."""
    for k, cadeia in enumerate(cadeias):
        x = cv.escrever(lin + k, col, f"[{k}]", tag_indice(k))
        x = cv.escrever(lin + k, x, " ─▶ " if cadeia else " ─▶ ∅", "fraco")
        for n, item in enumerate(cadeia):
            if n:
                x = cv.escrever(lin + k, x, " ─▶ ", "ponteiro")
            x = cv.escrever(lin + k, x, f"[{texto(item)}]", tag_item(k, item))


# ───────────────────────────── fluxo genérico ──────────────────────────────

def desenhar_estrutura(passo, est):
    """Lista de listas de tamanhos variados: uma cadeia por índice."""
    heap = passo.heap
    cadeias = [[r[1] for r in heap[r[1]]["itens"]] for r in heap[est.raiz]["itens"]]
    marcados = indices_do_topo(passo, len(cadeias))
    cv = Canvas()
    titulo(cv, "buckets", est.raiz, nomes_por_endereco(passo, so_topo=False).get(est.raiz, []))
    buckets(cv, 2, 2, cadeias, lambda k: "destaque" if k in marcados else "fraco",
            lambda k, item: "normal", texto)
    for k in marcados:                               # ▶ no bucket que um int do topo indica
        cv.escrever(2 + k, 0, "▶", "destaque")
    return cv
