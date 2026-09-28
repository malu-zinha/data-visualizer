"""Como o bubble sort é preparado, executado e desenhado."""
from vized.estruturas.array import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import locais_de
from vized.renderizadores.array import celulas


def desenhar_array(foto):
    """foto: valores, comparando (i, j) ou None, ordenados (set), troca, passada."""
    v, comp, ok = foto["valores"], foto["comparando"], foto["ordenados"]
    cv = Canvas()
    larg, col = 5, 2                                      # largura da célula, margem
    tags = ["destaque" if comp and i in comp else "ok" if i in ok else "normal"
            for i in range(len(v))]
    celulas(cv, 0, col, [str(x) for x in v], tags)
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
    p = p.vista                     # objetos reconstruídos a partir do heap
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
