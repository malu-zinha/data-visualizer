"""Inserção numa tabela hash, com o cálculo de h() visível."""
from vized.estruturas.hash import codigo
from vized.nucleo.canvas import Canvas
from vized.nucleo.cenario import Cenario
from vized.nucleo.layout import locais_de

CHAVE_NOVA = "iza"


def desenhar(p):
    p = p.vista                     # objetos reconstruídos a partir do heap
    t = p.estado["tabela"]
    i = locais_de(p, "inserir").get("i")
    hloc = locais_de(p, "h")                    # {} se h() não está na pilha
    cv = Canvas()
    for k, cadeia in enumerate(t.buckets):
        col = cv.escrever(k, 2, f"[{k}]", "destaque" if k == i else "fraco")
        col = cv.escrever(k, col, " ─▶ " if cadeia else " ─▶ ∅", "fraco")
        for n, chave in enumerate(cadeia):
            if n:
                col = cv.escrever(k, col, " ─▶ ", "ponteiro")
            col = cv.escrever(k, col, f"[{chave}]", "novo" if chave == CHAVE_NOVA else "normal")
    base = t.m + 1
    if hloc:                                    # dentro de h(): a soma crescendo
        pedacos = [(f"h('{CHAVE_NOVA}'):  ", "titulo")]
        for ch in hloc["chave"]:
            pedacos.append((f" {ch} ", "foco" if ch == hloc.get("c") else "normal"))
        pedacos.append((f"   soma = {hloc.get('soma', '?')}", "destaque"))
        if p.evento == "return" and p.topo.funcao == "h":
            pedacos.append((f"   {hloc['soma']} % {t.m} = {p.retorno}", "novo"))
        cv.trechos(base, 2, pedacos)
    elif i is not None:
        cv.trechos(base, 2, [(f"h('{CHAVE_NOVA}') = ", "titulo"), (str(i), "destaque")])
    return cv


def preparar():
    t = codigo.TabelaHash(7)
    for k in ("ana", "bia", "caio", "duda", "enzo", "leo"):
        t.inserir(k)
    return {"tabela": t}


CENARIOS = [
    Cenario(
        nome="Tabela hash",
        operacao=f't.inserir("{CHAVE_NOVA}")',
        preparar=preparar,
        executar=lambda e: e["tabela"].inserir(CHAVE_NOVA),
        desenhar=desenhar,
    ),
]
