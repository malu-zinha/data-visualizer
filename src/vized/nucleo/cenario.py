"""O contrato entre as estruturas e o resto do programa.

A interface só conhece `Cenario`: nada de árvores, filas ou grafos.
Cada estrutura exporta uma lista de cenários no seu cenario.py.
"""
from dataclasses import dataclass, field
from typing import Any, Callable

from vized.nucleo.rastreador import rastrear


@dataclass
class Cenario:
    nome: str                                  # texto da aba
    operacao: str                              # ex.: "inserir_avl(raiz, 25)"
    preparar: Callable[[], dict]               # monta o estado inicial (NÃO rastreado)
    executar: Callable[[dict], Any]            # a operação rastreada, recebe o estado
    desenhar: Callable[[Any], Any]             # Passo → Canvas
    pular: tuple = ()                          # funções tratadas como "step over"
    _passos: list = field(default=None, repr=False)

    @property
    def passos(self):
        """Linha do tempo, gerada na primeira vez que alguém pede."""
        if self._passos is None:
            estado = self.preparar()                     # estrutura pronta, fora do rastreio
            self._passos, _ = rastrear(
                lambda: self.executar(estado),           # só isto é gravado
                capturar=lambda: estado,                 # o estado vai em cada foto
                pular=self.pular,
            )
        return self._passos
