"""Visualizador 4 — curses (biblioteca padrão; no Windows: pip install windows-curses).

Uso:
    python v4_curses.py
Teclas: ↑ ↓ escolhem a estrutura · n/p andam no passo (Array e Grafo) · q sai
"""
import curses
import locale

import desenho
import estruturas as ed

# curses trabalha com "pares de cor" numerados: (frente, fundo)
PARES = {
    "normal":    (1, -1, 0),                     # (id do par, cor, atributo extra)
    "titulo":    (1, -1, curses.A_BOLD),
    "destaque":  (2, curses.COLOR_YELLOW, curses.A_BOLD),
    "novo":      (3, curses.COLOR_GREEN, curses.A_BOLD),
    "ok":        (4, curses.COLOR_BLUE, curses.A_BOLD),
    "fronteira": (5, curses.COLOR_MAGENTA, 0),
    "ponteiro":  (6, curses.COLOR_CYAN, 0),
    "fraco":     (7, curses.COLOR_WHITE, curses.A_DIM),
    "alerta":    (8, curses.COLOR_RED, curses.A_BOLD),
}


def iniciar_cores():
    curses.start_color()
    curses.use_default_colors()                  # -1 = cor padrão do terminal
    for tag, (par, cor, _) in PARES.items():
        if tag == "fraco" and curses.COLORS >= 16:
            cor = 8                              # cor 8 = cinza ("preto claro"), mais legível que A_DIM
        curses.init_pair(par, cor, -1)           # fundo -1 = transparente


def atributo(tag):
    par, _, extra = PARES[tag]
    return curses.color_pair(par) | extra        # cor + negrito/dim combinados por OU bit a bit


def desenhar_canvas(janela, canvas, y0=1, x0=2):
    """Escreve o Canvas célula a célula; curses não faz quebra nem rolagem sozinho."""
    alt, larg = janela.getmaxyx()
    for l, segmentos in enumerate(canvas.linhas()):
        if y0 + l >= alt - 1:                    # não escreve fora da janela (daria erro)
            break
        x = x0
        for texto, tag in segmentos:
            espaco = larg - 1 - x
            if espaco <= 0:
                break
            janela.addstr(y0 + l, x, texto[:espaco], atributo(tag))
            x += len(texto)


def main(tela):
    curses.curs_set(0)                           # esconde o cursor
    iniciar_cores()
    bolha = list(ed.bubble_passos(ed.ARRAY_INICIAL))
    ex_grafo = ed.exemplo_grafo()
    linhas_do_tempo = {                          # nome → [snapshots, desenho, índice atual]
        "Array": [bolha, desenho.desenhar_array, bolha.index(ed.exemplo_array())],
        "Grafo e BFS": [list(ed.bfs_passos(ex_grafo["grafo"], "A")),
                        desenho.desenhar_grafo, 2],
    }
    selecionado = 0
    while True:
        tela.erase()                             # limpa o buffer (não a tela física)
        alt, larg = tela.getmaxyx()
        menu_larg = 28
        # --- janela do menu (à esquerda) ---
        menu = tela.derwin(alt - 1, menu_larg, 0, 0)   # sub-janela com coordenadas próprias
        menu.box()
        menu.addstr(0, 2, " estruturas ", curses.A_BOLD)
        for i, (nome, _) in enumerate(desenho.SECOES):
            attr = curses.A_REVERSE if i == selecionado else 0   # item escolhido invertido
            menu.addstr(2 + i, 2, f" {nome:<{menu_larg - 6}}", attr)
        # --- janela do conteúdo (à direita) ---
        nome, funcao = desenho.SECOES[selecionado]
        corpo = tela.derwin(alt - 1, larg - menu_larg, 0, menu_larg)
        corpo.box()
        corpo.addstr(0, 2, f" {nome} ", curses.A_BOLD)
        if nome in linhas_do_tempo:
            passos, desenhar, k = linhas_do_tempo[nome]
            desenhar_canvas(corpo, desenhar(passos[k]))
            corpo.addstr(alt - 3, 2, f"passo {k + 1}/{len(passos)}", atributo("fraco"))
        else:
            desenhar_canvas(corpo, funcao())
        # --- barra de ajuda na última linha ---
        tela.addstr(alt - 1, 1, "↑↓ estrutura   n/p passo   q sair"[:larg - 2],
                    atributo("fraco"))
        tela.refresh()                           # só agora a tela física é atualizada

        tecla = tela.getch()                     # bloqueia até uma tecla
        if tecla in (ord("q"), 27):              # q ou Esc
            break
        if tecla == curses.KEY_DOWN:
            selecionado = (selecionado + 1) % len(desenho.SECOES)
        elif tecla == curses.KEY_UP:
            selecionado = (selecionado - 1) % len(desenho.SECOES)
        elif tecla in (ord("n"), ord("p")) and nome in linhas_do_tempo:
            estado = linhas_do_tempo[nome]
            delta = 1 if tecla == ord("n") else -1
            estado[2] = max(0, min(len(estado[0]) - 1, estado[2] + delta))


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")   # habilita UTF-8 (setas e bordas) no ncurses
    curses.wrapper(main)    # wrapper inicia o curses e SEMPRE restaura o terminal ao sair
