"""Árvores binárias: layout por percurso em ordem e floresta (árvore em pedaços).

Os campos de ligação são parâmetros (padrão: "esq" e "dir"); no fluxo
genérico eles vêm da detecção (deteccao/formas.py), não do nome.
"""
from vized.nucleo.canvas import Canvas
from vized.nucleo.layout import lado_a_lado
from vized.nucleo.vista import do_tipo
from vized.renderizadores.comum import nomes_por_endereco, titulo


def desenhar_arvore(raiz, rotulo, tag_aresta, esq="esq", dir="dir"):
    """Layout por percurso em ordem: a ordem in-order vira a COLUNA do nó.

    rotulo(n)          → lista de (texto, tag) para escrever o nó
    tag_aresta(pai, f) → tag da linha que liga pai ao filho f
    """
    def f_esq(n):
        return getattr(n, esq, None)      # tolera nó ainda no __init__

    def f_dir(n):
        return getattr(n, dir, None)

    posicao = {}                          # nó → (profundidade, ordem in-order)
    contador = [0]

    def visitar(n, prof):
        if n is None or n in posicao:     # "in posicao": não entra em ciclo
            return
        visitar(f_esq(n), prof + 1)       # esquerda primeiro...
        posicao[n] = (prof, contador[0])  # ...depois o nó ganha a próxima coluna
        contador[0] += 1
        visitar(f_dir(n), prof + 1)

    visitar(raiz, 0)
    slot = max(sum(len(t) for t, _ in rotulo(n)) for n in posicao) + 1
    centro = {n: o * slot + slot // 2 for n, (_, o) in posicao.items()}
    cv = Canvas()
    for n, (prof, _) in posicao.items():
        y, x = prof * 2, centro[n]        # nós nas linhas pares
        pedacos = rotulo(n)
        largura = sum(len(t) for t, _ in pedacos)
        cv.trechos(y, x - largura // 2, pedacos)
        e, d = f_esq(n), f_dir(n)
        if e not in centro:               # filho fora do desenho (ciclo): sem linha
            e = None
        if d not in centro:
            d = None
        if not (e or d):
            continue
        if e:                             # linha de conexão abaixo: ┌───┴───┐
            cv.escrever(y + 1, centro[e], "┌" + "─" * (x - centro[e] - 1),
                        tag_aresta(n, e))
        if d:
            cv.escrever(y + 1, x + 1, "─" * (centro[d] - x - 1) + "┐",
                        tag_aresta(n, d))
        juncao = "┴" if e and d else "┘" if e else "└"
        cv.escrever(y + 1, x, juncao, "fraco")
    return cv


def raizes_e_compartilhados(nos, esq="esq", dir="dir"):
    """Entre os nós dados: quem ninguém aponta (raízes) e quem tem 2+ pais."""
    pais = {}                             # id(filho) → quantos nós apontam para ele
    for n in nos:
        for f in (getattr(n, esq, None), getattr(n, dir, None)):
            if f is not None:
                pais[id(f)] = pais.get(id(f), 0) + 1
    raizes = [n for n in nos if id(n) not in pais]   # ninguém aponta para elas
    compartilhados = [n for n in nos if pais.get(id(n), 0) > 1]
    return raizes, compartilhados


def floresta(passo, raizes_conhecidas, tipo, esq="esq", dir="dir"):
    """Todas as árvores visíveis: das raízes conhecidas E das variáveis locais.

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
        pilha += [getattr(n, esq, None), getattr(n, dir, None)]
    raizes, compartilhados = raizes_e_compartilhados(nos.values(), esq, dir)
    raizes.sort(key=lambda n: (not hasattr(n, "valor"), getattr(n, "valor", 0)))
    return raizes, compartilhados


# ───────────────────────────── fluxo genérico ──────────────────────────────

def desenhar_estrutura(passo, est, d):
    """Árvore detectada (campos de ligação vindos de est.no), com rotação à vista.

    Cores: foco = apontado por variável do topo; novo = nó recém-criado ou
    aresta religada agora; destaque = nó seguro por uma chamada em aberto.
    """
    v, no = passo.vista, est.no
    esq, dir = no.ligacoes
    nos = [v.objetos[i] for i in est.objetos]
    raizes, compartilhados = raizes_e_compartilhados(nos, esq, dir)
    if not raizes:                                  # só ciclos: começa por qualquer um
        raizes = nos[:1]
    nomes = {id(v.objetos[i]): ns for i, ns in nomes_por_endereco(passo).items()
             if i in v.objetos}

    def ident(n):
        return v.enderecos[id(n)]

    def tag(n):
        if id(n) in nomes:
            return "foco"
        if ident(n) in d.novos:
            return "novo"
        return "destaque" if ident(n) in d.caminho else "normal"

    def tag_aresta(pai, filho):
        campo = esq if getattr(pai, esq, None) is filho else dir
        return "novo" if d.religou(ident(pai), campo) else "fraco"

    def rotulo(n):
        valor = getattr(n, no.valor, "?") if no.valor else v.endereco(n)
        pedacos = [(str(valor), tag(n))]
        # outros campos simples (ex.: altura numa AVL) aparecem entre parênteses
        extras = [str(x) for campo, x in vars(n).items()
                  if campo not in (no.valor, *no.ligacoes)
                  and isinstance(x, (int, float, str)) and not isinstance(x, bool)]
        if extras:
            pedacos.append(("(" + ",".join(extras) + ")", "fraco"))
        return pedacos

    cv = Canvas()
    titulo(cv, est.forma, detalhe=no.tipo)
    arvores = [desenhar_arvore(r, rotulo, tag_aresta, esq, dir) for r in raizes]
    cv.colar(lado_a_lado(arvores), 2, 2)
    base = cv.altura + 1
    legenda = []
    for n in nos:
        if id(n) in nomes:
            valor = getattr(n, no.valor, "?") if no.valor else v.endereco(n)
            legenda += [(", ".join(nomes[id(n)]), "foco"), (f" → {valor}    ", "fraco")]
    if legenda:
        cv.trechos(base, 2, [("variáveis: ", "titulo")] + legenda)
        base += 1
    if len(raizes) > 1:
        cv.escrever(base, 2, f"árvore em {len(raizes)} pedaços: nó ainda sem pai"
                    " ou rotação em andamento", "fraco")
        base += 1
    for k, n in enumerate(compartilhados):
        valor = getattr(n, no.valor, "?") if no.valor else v.endereco(n)
        cv.escrever(base + k, 2, f"o nó {valor} tem DOIS pais agora", "alerta")
    return cv
