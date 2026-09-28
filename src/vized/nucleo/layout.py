"""Funções de desenho reaproveitadas por várias estruturas.

Recebem a Vista do passo (objetos reconstruídos do heap); tipos são
indicados pelo NOME da classe, ex.: "NoAVL" (ver vista.do_tipo).
"""
from vized.nucleo.canvas import Canvas
from vized.nucleo.vista import do_tipo


# ───────────────────────────── leitura do passo ────────────────────────────

def locais_de(passo, funcao):
    """Variáveis do frame mais recente com esse nome, ou {} se não estiver na pilha."""
    for q in reversed(passo.quadros):
        if q.funcao == funcao:
            return q.locais
    return {}


def nomes_no_topo(passo, tipo):
    """id(objeto) → nomes das variáveis do frame do topo que apontam para ele."""
    nomes = {}
    for nome, valor in passo.topo.locais.items():
        if do_tipo(valor, tipo):
            nomes.setdefault(id(valor), []).append(nome)
    return nomes


def legenda_variaveis(cv, lin, passo, tipo):
    """Escreve 'variáveis: y → 40  x → 30' com as referências do frame do topo."""
    pedacos = []
    for nome, v in passo.topo.locais.items():
        if do_tipo(v, tipo):
            pedacos += [(nome, "foco"), (f" → {getattr(v, 'valor', '?')}    ", "fraco")]
    if pedacos:
        cv.trechos(lin, 2, [("variáveis: ", "titulo")] + pedacos)


# ───────────────────────────── composição ──────────────────────────────────

def lado_a_lado(canvases, espaco=6):
    cv, col = Canvas(), 0
    for c in canvases:
        cv.colar(c, 0, col)               # cola cada desenho à direita do anterior
        col += c.largura + espaco
    return cv


# ───────────────────────────── árvores binárias ────────────────────────────

def _esq(n):
    return getattr(n, "esq", None)        # tolera nó ainda no __init__


def _dir(n):
    return getattr(n, "dir", None)


def desenhar_arvore(raiz, rotulo, tag_aresta):
    """Layout por percurso em ordem: a ordem in-order vira a COLUNA do nó.

    rotulo(n)          → lista de (texto, tag) para escrever o nó
    tag_aresta(pai, f) → tag da linha que liga pai ao filho f
    """
    posicao = {}                          # nó → (profundidade, ordem in-order)
    contador = [0]

    def visitar(n, prof):
        if n is None:
            return
        visitar(_esq(n), prof + 1)        # esquerda primeiro...
        posicao[n] = (prof, contador[0])  # ...depois o nó ganha a próxima coluna
        contador[0] += 1
        visitar(_dir(n), prof + 1)

    visitar(raiz, 0)
    slot = max(sum(len(t) for t, _ in rotulo(n)) for n in posicao) + 1
    centro = {n: o * slot + slot // 2 for n, (_, o) in posicao.items()}
    cv = Canvas()
    for n, (prof, _) in posicao.items():
        y, x = prof * 2, centro[n]        # nós nas linhas pares
        pedacos = rotulo(n)
        largura = sum(len(t) for t, _ in pedacos)
        cv.trechos(y, x - largura // 2, pedacos)
        if not (_esq(n) or _dir(n)):
            continue
        if _esq(n):                       # linha de conexão abaixo: ┌───┴───┐
            cv.escrever(y + 1, centro[_esq(n)], "┌" + "─" * (x - centro[_esq(n)] - 1),
                        tag_aresta(n, _esq(n)))
        if _dir(n):
            cv.escrever(y + 1, x + 1, "─" * (centro[_dir(n)] - x - 1) + "┐",
                        tag_aresta(n, _dir(n)))
        juncao = "┴" if _esq(n) and _dir(n) else "┘" if _esq(n) else "└"
        cv.escrever(y + 1, x, juncao, "fraco")
    return cv


def floresta(passo, raizes_conhecidas, tipo):
    """Todas as árvores visíveis: da raiz do cenário E das variáveis locais.

    Durante uma rotação (ou logo após criar um nó), um pedaço pode ficar
    sem pai; ele vira uma árvore separada no desenho.
    Devolve (raízes, nós com mais de um pai).
    """
    candidatos = [r for r in raizes_conhecidas if r is not None]
    for q in passo.quadros:
        candidatos += [v for v in q.locais.values() if do_tipo(v, tipo)]
    if do_tipo(passo.retorno, tipo):
        candidatos.append(passo.retorno)
    nos, pilha = {}, list(candidatos)
    while pilha:                          # coleta tudo que é alcançável
        n = pilha.pop()
        if n is None or id(n) in nos:
            continue
        nos[id(n)] = n
        pilha += [_esq(n), _dir(n)]
    pais = {}                             # id(filho) → quantos nós apontam para ele
    for n in nos.values():
        for f in (_esq(n), _dir(n)):
            if f is not None:
                pais[id(f)] = pais.get(id(f), 0) + 1
    raizes = [n for n in nos.values() if id(n) not in pais]   # ninguém aponta para elas
    raizes.sort(key=lambda n: (not hasattr(n, "valor"), getattr(n, "valor", 0)))
    compartilhados = [n for n in nos.values() if pais.get(id(n), 0) > 1]
    return raizes, compartilhados
