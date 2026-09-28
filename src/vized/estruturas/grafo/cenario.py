"""Busca em largura, com matriz e lista de adjacência sincronizadas."""
from vized.estruturas.grafo import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import locais_de


def desenhar(p):
    loc = locais_de(p, "bfs")
    g = loc["g"]
    atual, viz = loc.get("atual"), loc.get("viz")
    fila = list(loc.get("fila", []))
    ordem = loc.get("ordem", [])

    def estado(v):
        if v == atual:
            return "destaque"                      # sendo processado
        if v in ordem:
            return "ok"                            # já processado
        return "fronteira" if v in fila else "normal"

    cv = Canvas()
    cv.escrever(0, 2, "matriz de adjacência", "titulo")
    for j, v in enumerate(g.vertices):
        cv.escrever(2, 6 + j * 3, v, estado(v))   # cabeçalho das colunas
    for i, v in enumerate(g.vertices):
        cv.escrever(3 + i, 3, v, estado(v))       # rótulo da linha
        for j, u in enumerate(g.vertices):
            bit = g.matriz[i][j]
            if bit and v == atual:
                tag = "foco" if u == viz else "destaque"   # vizinho sendo examinado
            else:
                tag = "normal" if bit else "fraco"
            cv.escrever(3 + i, 6 + j * 3, "1" if bit else "·", tag)
    lx = 28
    cv.escrever(0, lx, "lista de adjacência", "titulo")
    for i, v in enumerate(g.vertices):
        pedacos = [(v, estado(v)), (" →", "fraco")]
        for u in g.adj[v]:
            marcado = v == atual and u == viz
            pedacos += [(" ", "normal"),
                        (f"[{u}]", "foco" if marcado else "destaque" if v == atual else "normal")]
        cv.trechos(2 + i, lx, pedacos)
    by = 4 + len(g.vertices)
    cv.trechos(by, 2, [("atual ", "fraco"), (str(atual or "-"), "destaque"),
                       ("   viz ", "fraco"), (str(viz or "-"), "foco"),
                       ("   fila ", "fraco"), ("[" + ", ".join(fila) + "]", "fronteira"),
                       ("   ordem ", "fraco"), (" ".join(ordem) or "-", "ok")])
    cv.trechos(by + 2, 2, [("■ atual  ", "destaque"), ("■ processado  ", "ok"),
                           ("■ na fila  ", "fronteira"), ("■ não descoberto", "normal")])
    return cv


def preparar():
    g = codigo.Grafo("ABCDEF")
    for a, b in ("AB", "AC", "BD", "CD", "CE", "DF", "EF"):
        g.aresta(a, b)
    return {"g": g}


CENARIOS = [
    Cenario(
        nome="Grafo e BFS",
        operacao='bfs(g, "A")',
        preparar=preparar,
        executar=lambda e: codigo.bfs(e["g"], "A"),
        desenhar=desenhar,
    ),
]
