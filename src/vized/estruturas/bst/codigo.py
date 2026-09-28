"""Árvore binária de busca."""


class NoArvore:
    def __init__(self, valor):
        self.valor = valor
        self.esq = None
        self.dir = None


def inserir_bst(raiz, valor):
    if raiz is None:           # achou a vaga
        return NoArvore(valor)
    if valor < raiz.valor:
        raiz.esq = inserir_bst(raiz.esq, valor)
    else:
        raiz.dir = inserir_bst(raiz.dir, valor)
    return raiz
