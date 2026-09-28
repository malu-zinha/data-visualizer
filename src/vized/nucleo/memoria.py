"""Texto curto para mostrar valores no painel de memória."""
from collections import deque


def resumo(valor, passo, largura=34):
    if hasattr(valor, "__dict__") and type(valor).__name__.startswith("No"):
        s = f"nó {getattr(valor, 'valor', '?')} {passo.endereco(valor)}"    # nós: valor + endereço
    elif isinstance(valor, deque):
        s = f"deque({list(valor)})"
    elif isinstance(valor, set):
        s = "{" + ", ".join(map(repr, sorted(valor))) + "}"                 # ordenado: estável
    elif hasattr(valor, "__dict__") and not callable(valor):
        s = f"{type(valor).__name__} {passo.endereco(valor)}"              # objetos das estruturas
    else:
        s = repr(valor)
    return s if len(s) <= largura else s[:largura - 1] + "…"
