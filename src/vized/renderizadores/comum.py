"""Leituras do passo que vários renderizadores especializados usam."""
from vized.deteccao.formas import NOMES
from vized.nucleo.heap import endereco


def texto(v):
    """Valor dentro de uma célula: None vira "·", o resto vira str (sem aspas)."""
    return "·" if v is None else str(v)


def variaveis_do_topo(passo):
    """Refs visíveis na linha atual: globais + locais do frame do topo.

    No nível do arquivo o topo é <module>, sem locais: valem as globais.
    """
    visiveis = dict(passo.globais)
    visiveis.update(passo.topo.locais)          # uma local esconde a global de mesmo nome
    return visiveis


def nomes_por_endereco(passo, so_topo=True):
    """Endereço → nomes das variáveis que apontam para ele."""
    if so_topo:
        grupos = [variaveis_do_topo(passo)]
    else:
        grupos = [passo.globais, *(q.locais for q in passo.quadros)]
    nomes = {}
    for grupo in grupos:
        for nome, r in grupo.items():
            if r[0] == "ref" and nome not in nomes.get(r[1], []):
                nomes.setdefault(r[1], []).append(nome)
    return nomes


def indices_do_topo(passo, n):
    """Índice → nomes das variáveis inteiras do topo que cabem em range(n).

    É o que desenha "▲ j" embaixo de um array: um int que é um índice válido.
    """
    indices = {}
    for nome, r in variaveis_do_topo(passo).items():
        v = r[1]
        if r[0] == "valor" and type(v) is int and 0 <= v < n:   # bool não conta
            indices.setdefault(v, []).append(nome)
    return indices


def valores_do_topo(passo):
    """Valores primitivos das variáveis do topo (ex.: o vértice `atual` de uma BFS)."""
    return {r[1] for r in variaveis_do_topo(passo).values()
            if r[0] == "valor" and r[1] is not None and type(r[1]) is not bool}


def titulo(cv, forma, ident=None, nomes=(), detalhe=""):
    """Linha 0: 'array @1a2b  ← numeros, v'."""
    pedacos = [(NOMES[forma], "titulo")]
    if detalhe:
        pedacos.append((f" · {detalhe}", "fraco"))
    if ident is not None:
        pedacos.append((f" {endereco(ident)}", "fraco"))
    if nomes:
        pedacos.append(("  ← " + ", ".join(nomes), "foco"))
    cv.trechos(0, 0, pedacos)
