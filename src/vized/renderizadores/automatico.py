"""Fluxo genérico completo: detecta as formas e escolhe o desenho de cada uma.

    passo → detectar formas → [árvore] [lista] [array] ...   (em cima)
                            → genérico com o resto            (embaixo)

O que um renderizador especializado desenha some do genérico; nas caixas
de variáveis, a referência vira um rótulo ("nó 30 @2c60", "array @1a2b")
em vez de seta. Casos ambíguos simplesmente não são detectados e ficam
no genérico.
"""
from vized.deteccao.formas import detectar, tipos_de_no
from vized.nucleo.canvas import Canvas
from vized.nucleo.heap import endereco
from vized.renderizadores import arvore, array, buckets, generico, grafo, lista, sequencia

RENDERIZADORES = {
    "arvore": arvore.desenhar_estrutura,
    "lista": lista.desenhar_estrutura,
    "lista_dupla": lista.desenhar_estrutura,
    "array": array.desenhar_estrutura,
    "fila": sequencia.desenhar_estrutura,
    "matriz": grafo.desenhar_matriz,
    "matriz_adjacencia": grafo.desenhar_matriz,
    "lista_adjacencia": grafo.desenhar_adjacencia,
    "buckets": buckets.desenhar_estrutura,
}

# como um container aparece numa caixa de variável do genérico
CURTOS = {"array": "array", "fila": "fila", "matriz": "matriz", "matriz_adjacencia": "matriz",
          "lista_adjacencia": "adjacência", "buckets": "buckets"}


def _rotulos(passo, est):
    """Endereço → texto curto, para quem aponta para dentro da estrutura."""
    heap, rotulos = passo.heap, {}
    for ident in est.objetos:
        e = heap[ident]
        if est.no is not None:                          # nó: mostra o valor
            r = e["campos"].get(est.no.valor) if est.no.valor else None
            valor = r[1] if r and r[0] == "valor" else "?"
            rotulos[ident] = f"nó {valor} {endereco(ident)}"
        elif ident == est.raiz:
            rotulos[ident] = f"{CURTOS[est.forma]} {endereco(ident)}"
        else:                                           # linha de matriz, bucket...
            rotulos[ident] = f"{e['tipo']} {endereco(ident)}"
    return rotulos


def desenhar(passo, tipos):
    """Passo → Canvas: estruturas especializadas em cima, genérico embaixo."""
    estruturas = detectar(passo, tipos)
    if not estruturas:
        return generico.desenhar(passo)
    cv, lin = Canvas(), 0
    ocultos, rotulos = set(), {}
    for est in estruturas:
        parte = RENDERIZADORES[est.forma](passo, est)
        cv.colar(parte, lin, 0)
        lin += parte.altura + 1
        ocultos.update(est.objetos)
        rotulos.update(_rotulos(passo, est))
    cv.colar(generico.desenhar(passo, frozenset(ocultos), rotulos), lin, 0)
    return cv


class Desenhista:
    """desenhar(passo) para um Cenario, com os tipos de nó da linha do tempo inteira.

    Os tipos são calculados uma vez, na primeira chamada, olhando TODOS os
    passos (por isso recebe uma função que devolve os passos, não os passos).
    """

    def __init__(self, obter_passos):
        self._obter_passos = obter_passos
        self._tipos = None

    @property
    def tipos(self):
        if self._tipos is None:
            self._tipos = tipos_de_no(self._obter_passos())
        return self._tipos

    def __call__(self, passo):
        return desenhar(passo, self.tipos)
