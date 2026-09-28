"""Executa uma operação sob sys.settrace e grava um snapshot a cada linha.

É o que liga "linha do código" e "estado da memória": cada Passo guarda
qual linha VAI executar, a pilha de chamadas e uma cópia de tudo que
estava nas variáveis naquele instante.
"""
import copy
import functools
import inspect
import os
import sys
from dataclasses import dataclass

# pasta src/vized/estruturas: só os codigo.py daqui dentro são "código observado"
PASTA_ESTRUTURAS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "estruturas")


@functools.lru_cache(maxsize=None)      # chamado para TODO frame: vale guardar
def e_codigo_observado(caminho):
    """True para qualquer estruturas/<nome>/codigo.py."""
    caminho = os.path.abspath(caminho)
    return (os.path.basename(caminho) == "codigo.py"
            and caminho.startswith(os.path.abspath(PASTA_ESTRUTURAS)))


@dataclass
class Quadro:
    """Um frame da pilha de chamadas (copiado)."""
    funcao: str        # nome da função
    linha: int         # linha atual dentro dela
    locais: dict       # cópia das variáveis locais
    codigo: object     # code object, para achar o código-fonte


@dataclass
class Passo:
    evento: str        # "line" = vai executar a linha; "return" = está retornando
    quadros: list      # pilha de chamadas, da base para o topo
    estado: dict       # objetos extras que o cenário pediu para fotografar
    retorno: object    # valor retornado (só quando evento == "return")
    enderecos: dict    # id(cópia) → id(original)

    @property
    def topo(self):
        return self.quadros[-1]                 # frame que está executando

    def endereco(self, obj):
        # a cópia tem outro id(); o mapa devolve o endereço do objeto ORIGINAL,
        # assim o mesmo nó mostra o mesmo @xxxx em todos os passos
        original = self.enderecos.get(id(obj), id(obj))
        return f"@{original & 0xFFFF:04x}"


def rastrear(chamada, capturar=dict, pular=(), filtro=e_codigo_observado):
    """Roda `chamada()` e devolve (lista de Passos, resultado).

    filtro    recebe o caminho do arquivo de um frame; só grava se devolver True
    capturar  função sem argumentos que devolve objetos extras a fotografar
    pular     nomes de funções tratadas como "step over" (não entra nelas)
    """
    passos = []

    def interessa(frame):
        codigo = frame.f_code
        return filtro(codigo.co_filename) and codigo.co_name not in pular

    def registrar(frame, evento, retorno=None):
        pilha = []
        f = frame
        while f is not None:                    # sobe pela cadeia de chamadas
            if interessa(f):
                pilha.append(f)
            f = f.f_back
        pilha.reverse()                         # base primeiro, topo por último
        bruto = ([dict(f.f_locals) for f in pilha], capturar(), retorno)
        memo = {}                               # memo compartilhado = UMA cópia só,
        locais, estado, ret = copy.deepcopy(bruto, memo)  # preservando quem aponta p/ quem
        enderecos = {id(c): orig for orig, c in memo.items()}
        quadros = [Quadro(f.f_code.co_name, f.f_lineno, loc, f.f_code)
                   for f, loc in zip(pilha, locais)]
        passos.append(Passo(evento, quadros, estado, ret, enderecos))

    def tracer(frame, evento, arg):
        if not interessa(frame):
            return None                         # não rastreia este frame
        if evento == "line":
            registrar(frame, "line")            # dispara ANTES de a linha executar
        elif evento == "return":
            registrar(frame, "return", arg)     # arg = valor retornado
        return tracer                           # continua rastreando este frame

    sys.settrace(tracer)                        # liga o rastreio
    try:
        resultado = chamada()
    finally:
        sys.settrace(None)                      # desliga mesmo se der erro
    return passos, resultado


_cache_fonte = {}


def fonte(codigo):
    """(linhas, primeira_linha) da função dona do code object."""
    if codigo not in _cache_fonte:
        _cache_fonte[codigo] = inspect.getsourcelines(codigo)
    return _cache_fonte[codigo]
