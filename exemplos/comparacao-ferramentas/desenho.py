"""Transforma estruturas em uma grade de caracteres com TAGS semânticas.

A ideia central: o desenho diz "este trecho é 'novo'", "este é 'destaque'".
Cada ferramenta (ANSI, rich, textual, curses) só traduz tag → cor.
Assim o layout (a parte difícil) é escrito uma vez só.
"""
import estruturas as ed

# Tags usadas (o significado é o que importa; a cor fica com cada backend)
TAGS = {
    "normal":    "texto comum",
    "titulo":    "legendas e rótulos",
    "destaque":  "em foco agora (comparando, caminho, atual)",
    "novo":      "acabou de ser criado ou religado",
    "ok":        "concluído (ordenado, visitado)",
    "fronteira": "esperando (na fila da BFS)",
    "ponteiro":  "referências: head, topo, setas",
    "fraco":     "detalhes: índices, endereços, linhas",
    "alerta":    "desbalanceado / problema",
}


class Canvas:
    """Grade 2D de (caractere, tag) que cresce conforme se escreve."""

    def __init__(self):
        self.celulas = {}                         # (linha, coluna) → (char, tag)

    def escrever(self, lin, col, texto, tag="normal"):
        for i, ch in enumerate(texto):            # um caractere por célula
            self.celulas[(lin, col + i)] = (ch, tag)
        return col + len(texto)                   # devolve a coluna seguinte

    def trechos(self, lin, col, pedacos):
        for texto, tag in pedacos:                # escreve vários (texto, tag) em sequência
            col = self.escrever(lin, col, texto, tag)
        return col

    def colar(self, outro, lin, col):
        for (l, c), cel in outro.celulas.items(): # copia outro canvas com deslocamento
            self.celulas[(lin + l, col + c)] = cel

    @property
    def altura(self):
        return 1 + max((l for l, _ in self.celulas), default=-1)

    @property
    def largura(self):
        return 1 + max((c for _, c in self.celulas), default=-1)

    def linhas(self):
        """Lista de linhas; cada linha é uma lista de segmentos (texto, tag)."""
        saida = []
        for l in range(self.altura):
            segs, atual_txt, atual_tag = [], "", None
            ultima = max((c for ll, c in self.celulas if ll == l), default=-1)
            for c in range(ultima + 1):
                ch, tag = self.celulas.get((l, c), (" ", "normal"))  # buraco = espaço
                if tag != atual_tag and atual_txt:     # tag mudou: fecha o segmento
                    segs.append((atual_txt, atual_tag))
                    atual_txt = ""
                atual_txt += ch
                atual_tag = tag
            if atual_txt:
                segs.append((atual_txt, atual_tag))
            saida.append(segs)
        return saida

    def texto_puro(self):
        return "\n".join("".join(t for t, _ in segs) for segs in self.linhas())


def curto(obj):
    """Últimos 4 dígitos hex do id(): o 'endereço' do objeto no CPython."""
    return f"@{id(obj) & 0xFFFF:04x}"


# ───────────────────────────────── Array ───────────────────────────────────

def desenhar_array(foto=None):
    foto = foto or ed.exemplo_array()
    v, comp, ok = foto["valores"], foto["comparando"], foto["ordenados"]
    cv = Canvas()
    larg = 5                                              # largura de cada célula
    col = 2
    cv.escrever(0, col, "┌" + "┬".join("────" for _ in v) + "┐", "fraco")
    cv.escrever(2, col, "└" + "┴".join("────" for _ in v) + "┘", "fraco")
    for i, x in enumerate(v):
        tag = "destaque" if comp and i in comp else "ok" if i in ok else "normal"
        c = col + i * larg
        cv.escrever(1, c, "│", "fraco")                  # parede da célula
        cv.escrever(1, c + 1, f"{x:^4}", tag)            # valor centralizado
        cv.escrever(3, c + 1, f"{i:^4}", "fraco")        # índice embaixo
    cv.escrever(1, col + len(v) * larg, "│", "fraco")
    if comp:
        i, j = comp
        cv.escrever(4, col + i * larg + 2, "▲", "destaque")
        cv.escrever(4, col + j * larg + 2, "▲", "destaque")
        cv.escrever(5, col + i * larg + 2, "j", "destaque")
        cv.escrever(5, col + j * larg + 1, "j+1", "destaque")
        a, b = v[i], v[j]
        veredito = f"{a} > {b} → troca" if foto["troca"] else f"{a} ≤ {b} → mantém"
        cv.trechos(7, 2, [(f"bubble sort, passada {foto['passada']}: ", "titulo"),
                          (veredito, "destaque")])
    else:
        cv.escrever(7, 2, "bubble sort concluído", "ok")
    return cv


# ─────────────────────────── Lista encadeada ───────────────────────────────

def desenhar_lista():
    ex = ed.exemplo_lista()
    nos, novo = list(ex["lista"].nos()), ex["novo"]
    cv = Canvas()
    passo = 15                                           # colunas por nó (caixa + seta)
    cv.escrever(0, 1, "head", "ponteiro")
    cv.escrever(1, 2, "│", "ponteiro")
    cv.escrever(2, 2, "▼", "ponteiro")
    for k, no in enumerate(nos):
        c = k * passo
        tag = "novo" if no is novo else "normal"
        borda = "novo" if no is novo else "fraco"
        cv.escrever(3, c, "┌────┬───┐", borda)
        cv.escrever(4, c, "│", borda)
        cv.escrever(4, c + 1, f"{no.valor:^4}", tag)     # campo valor
        cv.escrever(4, c + 5, "│", borda)
        cv.escrever(5, c, "└────┴───┘", borda)
        cv.escrever(6, c + 1, curto(no), "fraco")        # endereço do nó
        if no.prox:
            # a seta que mudou nesta operação é a que aponta para o nó novo
            seta = "novo" if no.prox is novo else "ponteiro"
            cv.escrever(4, c + 6, " ●─", seta)
            cv.escrever(4, c + 9, "┼────▶", seta)
            cv.escrever(7, c + 1, f"prox={curto(no.prox)}", "fraco")
        else:
            cv.escrever(4, c + 6, " ∅ │", "fraco")       # prox = None
            cv.escrever(7, c + 1, "prox=None", "fraco")
    cv.trechos(9, 0, [("operação: ", "titulo"), (ex["operacao"], "novo"),
                      ("  (só a referência prox do nó 9 mudou)", "fraco")])
    return cv


# ───────────────────────────── Pilha e fila ────────────────────────────────

def desenhar_pilha_fila():
    ex = ed.exemplo_pilha_fila()
    cv = Canvas()
    # --- pilha, na vertical, topo em cima ---
    cv.escrever(0, 2, "Pilha (LIFO)", "titulo")
    x = 9
    cv.escrever(1, x, "┌──────┐", "fraco")
    lin = 2
    for k, item in enumerate(reversed(ex["pilha"])):      # desenha do topo para a base
        tag = "novo" if k == 0 else "normal"
        cv.escrever(lin, x, "│", "fraco")
        cv.escrever(lin, x + 1, f"{item:^6}", tag)
        cv.escrever(lin, x + 7, "│", "fraco")
        if k == 0:
            cv.escrever(lin, 1, "topo →", "ponteiro")
            cv.escrever(lin, x + 9, "← push(23)", "novo")
        lin += 1
        if k < len(ex["pilha"]) - 1:
            cv.escrever(lin, x, "├──────┤", "fraco")
            lin += 1
    cv.escrever(lin, x, "└──────┘", "fraco")
    # --- fila, na horizontal, frente à esquerda ---
    fx = 34
    cv.escrever(0, fx, "Fila (FIFO)", "titulo")
    cv.trechos(2, fx, [("dequeue() → ", "fraco"), (ex["saiu"], "ok")])
    itens = list(ex["fila"])
    cv.escrever(4, fx + 9, "┌" + "┬".join("───" for _ in itens) + "┐", "fraco")
    cv.escrever(5, fx, "frente →", "ponteiro")
    for k, item in enumerate(itens):
        c = fx + 9 + k * 4
        cv.escrever(5, c, "│", "fraco")
        cv.escrever(5, c + 1, f" {item} ", "novo" if item == ex["entrou"] else "normal")
    fim = fx + 9 + len(itens) * 4
    cv.escrever(5, fim, "│", "fraco")
    cv.escrever(5, fim + 2, "← trás", "ponteiro")
    cv.escrever(6, fx + 9, "└" + "┴".join("───" for _ in itens) + "┘", "fraco")
    cv.trechos(8, fx, [("enqueue(", "fraco"), (ex["entrou"], "novo"), (")", "fraco")])
    return cv


# ─────────────────────────── Árvores (BST e AVL) ───────────────────────────

def _esq(n):
    return getattr(n, "esq", None)        # tolera nó ainda sendo construído (__init__)


def _dir(n):
    return getattr(n, "dir", None)


def desenhar_arvore(raiz, rotulo, tag_aresta):
    """Layout por percurso em ordem: a ordem in-order vira a COLUNA do nó.

    rotulo(n)          → lista de (texto, tag) para escrever o nó
    tag_aresta(pai, f) → tag da linha que liga pai ao filho f
    """
    posicao = {}                                  # nó → (profundidade, ordem in-order)
    contador = [0]

    def visitar(n, prof):
        if n is None:
            return
        visitar(_esq(n), prof + 1)                  # esquerda primeiro...
        posicao[n] = (prof, contador[0])          # ...depois o nó ganha a próxima coluna
        contador[0] += 1
        visitar(_dir(n), prof + 1)

    visitar(raiz, 0)
    slot = max(sum(len(t) for t, _ in rotulo(n)) for n in posicao) + 1
    centro = {n: o * slot + slot // 2 for n, (_, o) in posicao.items()}
    cv = Canvas()
    for n, (prof, _) in posicao.items():
        y, x = prof * 2, centro[n]                # nós em linhas pares
        pedacos = rotulo(n)
        largura = sum(len(t) for t, _ in pedacos)
        cv.trechos(y, x - largura // 2, pedacos)  # rótulo centralizado
        if not (_esq(n) or _dir(n)):
            continue
        # linha de conexão logo abaixo: ┌───┴───┐
        if _esq(n):
            t = tag_aresta(n, _esq(n))
            cv.escrever(y + 1, centro[_esq(n)], "┌" + "─" * (x - centro[_esq(n)] - 1), t)
        if _dir(n):
            t = tag_aresta(n, _dir(n))
            cv.escrever(y + 1, x + 1, "─" * (centro[_dir(n)] - x - 1) + "┐", t)
        juncao = "┴" if _esq(n) and _dir(n) else "┘" if _esq(n) else "└"
        cv.escrever(y + 1, x, juncao, "fraco")
    return cv


def desenhar_bst():
    ex = ed.exemplo_bst()
    no_caminho = set(map(id, ex["caminho"]))
    novo = ex["novo"]

    def tag_no(n):
        return "novo" if n is novo else "destaque" if id(n) in no_caminho else "normal"

    def aresta(pai, filho):
        return "destaque" if id(pai) in no_caminho and tag_no(filho) != "normal" else "fraco"

    cv = Canvas()
    arv = desenhar_arvore(ex["raiz"], lambda n: [(f"({n.valor})", tag_no(n))], aresta)
    cv.colar(arv, 0, 2)
    # narra as decisões tomadas em cada nó do caminho
    v = ex["valor"]
    passos = [f"{v} {'<' if v < n.valor else '>'} {n.valor} → {'esq' if v < n.valor else 'dir'}"
              for n in ex["caminho"]]
    cv.trechos(arv.altura + 1, 2, [(f"inserir({v}): ", "titulo"),
                                   (",  ".join(passos), "destaque")])
    return cv


def desenhar_avl():
    ex = ed.exemplo_avl()

    def rotulo(tag_fn):
        def r(n):
            b = ed.fator(n)
            tag_fb = "alerta" if abs(b) > 1 else "fraco"
            return [(str(n.valor), tag_fn(n)), (f"({b:+d})" if b else "(0)", tag_fb)]
        return r

    desbal = {n.valor for n in _todos(ex["antes"]) if abs(ed.fator(n)) > 1}
    girados = {20, 30, 40}                            # nós que trocaram de posição na RL

    antes = desenhar_arvore(
        ex["antes"],
        rotulo(lambda n: "alerta" if n.valor in desbal else
               "novo" if n.valor == ex["valor"] else "normal"),
        lambda p, f: "fraco")
    depois = desenhar_arvore(
        ex["depois"],
        rotulo(lambda n: "novo" if n.valor in girados else "normal"),
        lambda p, f: "fraco")

    cv = Canvas()
    titulo = f"antes: inserir({ex['valor']}) sem rebalancear"
    cv.escrever(0, 2, titulo, "titulo")
    cv.colar(antes, 2, 2)
    meio = 2 + antes.altura // 2
    x2 = max(antes.largura, len(titulo)) + 9          # não deixa os títulos colidirem
    cv.escrever(meio, x2 - 5, "══▶", "ponteiro")
    cv.escrever(0, x2, "depois da rotação", "titulo")
    cv.colar(depois, 2, x2)
    base = 3 + max(antes.altura, depois.altura)
    for k, linha in enumerate(ex["log"]):
        cv.trechos(base + k, 2, [("rotação: ", "titulo"), (linha, "novo")])
    cv.escrever(base + len(ex["log"]) + 1, 2,
                "(n) ao lado da chave = fator de balanceamento = h_esq − h_dir",
                "fraco")
    return cv


def _todos(n):
    if n:
        yield n
        yield from _todos(n.esq)
        yield from _todos(n.dir)


# ───────────────────────────────── Grafo ───────────────────────────────────

def estado_vertice(v, est):
    if v == est["atual"]:
        return "destaque"                          # sendo processado agora
    if v in est["ordem"]:
        return "ok"                                # já processado
    if v in est["fila"]:
        return "fronteira"                         # descoberto, esperando na fila
    return "normal"                                # ainda não descoberto


def desenhar_grafo(estado=None):
    ex = ed.exemplo_grafo()
    g, est = ex["grafo"], estado or ex["estado"]      # permite desenhar qualquer passo
    cv = Canvas()
    # --- matriz de adjacência ---
    cv.escrever(0, 2, "matriz de adjacência", "titulo")
    for j, v in enumerate(g.vertices):
        cv.escrever(2, 6 + j * 3, v, estado_vertice(v, est))         # cabeçalho
    for i, v in enumerate(g.vertices):
        cv.escrever(3 + i, 3, v, estado_vertice(v, est))             # rótulo da linha
        for j, u in enumerate(g.vertices):
            bit = g.matriz[i][j]
            if bit and v == est["atual"]:
                tag = "destaque"                                     # vizinhos examinados
            else:
                tag = "normal" if bit else "fraco"
            cv.escrever(3 + i, 6 + j * 3, "1" if bit else "·", tag)
    # --- lista de adjacência ---
    lx = 28
    cv.escrever(0, lx, "lista de adjacência", "titulo")
    for i, v in enumerate(g.vertices):
        pedacos = [(v, estado_vertice(v, est)), (" → ", "fraco")]
        for k, u in enumerate(g.adj[v]):
            if k:
                pedacos.append((" → ", "fraco"))
            pedacos.append((f"[{u}]", "destaque" if v == est["atual"] else "normal"))
        cv.trechos(2 + i, lx, pedacos)
    # --- estado da BFS ---
    by = 4 + len(g.vertices)
    cv.trechos(by, 2, [(f"BFS a partir de {ex['origem']}   ", "titulo"),
                       ("atual: ", "fraco"), (est["atual"], "destaque"),
                       ("   fila: ", "fraco"), ("[" + ", ".join(est["fila"]) + "]", "fronteira"),
                       ("   ordem: ", "fraco"), (" ".join(est["ordem"]), "ok")])
    cv.trechos(by + 2, 2, [("■ atual  ", "destaque"), ("■ processado  ", "ok"),
                           ("■ na fila  ", "fronteira"), ("■ não descoberto", "normal")])
    return cv


# ─────────────────────────────── Tabela hash ───────────────────────────────

def desenhar_hash():
    ex = ed.exemplo_hash()
    cv = Canvas()
    for i, cadeia in enumerate(ex["buckets"]):
        tag_idx = "destaque" if i == ex["indice"] else "fraco"
        col = cv.escrever(i, 2, f"[{i}]", tag_idx)
        col = cv.escrever(i, col, " ─▶ " if cadeia else " ─▶ ∅", "fraco")
        for k, chave in enumerate(cadeia):
            if k:
                col = cv.escrever(i, col, " ─▶ ", "ponteiro")
            col = cv.escrever(i, col, f"[{chave}]",
                              "novo" if chave == ex["ultima"] else "normal")
    soma = sum(ex["codigos"])
    conta = " + ".join(map(str, ex["codigos"]))
    base = ex["m"] + 1
    cv.trechos(base, 2, [(f"h('{ex['ultima']}') = ", "titulo"),
                         (f"({conta}) % {ex['m']} = {soma} % {ex['m']} = ", "fraco"),
                         (str(ex["indice"]), "destaque")])
    tamanho = sum(len(b) for b in ex["buckets"])
    cv.escrever(base + 1, 2,
                f"colisão resolvida por encadeamento; fator de carga = {tamanho}/{ex['m']}",
                "fraco")
    return cv


# Ordem e nomes das seções, usados por todos os visualizadores
SECOES = [
    ("Array", desenhar_array),
    ("Lista encadeada", desenhar_lista),
    ("Pilha e fila", desenhar_pilha_fila),
    ("Árvore binária de busca", desenhar_bst),
    ("AVL", desenhar_avl),
    ("Grafo e BFS", desenhar_grafo),
    ("Tabela hash", desenhar_hash),
]
