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
from dataclasses import dataclass, field

# pasta src/vized/estruturas: só os codigo.py daqui dentro são "código observado"
PASTA_ESTRUTURAS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "estruturas")


@functools.lru_cache(maxsize=None)      # chamado para TODO frame: vale guardar
def e_codigo_observado(caminho):
    """True para qualquer estruturas/<nome>/codigo.py."""
    caminho = os.path.abspath(caminho)
    return (os.path.basename(caminho) == "codigo.py"
            and caminho.startswith(os.path.abspath(PASTA_ESTRUTURAS)))


def filtro_arquivos(*caminhos):
    """Filtro que aceita só os arquivos dados (ex.: o programa da usuária).

    Compara caminhos absolutos: o runpy compila o arquivo com o caminho
    do jeito que foi digitado ("exemplos/bubble.py"), que pode ser relativo.
    """
    alvos = {os.path.abspath(c) for c in caminhos}

    @functools.lru_cache(maxsize=None)  # um filtro por execução, cache próprio
    def filtro(caminho):
        return os.path.abspath(caminho) in alvos
    return filtro


class LimiteDePassos(BaseException):
    """Levantada pelo tracer quando a linha do tempo chega ao limite.

    Herda de BaseException (e não de Exception) de propósito: um
    `try/except Exception` no programa da usuária não a engole, então a
    execução realmente para, mesmo num `while True`.
    """


@dataclass
class Opaco:
    """Lugar de um valor que o deepcopy não conseguiu copiar (arquivo, gerador...).

    Remendo provisório: a etapa 2 troca o deepcopy pelo heap achatado.
    """
    tipo: str          # nome do tipo original, ex.: "TextIOWrapper"
    texto: str         # repr curto do original, feito na hora da foto

    def __repr__(self):
        return self.texto              # o repr do original já diz o tipo


@dataclass
class Quadro:
    """Um frame da pilha de chamadas (copiado)."""
    funcao: str        # nome da função ("<module>" = nível do arquivo)
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
    globais: dict = field(default_factory=dict)   # variáveis globais do arquivo (cópia)
    saida: int = 0     # quantos caracteres de print() já tinham saído até aqui

    @property
    def topo(self):
        return self.quadros[-1]                 # frame que está executando

    def endereco(self, obj):
        # a cópia tem outro id(); o mapa devolve o endereço do objeto ORIGINAL,
        # assim o mesmo nó mostra o mesmo @xxxx em todos os passos
        original = self.enderecos.get(id(obj), id(obj))
        return f"@{original & 0xFFFF:04x}"


@dataclass
class Rastreio:
    """Tudo que uma execução rastreada produziu."""
    passos: list                   # a linha do tempo
    resultado: object = None       # o que chamada() devolveu
    erro: Exception = None         # exceção do programa, se ele quebrou
    cortado: bool = False          # True = parou no limite de passos


def global_visivel(nome, valor):
    """As globais que interessam: sem __dunder__, módulos, funções e classes.

    Além de limpar o painel, isso evita copiar módulos (o deepcopy de um
    módulo levanta TypeError: qualquer `import` quebraria o rastreio).
    """
    if nome.startswith("__") and nome.endswith("__"):
        return False                            # __name__, __builtins__, __file__...
    return not (inspect.ismodule(valor) or inspect.isroutine(valor)
                or inspect.isclass(valor))


def _copiar_um(valor, memo):
    """Copia um valor com o memo compartilhado; se não der, devolve Opaco."""
    antes = dict(memo)                          # foto do memo antes de tentar
    try:
        return copy.deepcopy(valor, memo)
    except Exception:
        # uma cópia que falhou no meio pode ter deixado objetos pela metade
        # no memo; volta o memo ao que era para não reaproveitá-los depois
        memo.clear()
        memo.update(antes)
        try:
            texto = repr(valor)
        except Exception:                       # até o repr pode falhar
            texto = "?"
        return Opaco(type(valor).__name__, texto[:40])


def _copiar(locais, globais, estado, retorno):
    """Uma única cópia de tudo, preservando quem aponta para quem.

    Devolve (locais, globais, estado, retorno, memo).
    """
    memo = {}                                   # memo compartilhado = UMA cópia só
    try:
        copia = copy.deepcopy((locais, globais, estado, retorno), memo)
        return (*copia, memo)
    except Exception:
        pass                                    # algo ali não se deixa copiar...
    memo = {}                                   # ...então vai variável por variável,
    locais = [{k: _copiar_um(v, memo) for k, v in loc.items()} for loc in locais]
    globais = {k: _copiar_um(v, memo) for k, v in globais.items()}
    estado = _copiar_um(estado, memo)           # ainda com o MESMO memo
    retorno = _copiar_um(retorno, memo)
    return locais, globais, estado, retorno, memo


def rastrear(chamada, capturar=dict, pular=(), filtro=e_codigo_observado,
             max_passos=None, com_globais=False, medir_saida=None):
    """Roda `chamada()` e devolve um Rastreio.

    filtro       recebe o caminho do arquivo de um frame; só grava se devolver True
    capturar     função sem argumentos que devolve objetos extras a fotografar
    pular        nomes de funções tratadas como "step over" (não entra nelas)
    max_passos   limite da linha do tempo (None = sem limite)
    com_globais  grava também as variáveis globais do arquivo observado
    medir_saida  função sem argumentos que diz quanto de stdout já saiu
    """
    passos = []

    def interessa(frame):
        codigo = frame.f_code
        return filtro(codigo.co_filename) and codigo.co_name not in pular

    def registrar(frame, evento, retorno=None):
        if max_passos is not None and len(passos) >= max_passos:
            raise LimiteDePassos                # interrompe o programa observado
        pilha = []
        f = frame
        while f is not None:                    # sobe pela cadeia de chamadas
            if interessa(f):
                pilha.append(f)
            f = f.f_back
        pilha.reverse()                         # base primeiro, topo por último
        # no nível do arquivo, f_locals É o dicionário de globais: deixa vazio
        # para não mostrar tudo duas vezes (as globais vêm à parte)
        locais = [{} if f.f_code.co_name == "<module>" else dict(f.f_locals)
                  for f in pilha]
        globais = {}
        if com_globais:                         # globais do frame mais perto da base
            globais = {k: v for k, v in pilha[0].f_globals.items()
                       if global_visivel(k, v)}
        locais, globais, estado, ret, memo = _copiar(locais, globais, capturar(), retorno)
        enderecos = {id(c): orig for orig, c in memo.items()}
        quadros = [Quadro(f.f_code.co_name, f.f_lineno, loc, f.f_code)
                   for f, loc in zip(pilha, locais)]
        saida = medir_saida() if medir_saida else 0
        passos.append(Passo(evento, quadros, estado, ret, enderecos, globais, saida))

    def tracer(frame, evento, arg):
        if not interessa(frame):
            return None                         # não rastreia este frame
        if evento == "line":
            registrar(frame, "line")            # dispara ANTES de a linha executar
        elif evento == "return":
            registrar(frame, "return", arg)     # arg = valor retornado
        return tracer                           # continua rastreando este frame

    rastreio = Rastreio(passos)
    sys.settrace(tracer)                        # liga o rastreio
    try:
        rastreio.resultado = chamada()
    except LimiteDePassos:
        rastreio.cortado = True                 # parou de propósito no limite
    except Exception as erro:
        rastreio.erro = erro                    # o programa quebrou: os passos ficam
    finally:
        sys.settrace(None)                      # desliga mesmo se der erro
    return rastreio


_cache_fonte = {}


def fonte(codigo):
    """(linhas, primeira_linha) da função dona do code object."""
    if codigo not in _cache_fonte:
        _cache_fonte[codigo] = inspect.getsourcelines(codigo)
    return _cache_fonte[codigo]
