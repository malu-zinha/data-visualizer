"""Registro das estruturas: a ordem desta lista é a ordem das abas.

Para adicionar uma estrutura nova:
  1. crie estruturas/<nome>/codigo.py   (o código que será mostrado)
  2. crie estruturas/<nome>/cenario.py  (com uma lista CENARIOS)
  3. acrescente uma linha aqui
"""
from vized.estruturas.array.cenario import CENARIOS as ARRAY
from vized.estruturas.avl.cenario import CENARIOS as AVL
from vized.estruturas.bst.cenario import CENARIOS as BST
from vized.estruturas.grafo.cenario import CENARIOS as GRAFO
from vized.estruturas.hash.cenario import CENARIOS as HASH
from vized.estruturas.lista_encadeada.cenario import CENARIOS as LISTA
from vized.estruturas.pilha_fila.cenario import CENARIOS as PILHA_FILA

CENARIOS = [*ARRAY, *LISTA, *PILHA_FILA, *BST, *AVL, *GRAFO, *HASH]
