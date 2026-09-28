"""Como o bubble sort é preparado, executado e desenhado."""
from vized.estruturas.array import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import locais_de


def desenhar_array(foto):
    """foto: valores, comparando (i, j) ou None, ordenados (set), troca, passada."""
    v, comp, ok = foto["valores"], foto["comparando"], foto["ordenados"]
    cv = Canvas()
    larg, col = 5, 2                                      # largura da célula, margem
    cv.escrever(0, col, "┌" + "┬".join("────" for _ in v) + "┐", "fraco")
    cv.escrever(2, col, "└" + "┴".join("────" for _ in v) + "┘", "fraco")
    for i, x in enumerate(v):
        tag = "destaque" if comp and i in comp else "ok" if i in ok else "normal"
        c = col + i * larg
        cv.escrever(1, c, "│", "fraco")                  # parede da célula
        cv.escrever(1, c + 1, f"{x:^4}", tag)            # valor centralizado
        cv.escrever(3, c + 1, f"{i:^4}", "fraco")        # índice embaixo
    cv.escrever(1, col + len(v) * larg, "│", "fraco")
    if comp:
        i, j = comp
        cv.escrever(4, col + i * larg + 2, "▲", "destaque")
        cv.escrever(4, col + j * larg + 2, "▲", "destaque")
        cv.escrever(5, col + i * larg + 2, "j", "destaque")
        cv.escrever(5, col + j * larg + 1, "j+1", "destaque")
        a, b = v[i], v[j]
        veredito = f"{a} > {b} → troca" if foto["troca"] else f"{a} ≤ {b} → mantém"
        cv.trechos(7, 2, [(f"bubble sort, passada {foto['passada']}: ", "titulo"),
                          (veredito, "destaque")])
    else:
        cv.escrever(7, 2, "bubble sort concluído", "ok")
    return cv


def desenhar(p):
    loc = locais_de(p, "bubble_sort")
    vals, n = loc["v"], len(loc["v"])
    if p.evento == "return" and p.topo.funcao == "bubble_sort":
        return desenhar_array({"valores": vals, "comparando": None, "ordenados": set(range(n))})
    passada, j = loc.get("passada"), loc.get("j")
    comp = (j, j + 1) if j is not None else None
    return desenhar_array({
        "valores": vals,
        "comparando": comp,
        "ordenados": set(range(n - passada, n)) if passada is not None else set(),  # sufixo fixo
        "troca": bool(comp) and vals[j] > vals[j + 1],
        "passada": (passada or 0) + 1,
    })


CENARIOS = [
    Cenario(
        nome="Array",
        operacao="bubble_sort(v)",
        preparar=lambda: {"v": [29, 10, 42, 14, 37, 13, 5]},
        executar=lambda e: codigo.bubble_sort(e["v"]),
        desenhar=desenhar,
    ),
]
