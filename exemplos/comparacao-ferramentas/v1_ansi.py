"""Visualizador 1 — códigos ANSI puros, sem nenhuma biblioteca.

Uso:
    python v1_ansi.py            # imprime todas as estruturas
    python v1_ansi.py --animar   # anima o bubble sort redesenhando no lugar
"""
import sys
import time

import desenho
import estruturas as ed

ESC = "\033["          # "Control Sequence Introducer": todo comando começa assim

# Cada tag vira uma sequência SGR (Select Graphic Rendition): ESC[<códigos>m
CORES = {
    "normal":    "0",        # reset
    "titulo":    "1",        # negrito
    "destaque":  "1;33",     # negrito + amarelo
    "novo":      "1;32",     # negrito + verde
    "ok":        "94",       # azul claro
    "fronteira": "35",       # magenta
    "ponteiro":  "36",       # ciano
    "fraco":     "90",       # cinza ("preto claro")
    "alerta":    "1;31",     # negrito + vermelho
}


def pintar(canvas):
    """Converte o Canvas em uma string com escapes ANSI embutidos."""
    linhas = []
    for segmentos in canvas.linhas():
        partes = []
        for texto, tag in segmentos:
            # abre a cor, escreve o texto e reseta (ESC[0m) para não "vazar"
            partes.append(f"{ESC}{CORES[tag]}m{texto}{ESC}0m")
        linhas.append("".join(partes))
    return "\n".join(linhas)


def cabecalho(nome):
    # 1;4 = negrito sublinhado; o terminal interpreta, o Python só envia bytes
    return f"{ESC}1;4m{nome}{ESC}0m\n"


def imprimir_tudo(secoes=desenho.SECOES):
    for nome, funcao in secoes:
        sys.stdout.write(cabecalho(nome))       # título da seção
        sys.stdout.write(pintar(funcao()))      # desenho colorido
        sys.stdout.write("\n\n")


def animar(atraso=0.6):
    """Mostra o ponto forte do ANSI: controle do cursor para redesenhar."""
    sys.stdout.write(f"{ESC}?25l")               # esconde o cursor
    try:
        for foto in ed.bubble_passos(ed.ARRAY_INICIAL):
            sys.stdout.write(f"{ESC}H{ESC}2J")   # cursor para (1,1) + limpa a tela
            sys.stdout.write(cabecalho("Array (animado)"))
            sys.stdout.write(pintar(desenho.desenhar_array(foto)) + "\n")
            sys.stdout.flush()                   # força a saída agora
            time.sleep(atraso)
    finally:
        sys.stdout.write(f"{ESC}?25h\n")         # devolve o cursor mesmo com Ctrl+C


if __name__ == "__main__":
    if "--animar" in sys.argv:
        animar()
    else:
        imprimir_tudo()
