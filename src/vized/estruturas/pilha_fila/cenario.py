"""Pilha e fila circular lado a lado."""
from vized.estruturas.pilha_fila import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario


def desenhar(p):
    p = p.vista                     # objetos reconstruídos a partir do heap
    pilha, fila = p.estado["pilha"], p.estado["fila"]
    topo = p.topo.funcao
    cv = Canvas()
    # --- pilha (vertical, topo em cima) ---
    cv.escrever(0, 1, "Pilha", "titulo")
    x = 8
    itens = list(reversed(pilha.itens))
    cv.escrever(1, x, "┌──────┐", "fraco")
    lin = 2
    for k, item in enumerate(itens):
        ativo = k == 0 and topo in ("empilhar", "desempilhar")
        cv.escrever(lin, x, "│", "fraco")
        cv.escrever(lin, x + 1, f"{item:^6}", "destaque" if ativo else "normal")
        cv.escrever(lin, x + 7, "│", "fraco")
        if k == 0:
            cv.escrever(lin, 0, "topo →", "ponteiro")
        lin += 1
        if k < len(itens) - 1:
            cv.escrever(lin, x, "├──────┤", "fraco")
            lin += 1
    cv.escrever(lin, x, "└──────┘", "fraco")
    if topo in ("empilhar", "desempilhar") and "x" in p.topo.locais:
        cv.trechos(lin + 1, 1, [("x", "foco"), (f" = {p.topo.locais['x']}", "fraco")])
    # --- fila circular (vetor com índices) ---
    fx, larg = 24, 6
    cap = len(fila.dados)
    cv.escrever(0, fx, f"Fila circular (capacidade {cap})", "titulo")
    validos = {(fila.inicio + k) % cap for k in range(fila.tamanho)}   # posições ocupadas
    mexendo = {"enfileirar": fila.fim, "desenfileirar": fila.inicio}.get(topo)
    cv.escrever(3, fx, "┌" + "┬".join("─────" for _ in range(cap)) + "┐", "fraco")
    cv.escrever(5, fx, "└" + "┴".join("─────" for _ in range(cap)) + "┘", "fraco")
    for i, dado in enumerate(fila.dados):
        c = fx + i * larg
        cv.escrever(2, c + 3, str(i), "fraco")
        cv.escrever(4, c, "│", "fraco")
        if i == mexendo:
            tag = "destaque"
        elif i in validos:
            tag = "novo" if dado in ("E", "F") else "normal"
        else:
            tag = "fraco"                         # sobra antiga, fora da fila
        cv.escrever(4, c + 1, f"{'·' if dado is None else dado:^5}", tag)
    cv.escrever(4, fx + cap * larg, "│", "fraco")
    for nome, idx, linha in (("ini", fila.inicio, 6), ("fim", fila.fim, 7)):
        cv.escrever(linha, fx + idx * larg + 3, "▲", "ponteiro")
        cv.escrever(linha, fx + idx * larg + 5, nome, "ponteiro")
    cv.escrever(9, fx, f"tamanho = {fila.tamanho}", "normal")
    cv.escrever(10, fx, "cinza = sobra antiga, fora da fila", "fraco")
    if p.evento == "return" and topo in ("desempilhar", "desenfileirar"):
        cv.trechos(13, 1, [(f"{topo}() retorna ", "titulo"), (repr(p.retorno), "ok")])
    return cv


def preparar():
    pilha = codigo.Pilha()
    for x in (4, 8, 15, 16):
        pilha.empilhar(x)
    fila = codigo.FilaCircular(5)
    for x in "ABCD":
        fila.enfileirar(x)
    fila.desenfileirar()
    fila.desenfileirar()                  # frente em 2: A e B viram "sobra"
    return {"pilha": pilha, "fila": fila}


CENARIOS = [
    Cenario(
        nome="Pilha e fila",
        operacao="roteiro_pilha_fila(pilha, fila)",
        preparar=preparar,
        executar=lambda e: codigo.roteiro_pilha_fila(e["pilha"], e["fila"]),
        desenhar=desenhar,
    ),
]
