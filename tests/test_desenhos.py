"""O desenho de cada passo continua igual? (testes de snapshot)

Para (re)gerar os arquivos esperados depois de uma mudança INTENCIONAL:
    VIZED_ATUALIZAR=1 pytest tests/test_desenhos.py
"""
import os
import re
import unicodedata
from pathlib import Path

import pytest

from vized.estruturas import CENARIOS

PASTA = Path(__file__).parent / "snapshots"
ATUALIZAR = os.environ.get("VIZED_ATUALIZAR") == "1"


def slug(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def normalizar(texto):
    # endereços @xxxx vêm do id() e mudam a cada execução: não fazem parte do teste
    return re.sub(r"@[0-9a-f]{4}", "@····", texto) + "\n"


@pytest.mark.parametrize("cenario", CENARIOS, ids=lambda c: slug(c.nome))
def test_todos_os_passos_desenham(cenario):
    assert cenario.erro is None                 # o rastreio guarda o erro em vez de estourar
    for passo in cenario.passos:                # nenhum passo pode quebrar o desenho
        cenario.desenhar(passo)


@pytest.mark.parametrize("cenario", CENARIOS, ids=lambda c: slug(c.nome))
def test_snapshots(cenario):
    n = len(cenario.passos)
    for k in sorted({0, n // 4, n // 2, 3 * n // 4, n - 1}):   # cinco pontos da linha do tempo
        atual = normalizar(cenario.desenhar(cenario.passos[k]).texto_puro())
        arquivo = PASTA / f"{slug(cenario.nome)}_{k:03d}.txt"
        if ATUALIZAR:
            PASTA.mkdir(exist_ok=True)
            arquivo.write_text(atual, encoding="utf-8")
            continue
        assert arquivo.exists(), f"sem snapshot: rode com VIZED_ATUALIZAR=1 ({arquivo.name})"
        assert atual == arquivo.read_text(encoding="utf-8"), f"desenho mudou em {arquivo.name}"
