"""Estruturas de dados mínimas + os exemplos usados nas visualizações.

Nada aqui sabe que existe terminal. Os quatro visualizadores (ANSI, rich,
textual, curses) importam este módulo e só decidem COMO desenhar.
"""
import copy                      # deepcopy para tirar "fotos" do estado
from collections import deque    # fila eficiente (popleft em O(1))


# ─────────────────────────── Array + bubble sort ───────────────────────────

def bubble_passos(valores):
    """Gera um snapshot a cada comparação do bubble sort."""
    v = list(valores)                                   # cópia: não altera a entrada
    n = len(v)                                          # tamanho do array
    for passada in range(n - 1):                        # cada passada "afunda" o maior
        for j in range(n - 1 - passada):                # compara vizinhos até a parte ordenada
            troca = v[j] > v[j + 1]                     # decide ANTES de trocar
            yield {                                     # foto do momento da comparação
                "valores": list(v),                     # estado atual do array
                "comparando": (j, j + 1),               # os dois índices em jogo
                "ordenados": set(range(n - passada, n)),# sufixo que já está no lugar
                "troca": troca,                         # vai trocar?
                "passada": passada + 1,                 # passada humana (começa em 1)
            }
            if troca:                                   # efetivamente troca
                v[j], v[j + 1] = v[j + 1], v[j]
    yield {"valores": v, "comparando": None,            # foto final: tudo ordenado
           "ordenados": set(range(n)), "troca": False, "passada": n - 1}


ARRAY_INICIAL = [29, 10, 42, 14, 37, 13, 5]            # entrada do exemplo


def exemplo_array():
    """Snapshot no meio da 2ª passada, comparando as posições 3 e 4."""
    for foto in bubble_passos(ARRAY_INICIAL):           # percorre a linha do tempo
        if foto["passada"] == 2 and foto["comparando"] == (3, 4):
            return foto                                 # devolve o instante escolhido


# ───────────────────────────── Lista encadeada ─────────────────────────────

class No:
    """Nó de lista encadeada: um valor e uma REFERÊNCIA para o próximo."""
    def __init__(self, valor, prox=None):
        self.valor = valor           # dado guardado
        self.prox = prox             # referência (endereço) do próximo nó, ou None


class ListaEncadeada:
    def __init__(self):
        self.head = None             # lista vazia: head não aponta para nada

    def inserir_fim(self, valor):
        novo = No(valor)             # cria o nó no heap
        if self.head is None:        # caso lista vazia
            self.head = novo         # head passa a apontar para ele
            return novo
        atual = self.head            # começa do início...
        while atual.prox:            # ...e anda até o último nó
            atual = atual.prox
        atual.prox = novo            # religa a referência do antigo último
        return novo

    def nos(self):
        atual = self.head            # itera seguindo as referências
        while atual:
            yield atual
            atual = atual.prox


def exemplo_lista():
    lista = ListaEncadeada()
    for v in (3, 7, 9):              # monta a lista 3 → 7 → 9
        lista.inserir_fim(v)
    novo = lista.inserir_fim(12)     # operação que queremos destacar
    return {"lista": lista, "novo": novo, "operacao": "inserir_fim(12)"}


# ────────────────────────────── Pilha e fila ───────────────────────────────

def exemplo_pilha_fila():
    pilha = [4, 8, 15, 16]           # topo = fim da lista Python
    pilha.append(23)                 # push(23): a operação destacada
    fila = deque(["A", "B", "C", "D"])
    saiu = fila.popleft()            # dequeue() remove pela frente
    fila.append("E")                 # enqueue("E") entra por trás
    return {"pilha": pilha, "fila": fila, "saiu": saiu, "entrou": "E"}


# ─────────────────────────── Árvore binária (BST) ──────────────────────────

class NoArvore:
    def __init__(self, valor):
        self.valor = valor           # chave do nó
        self.esq = None              # subárvore esquerda (menores)
        self.dir = None              # subárvore direita (maiores)
        self.altura = 1              # usada só pela AVL


def inserir_bst(raiz, valor, caminho):
    """Inserção recursiva; `caminho` registra os nós visitados."""
    if raiz is None:                              # achou o lugar vazio
        return NoArvore(valor)
    caminho.append(raiz)                          # registra a visita (evento!)
    if valor < raiz.valor:                        # menor → desce à esquerda
        raiz.esq = inserir_bst(raiz.esq, valor, caminho)
    else:                                         # maior/igual → desce à direita
        raiz.dir = inserir_bst(raiz.dir, valor, caminho)
    return raiz


def buscar(raiz, valor):
    while raiz and raiz.valor != valor:           # busca iterativa simples
        raiz = raiz.esq if valor < raiz.valor else raiz.dir
    return raiz


def exemplo_bst():
    raiz = None
    for v in (8, 3, 10, 1, 6, 14, 4, 7):          # árvore clássica de livro
        raiz = inserir_bst(raiz, v, [])
    caminho = []                                  # agora gravamos o caminho
    raiz = inserir_bst(raiz, 13, caminho)         # inserir(13) é a operação exibida
    return {"raiz": raiz, "caminho": caminho, "novo": buscar(raiz, 13), "valor": 13}


# ────────────────────────────────── AVL ────────────────────────────────────

def altura(n):
    return n.altura if n else 0                   # altura de None é 0


def fator(n):
    return altura(n.esq) - altura(n.dir)          # fator de balanceamento


def atualizar(n):
    n.altura = 1 + max(altura(n.esq), altura(n.dir))


def rot_dir(y):
    x = y.esq                                     # x sobe
    y.esq = x.dir                                 # filho direito de x muda de pai
    x.dir = y                                     # y desce para a direita de x
    atualizar(y); atualizar(x)                    # y primeiro: agora é filho
    return x                                      # nova raiz da subárvore


def rot_esq(x):
    y = x.dir                                     # espelho da rotação à direita
    x.dir = y.esq
    y.esq = x
    atualizar(x); atualizar(y)
    return y


def inserir_avl(n, valor, log, balancear=True):
    if n is None:
        return NoArvore(valor)
    if valor < n.valor:
        n.esq = inserir_avl(n.esq, valor, log, balancear)
    else:
        n.dir = inserir_avl(n.dir, valor, log, balancear)
    atualizar(n)                                  # altura na volta da recursão
    if not balancear:                             # modo "foto antes da rotação"
        return n
    b = fator(n)
    if b > 1 and valor < n.esq.valor:             # caso LL
        log.append(f"LL em {n.valor}: rotação simples à direita")
        return rot_dir(n)
    if b < -1 and valor >= n.dir.valor:           # caso RR
        log.append(f"RR em {n.valor}: rotação simples à esquerda")
        return rot_esq(n)
    if b > 1:                                     # caso LR
        log.append(f"LR em {n.valor}: esquerda em {n.esq.valor}, direita em {n.valor}")
        n.esq = rot_esq(n.esq)
        return rot_dir(n)
    if b < -1:                                    # caso RL
        log.append(f"RL em {n.valor}: direita em {n.dir.valor}, esquerda em {n.valor}")
        n.dir = rot_dir(n.dir)
        return rot_esq(n)
    return n


def exemplo_avl():
    raiz = None
    for v in (10, 20, 30, 40, 50):                # já provoca 2 rotações RR
        raiz = inserir_avl(raiz, v, [])
    antes = copy.deepcopy(raiz)                   # foto antes da operação
    antes = inserir_avl(antes, 25, [], balancear=False)  # 25 inserido SEM rebalancear
    log = []
    raiz = inserir_avl(raiz, 25, log)             # inserção real, com rotação
    return {"antes": antes, "depois": raiz, "log": log, "valor": 25}


# ───────────────────────────────── Grafo ───────────────────────────────────

class Grafo:
    """Grafo não direcionado guardado nas DUAS representações ao mesmo tempo."""
    def __init__(self, vertices):
        self.vertices = list(vertices)                          # ordem fixa
        self.idx = {v: i for i, v in enumerate(self.vertices)}  # vértice → linha/coluna
        n = len(self.vertices)
        self.matriz = [[0] * n for _ in range(n)]               # matriz n×n zerada
        self.adj = {v: [] for v in self.vertices}               # lista de adjacência

    def aresta(self, a, b):
        i, j = self.idx[a], self.idx[b]
        self.matriz[i][j] = self.matriz[j][i] = 1               # simétrica
        self.adj[a].append(b)                                   # nas duas listas
        self.adj[b].append(a)


def bfs_passos(g, origem):
    """BFS emitindo um snapshot a cada vértice retirado da fila."""
    descobertos = {origem}           # já entraram na fila alguma vez
    fila = deque([origem])
    ordem = []                       # ordem de processamento
    while fila:
        atual = fila.popleft()       # retira da frente
        ordem.append(atual)
        for viz in g.adj[atual]:     # examina os vizinhos
            if viz not in descobertos:
                descobertos.add(viz)
                fila.append(viz)     # entra no fim da fila
        yield {"atual": atual, "descobertos": set(descobertos),
               "fila": list(fila), "ordem": list(ordem)}


def exemplo_grafo():
    g = Grafo("ABCDEF")
    for a, b in ("AB", "AC", "BD", "CD", "CE", "DF", "EF"):
        g.aresta(a, b)
    passos = list(bfs_passos(g, "A"))
    return {"grafo": g, "estado": passos[2], "origem": "A"}   # 3º passo: processando C


# ─────────────────────────────── Tabela hash ───────────────────────────────

def h(chave, m):
    """Hash didático e DETERMINÍSTICO (o hash() de str muda a cada execução)."""
    return sum(ord(c) for c in chave) % m


def exemplo_hash():
    m = 7                                                # número de buckets (primo)
    buckets = [[] for _ in range(m)]                     # encadeamento separado
    for chave in ("ana", "bia", "caio", "duda", "enzo", "leo", "iza"):
        buckets[h(chave, m)].append(chave)               # colisão → fim da cadeia
    ultima = "iza"                                       # inserção destacada
    codigos = [ord(c) for c in ultima]
    return {"buckets": buckets, "m": m, "ultima": ultima,
            "codigos": codigos, "indice": h(ultima, m)}
