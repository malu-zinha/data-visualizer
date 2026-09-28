"""Visualizador 2 — rich: painéis, tabelas, árvores e redesenho com Live.

Uso:
    python v2_rich.py            # imprime todas as estruturas em painéis
    python v2_rich.py --animar   # bubble sort animado com rich.live.Live
"""
import sys
import time

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

import desenho
import estruturas as ed

# Mesmas tags do desenho.py, agora como "estilos" do rich (sintaxe legível)
ESTILOS = {
    "normal": "", "titulo": "bold", "destaque": "bold yellow",
    "novo": "bold green", "ok": "bright_blue", "fronteira": "magenta",
    "ponteiro": "cyan", "fraco": "bright_black", "alerta": "bold red",
}


def para_text(canvas):
    """Canvas → rich.Text: o rich cuida dos escapes e da largura dos caracteres."""
    texto = Text()
    for i, segmentos in enumerate(canvas.linhas()):
        if i:
            texto.append("\n")
        for pedaco, tag in segmentos:
            texto.append(pedaco, style=ESTILOS[tag])   # cada trecho com seu estilo
    return texto


def painel(conteudo, titulo):
    # Panel desenha a moldura; box.ROUNDED escolhe os cantos arredondados
    return Panel(conteudo, title=f"[bold]{titulo}", title_align="left",
                 box=box.ROUNDED, border_style="bright_black", expand=False)


def arvore_nativa(no, pai=None):
    """Mesma BST usando rich.Tree: vista 'deitada', ótima para árvores profundas."""
    rotulo = Text(str(no.valor), style="bold")
    ramo = pai.add(rotulo) if pai else Tree(rotulo, guide_style="bright_black")
    for filho, lado in ((no.esq, "esq"), (no.dir, "dir")):
        if filho:
            arvore_nativa(filho, ramo).label = Text.assemble(
                (f"{lado}: ", "bright_black"), (str(filho.valor), "bold"))
    return ramo


def linha_do_tempo_bfs():
    """Tabela com TODOS os passos da BFS: o histórico que a tela única não mostra."""
    ex = ed.exemplo_grafo()
    tabela = Table(box=box.SIMPLE_HEAD, header_style="bold", show_edge=False)
    for coluna in ("passo", "atual", "fila depois", "ordem"):
        tabela.add_column(coluna)
    for k, est in enumerate(ed.bfs_passos(ex["grafo"], ex["origem"]), start=1):
        agora = est["atual"] == ex["estado"]["atual"]      # linha do snapshot exibido
        tabela.add_row(str(k), est["atual"], "[" + ", ".join(est["fila"]) + "]",
                       " ".join(est["ordem"]),
                       style="bold yellow" if agora else None)
    return tabela


def renderizavel(nome, funcao):
    """Escolhe, por seção, o que o rich tem de melhor a acrescentar."""
    base = para_text(funcao())
    if nome == "Árvore binária de busca":
        return painel(Columns([base, painel(arvore_nativa(ed.exemplo_bst()["raiz"]),
                                            "rich.Tree")], padding=(0, 4)), nome)
    if nome == "Grafo e BFS":
        return painel(Group(base, Text(), Text("linha do tempo", style="bold"),
                            linha_do_tempo_bfs()), nome)
    return painel(base, nome)


def imprimir_tudo(console=None, secoes=desenho.SECOES):
    console = console or Console()
    for nome, funcao in secoes:
        console.print(renderizavel(nome, funcao))


def animar(atraso=0.6):
    console = Console()
    passos = list(ed.bubble_passos(ed.ARRAY_INICIAL))
    # Live redesenha só o que mudou, sem piscar a tela inteira
    with Live(console=console, refresh_per_second=20) as live:
        for k, foto in enumerate(passos, start=1):
            conteudo = Group(para_text(desenho.desenhar_array(foto)), Text(),
                             Text(f"passo {k}/{len(passos)}", style="bright_black"))
            live.update(painel(conteudo, "Array (animado)"))
            time.sleep(atraso)


if __name__ == "__main__":
    animar() if "--animar" in sys.argv else imprimir_tudo()
