"""Busca em largura, com matriz e lista de adjacência sincronizadas."""
from vized.estruturas.grafo import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import locais_de
from vized.renderizadores.grafo import adjacencia, matriz


def desenhar(p):
    p = p.vista                     # objetos reconstruídos a partir do heap
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
    vs = g.vertices

    def tag_celula(i, j, bit):
        if bit and vs[i] == atual:
            return "foco" if vs[j] == viz else "destaque"   # vizinho sendo examinado
        return "normal" if bit else "fraco"

    matriz(cv, 2, 3, vs, g.matriz, lambda i: estado(vs[i]), tag_celula)
    lx = 28
    cv.escrever(0, lx, "lista de adjacência", "titulo")

    def tag_vizinho(v, u):
        marcado = v == atual and u == viz
        return "foco" if marcado else "destaque" if v == atual else "normal"

    adjacencia(cv, 2, lx, {v: g.adj[v] for v in vs}, estado, tag_vizinho)
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
