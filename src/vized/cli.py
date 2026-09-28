"""Linha de comando: `vized` abre os cenários; `vized programa.py` rastreia um arquivo.

Uso:
    vized                               # cenários prontos (uma aba por estrutura)
    vized exemplos/bubble.py            # qualquer arquivo Python
    vized exemplos/bubble.py --max-passos 500
"""
import argparse
import os
import runpy
import sys

from vized.nucleo.cenario import Cenario
from vized.nucleo.rastreador import filtro_arquivos
from vized.renderizadores import generico

MAX_PASSOS = 2000                  # laços longos: a linha do tempo para aqui


def executar_arquivo(caminho):
    """Roda o arquivo como se fosse `python caminho`."""
    path_antigo = list(sys.path)
    # `python arquivo.py` põe a pasta do arquivo no começo do sys.path;
    # sem isso, um `import meu_modulo` ao lado do arquivo não funcionaria
    sys.path.insert(0, os.path.dirname(os.path.abspath(caminho)))
    try:
        # run_name="__main__" faz o bloco `if __name__ == "__main__":` rodar;
        # o run_path também troca sys.argv[0] pelo caminho durante a execução
        runpy.run_path(caminho, run_name="__main__")
    finally:
        sys.path[:] = path_antigo      # devolve o sys.path como estava


def cenario_do_arquivo(caminho, max_passos=MAX_PASSOS):
    """Um Cenario que rastreia o arquivo inteiro, do começo ao fim."""
    return Cenario(
        nome=os.path.basename(caminho),
        operacao=f"python {caminho}",
        preparar=dict,                         # nada a preparar: o arquivo faz tudo
        executar=lambda _estado: executar_arquivo(caminho),
        desenhar=generico.desenhar,            # caixas e setas, para qualquer heap
        filtro=filtro_arquivos(caminho),       # grava só as linhas deste arquivo
        max_passos=max_passos,
        com_globais=True,                      # num script, quase tudo é global
        arquivo=os.path.abspath(caminho),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vized",
        description="Mostra no terminal, passo a passo, o código rodando e a memória.")
    parser.add_argument("arquivo", nargs="?",
                        help="programa Python a visualizar (sem ele: cenários prontos)")
    parser.add_argument("--max-passos", type=int, default=MAX_PASSOS, metavar="N",
                        help=f"para depois de N passos (padrão: {MAX_PASSOS})")
    args = parser.parse_args(argv)

    if args.arquivo is None:
        cenarios = None                        # a interface usa os cenários prontos
    elif not os.path.isfile(args.arquivo):
        parser.error(f"arquivo não encontrado: {args.arquivo}")
    else:
        cenarios = [cenario_do_arquivo(args.arquivo, args.max_passos)]

    # importado aqui: `vized --help` responde sem carregar o textual
    from vized.interface.app_textual import VisualizadorApp
    VisualizadorApp(cenarios).run()
