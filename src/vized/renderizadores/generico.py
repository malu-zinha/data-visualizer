"""Renderizador genérico: qualquer heap desenhado como caixas e setas.

É a rede de segurança: funciona para qualquer programa, mesmo que o
desenho fique feio. O layout segue o Python Tutor:

    variáveis globais        list @1a2b
    ┌──────────────┐         ┌───┬───┬───┐
    │ numeros  ●───┼────────▶│ 5 │ 2 │ 9 │
    │ fim      True│         └───┴───┴───┘
    └──────────────┘           0   1   2

- coluna 0: caixas de variáveis (globais e uma por chamada de função);
- coluna k: objetos a k referências de distância das variáveis
  (profundidade de uma busca em largura);
- referência para a coluna seguinte vira seta; qualquer outra (ciclo,
  auto-referência, alvo na mesma coluna) vira o endereço "@xxxx" escrito.
"""
from collections import deque
from dataclasses import dataclass, field

from vized.nucleo.canvas import Canvas
from vized.nucleo.heap import endereco

MAX_OBJETOS = 60        # a partir daqui, objetos não são desenhados
MAX_ITENS = 12          # itens por lista/dicionário/objeto
MAX_TEXTO = 18          # largura máxima de um valor escrito
MAX_DEITADA = 60        # largura máxima de uma lista desenhada na horizontal
PONTO = "●"             # onde nasce uma seta


# ───────────────────────────── modelo das caixas ───────────────────────────

@dataclass
class Linha:
    """Uma linha dentro de uma caixa: rótulo (nome, índice, chave) e valor."""
    rotulo: str
    valor: str
    alvo: int = None               # endereço de destino, se a linha tem seta
    tag_rotulo: str = "normal"
    tag_valor: str = "normal"


@dataclass
class Caixa:
    titulo: list                   # [(texto, tag)], escrito acima da caixa
    linhas: list = field(default_factory=list)   # desenho vertical
    celulas: list = None           # desenho deitado: textos das células
    ident: int = None              # endereço do objeto (None = caixa de variáveis)
    x: int = 0
    y: int = 0                     # linha do título

    def __post_init__(self):
        if self.celulas is None:
            self.larg_rotulo = max((len(l.rotulo) for l in self.linhas), default=0)
            self.larg_valor = max((len(l.valor) for l in self.linhas), default=0)

    @property
    def largura_caixa(self):
        """Da borda esquerda à direita, inclusive."""
        if self.celulas is not None:
            return 1 + sum(len(c) + 3 for c in self.celulas) if self.celulas else 2
        miolo = self.larg_valor + 2                       # " valor "
        if self.larg_rotulo:
            miolo += self.larg_rotulo + 2                 # "rótulo  "
        return miolo + 2                                  # as duas bordas

    @property
    def largura(self):
        """Espaço ocupado na coluna (o título pode ser mais largo que a caixa)."""
        return max(self.largura_caixa, sum(len(t) for t, _ in self.titulo))

    @property
    def altura(self):
        if self.celulas is not None:
            return 5                                      # título, 3 linhas, índices
        return len(self.linhas) + 3                       # título, bordas e linhas

    def linha_de(self, i):
        """Linha absoluta da i-ésima Linha da caixa (onde a seta nasce)."""
        return self.y + 2 + i


# ───────────────────────────── do heap às caixas ───────────────────────────

def _texto_primitivo(x):
    s = repr(x)
    return s if len(s) <= MAX_TEXTO else s[:MAX_TEXTO - 1] + "…"


def _refs_do_objeto(e):
    """(rótulo, ref) de cada coisa dentro de um objeto do heap, já limitada."""
    forma = e["forma"]
    if forma == "objeto":
        itens = list(e["campos"].items())
    elif forma == "dicionario":
        itens = [(k, v) for k, v in e["pares"]]           # rótulo = ref da chave
    elif forma == "sequencia":
        rotular = e["tipo"] not in ("set", "frozenset")  # set não tem índice
        itens = [(str(i) if rotular else "", r) for i, r in enumerate(e["itens"])]
    else:
        itens = []
    return itens[:MAX_ITENS], len(itens) - MAX_ITENS     # (itens, quantos sobraram)


def _profundidades(raizes, heap):
    """Busca em largura a partir das variáveis: endereço → coluna.

    A ordem de descoberta também é devolvida: ela decide quem entra quando
    há mais de MAX_OBJETOS e desempata a posição vertical.
    """
    prof, ordem = {}, []
    fila = deque((r, 1) for r in raizes)
    while fila:
        ident, d = fila.popleft()
        if ident in prof or ident not in heap or len(ordem) >= MAX_OBJETOS:
            continue
        prof[ident] = d
        ordem.append(ident)
        itens, _ = _refs_do_objeto(heap[ident])
        for rotulo, r in itens:
            for ref in (r, rotulo) if isinstance(rotulo, tuple) else (r,):
                if ref[0] == "ref":                       # chave de dict também pode ser objeto
                    fila.append((ref[1], d + 1))
    return prof, ordem


def _linha(rotulo, r, prof_origem, prof):
    """Linha de caixa para uma referência vista a partir da coluna prof_origem."""
    if r[0] == "valor":
        return Linha(rotulo, _texto_primitivo(r[1]))
    ident = r[1]
    if prof.get(ident) == prof_origem + 1:                # alvo na coluna seguinte: seta
        return Linha(rotulo, PONTO, alvo=ident, tag_valor="ponteiro")
    return Linha(rotulo, endereco(ident), tag_valor="ponteiro")   # o resto: endereço escrito


def _caixa_do_objeto(ident, heap, prof):
    caixa = _montar_caixa(ident, heap, prof)
    caixa.ident = ident
    return caixa


def _montar_caixa(ident, heap, prof):
    e, d = heap[ident], prof[ident]
    titulo = [(e["tipo"], "titulo"), (" " + endereco(ident), "fraco")]
    if e["forma"] == "opaco":
        return Caixa(titulo, [Linha("", e["texto"][:MAX_TEXTO * 2], tag_valor="fraco")])
    itens, sobra = _refs_do_objeto(e)
    if (e["forma"] == "sequencia" and itens
            and all(r[0] == "valor" for _, r in itens)):
        celulas = [_texto_primitivo(r[1]) for _, r in itens]
        if sobra > 0:
            celulas.append("…")
        if sum(len(c) + 3 for c in celulas) <= MAX_DEITADA:
            return Caixa(titulo, celulas=celulas)         # lista de primitivos: deitada
    linhas = []
    for rotulo, r in itens:
        if isinstance(rotulo, tuple):                     # chave de dicionário (é uma ref)
            rotulo = (_texto_primitivo(rotulo[1]) if rotulo[0] == "valor"
                      else endereco(rotulo[1]))
        linhas.append(_linha(rotulo, r, d, prof))
    if sobra > 0:
        linhas.append(Linha("…", f"+{sobra}", tag_rotulo="fraco", tag_valor="fraco"))
    if not linhas:
        linhas.append(Linha("", "(vazio)", tag_valor="fraco"))
    return Caixa(titulo, linhas)


def _caixas_de_variaveis(passo, prof):
    """Coluna 0: globais, estado (cenários) e uma caixa por chamada de função."""
    caixas = []

    def caixa(titulo, variaveis, tag_nome="normal", extra=()):
        linhas = [_linha(nome, r, 0, prof) for nome, r in variaveis.items()]
        for l in linhas:
            l.tag_rotulo = tag_nome
        linhas += list(extra)
        if linhas:
            caixas.append(Caixa(titulo, linhas))

    caixa([("variáveis globais", "titulo")], passo.globais)
    caixa([("estado", "titulo")], passo.estado)
    for k, q in enumerate(passo.quadros):
        if q.funcao == "<module>":
            continue                                      # o módulo são as globais
        no_topo = k == len(passo.quadros) - 1
        extra = []
        if no_topo and passo.evento == "return":
            ret = _linha("retorna", passo.retorno, 0, prof)
            ret.tag_rotulo = "ok"
            extra.append(ret)
        caixa([(f"{q.funcao}()", "foco" if no_topo else "titulo")], q.locais,
              "destaque" if no_topo else "normal", extra)
    return caixas


# ───────────────────────────── desenho ─────────────────────────────────────

def _escrever_caixa(cv, c):
    cv.trechos(c.y, c.x, c.titulo)
    if c.celulas is not None:                             # deitada: │ 5 │ 2 │ 9 │
        larguras = [len(t) + 2 for t in c.celulas]
        cv.escrever(c.y + 1, c.x, "┌" + "┬".join("─" * w for w in larguras) + "┐", "fraco")
        cv.escrever(c.y + 3, c.x, "└" + "┴".join("─" * w for w in larguras) + "┘", "fraco")
        col = c.x
        for i, (texto, w) in enumerate(zip(c.celulas, larguras)):
            cv.escrever(c.y + 2, col, "│", "fraco")
            cv.escrever(c.y + 2, col + 1, texto.center(w))
            if texto != "…":
                cv.escrever(c.y + 4, col + 1, str(i).center(w), "fraco")   # índice
            col += w + 1
        cv.escrever(c.y + 2, col, "│", "fraco")
        return
    w = c.largura_caixa
    cv.escrever(c.y + 1, c.x, "┌" + "─" * (w - 2) + "┐", "fraco")
    for i, l in enumerate(c.linhas):
        lin = c.linha_de(i)
        cv.escrever(lin, c.x, "│", "fraco")
        col = c.x + 2
        if c.larg_rotulo:
            cv.escrever(lin, col, l.rotulo, l.tag_rotulo)
            col += c.larg_rotulo + 2
        cv.escrever(lin, col, l.valor, l.tag_valor)
        if l.alvo is not None:                            # ●──── até a borda: a seta sai dali
            fim = c.x + w - 1
            cv.escrever(lin, col + 1, "─" * (fim - col), "ponteiro")
        else:
            cv.escrever(lin, c.x + w - 1, "│", "fraco")
    cv.escrever(c.y + 2 + len(c.linhas), c.x, "└" + "─" * (w - 2) + "┘", "fraco")


# direções que passam por uma célula → caractere de desenho de caixa
N, S, L, O = "N", "S", "L", "O"          # norte, sul, leste, oeste
_JUNCOES = {
    frozenset("LO"): "─", frozenset("NS"): "│",
    frozenset("SL"): "┌", frozenset("SO"): "┐", frozenset("NL"): "└", frozenset("NO"): "┘",
    frozenset("NSL"): "├", frozenset("NSO"): "┤", frozenset("SLO"): "┬", frozenset("NLO"): "┴",
    frozenset("NSLO"): "┼", frozenset("L"): "─", frozenset("O"): "─",
    frozenset("N"): "│", frozenset("S"): "│",
}


class _Setas:
    """Acumula as direções de cada célula; só no fim vira caractere.

    Assim duas setas que se cruzam viram "┼" e duas que se juntam viram
    "┴"/"┬", sem que uma apague a outra.
    """

    def __init__(self):
        self.direcoes = {}                                # (lin, col) → set de direções
        self.pontas = set()                               # onde vai "▶"

    def _marcar(self, lin, col, d):
        self.direcoes.setdefault((lin, col), set()).add(d)

    def horizontal(self, lin, xa, xb):
        a, b = min(xa, xb), max(xa, xb)
        for x in range(a, b):
            self._marcar(lin, x, L)
            self._marcar(lin, x + 1, O)

    def vertical(self, col, ya, yb):
        a, b = min(ya, yb), max(ya, yb)
        for y in range(a, b):
            self._marcar(y, col, S)
            self._marcar(y + 1, col, N)

    def seta(self, lin_origem, x_origem, x_raia, lin_alvo, x_alvo):
        """Sai para a direita, desce/sobe na raia, entra no alvo com ▶."""
        self._marcar(lin_origem, x_origem, O)             # continua o ●──── da caixa
        self.horizontal(lin_origem, x_origem, x_raia)
        self.vertical(x_raia, lin_origem, lin_alvo)
        self.horizontal(lin_alvo, x_raia, x_alvo - 2)
        self.pontas.add((lin_alvo, x_alvo - 2))           # "▶ título"

    def desenhar(self, cv):
        for (lin, col), ds in self.direcoes.items():
            cv.escrever(lin, col, _JUNCOES.get(frozenset(ds), "┼"), "ponteiro")
        for lin, col in self.pontas:
            cv.escrever(lin, col, "▶", "ponteiro")


@dataclass
class Montagem:
    """Onde cada coisa vai; separado do desenho para poder ser testado."""
    colunas: list          # [[Caixa]], coluna 0 = variáveis
    setas: list            # [(linha de origem, x de origem, x da raia, endereço do alvo)]
    caixa_de: dict         # endereço → Caixa
    cortou: bool           # passou de MAX_OBJETOS?


def montar(passo):
    """Passo (JSON) → Montagem: caixas com posição e setas com raia."""
    heap = passo.heap
    raizes = [r[1] for variaveis in (passo.globais, passo.estado,
                                     *(q.locais for q in passo.quadros))
              for r in variaveis.values() if r[0] == "ref"]
    if passo.evento == "return" and passo.retorno[0] == "ref":
        raizes.append(passo.retorno[1])
    prof, ordem = _profundidades(raizes, heap)

    # 1) as caixas, separadas em colunas
    colunas = [_caixas_de_variaveis(passo, prof)]
    caixa_de = {}                                         # endereço → caixa
    for ident in ordem:                                   # ordem da busca em largura
        while len(colunas) <= prof[ident]:
            colunas.append([])
        caixa_de[ident] = _caixa_do_objeto(ident, heap, prof)
        colunas[prof[ident]].append(caixa_de[ident])

    # 2) posições, coluna a coluna, e as setas que saem de cada uma
    setas_pendentes = []            # (linha de origem, x de origem, x da raia, alvo)
    chegando = {}                   # endereço → linha da 1ª seta que chega nele
    origens = {}                    # linha → alvo da seta que SAI nela (coluna anterior)
    x = 0
    for k, coluna in enumerate(colunas):
        y_livre = 0
        # cada caixa tenta ficar na altura da seta que chega nela (seta reta);
        # se não couber, vai para baixo da anterior
        posicao = {id(c): n for n, c in enumerate(coluna)}
        for c in sorted(coluna, key=lambda c: (chegando.get(c.ident, 0), posicao[id(c)])):
            y = max(y_livre, chegando.get(c.ident, 0))
            # o título não pode ficar numa linha de onde sai a seta de OUTRA
            # caixa: os dois traços se fundiriam e a seta pareceria apontar para cá
            while y in origens and origens[y] != c.ident:
                y += 1
            c.x, c.y = x, y
            y_livre = c.y + c.altura + 1
        # setas desta coluna para a próxima: cada uma ganha sua raia vertical
        saindo = sorted(((c.linha_de(i), c, l) for c in coluna
                         for i, l in enumerate(c.linhas) if l.alvo is not None),
                        key=lambda t: t[0])
        largura = max(c.largura for c in coluna) if coluna else 0
        origens = {lin: l.alvo for lin, c, l in saindo}
        for raia, (lin, c, l) in enumerate(saindo):
            chegando.setdefault(l.alvo, lin)              # a 1ª (mais alta) decide
            setas_pendentes.append((lin, c.x + c.largura_caixa, x + largura + 1 + raia, l.alvo))
        x += largura + len(saindo) + 3                    # caixas + raias + "▶ "

    return Montagem(colunas, setas_pendentes, caixa_de, len(ordem) >= MAX_OBJETOS)


def desenhar(passo):
    """Passo (JSON) → Canvas com caixas e setas."""
    m = montar(passo)
    cv = Canvas()
    if not any(m.colunas):
        cv.escrever(0, 0, "(nenhuma variável ainda)", "fraco")
        return cv
    # setas primeiro; as caixas são escritas por cima
    setas = _Setas()
    for lin, x_origem, x_raia, alvo in m.setas:
        destino = m.caixa_de[alvo]
        setas.seta(lin, x_origem, x_raia, destino.y, destino.x)
    setas.desenhar(cv)
    for coluna in m.colunas:
        for c in coluna:
            _escrever_caixa(cv, c)
    if m.cortou:
        cv.escrever(cv.altura + 1, 0, f"(só os {MAX_OBJETOS} primeiros objetos foram desenhados)",
                    "fraco")
    return cv
