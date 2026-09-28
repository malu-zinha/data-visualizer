# vized: estruturas de dados no terminal

Visualizador de estruturas de dados em Python: o código roda linha a linha
no painel da esquerda e a estrutura, como está na memória naquele instante,
aparece à direita.

## Instalação e uso

    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -e ".[dev]"
    vized                              # ou: python -m vized

Teclas: ← → estrutura · n / p próximo/anterior · espaço play/pausa · r reinicia · q sai.
Use um terminal com pelo menos 130 colunas.

### Um arquivo qualquer

    vized exemplos/bubble.py                     # roda o arquivo linha a linha
    vized exemplos/bubble.py --max-passos 500    # limite da linha do tempo (padrão 2000)

Mostra o arquivo com a linha atual, a pilha de chamadas, as variáveis
globais e locais, e o que o `print()` escreveu até aquele passo. Laços
infinitos param no limite de passos; um erro no programa não perde os
passos gravados até ele; `input()` recebe fim de arquivo (não há teclado
durante a gravação). O desenho da memória para código qualquer ainda não
existe (etapa 3 do roteiro).

## Organização

    src/vized/
    ├── cli.py                  # `vized` e `vized arquivo.py`
    ├── nucleo/                 # compartilhado por todas as estruturas
    │   ├── rastreador.py       # sys.settrace: um snapshot por linha executada
    │   ├── heap.py             # memória → {endereço: descrição rasa} (JSON)
    │   ├── vista.py            # heap → objetos leves, para os desenhos
    │   ├── canvas.py           # grade de caracteres com tags semânticas
    │   ├── layout.py           # árvore, floresta, composição lado a lado
    │   ├── cenario.py          # o contrato Cenario (preparar/executar/desenhar)
    │   └── memoria.py          # textos do painel de memória
    ├── estruturas/
    │   ├── __init__.py         # registro: a ordem aqui é a ordem das abas
    │   └── <estrutura>/
    │       ├── codigo.py       # o código observado (aparece no painel)
    │       └── cenario.py      # prepara, executa e desenha cada passo
    └── interface/
        └── app_textual.py

Nos cenários, só os arquivos `estruturas/*/codigo.py` são rastreados. Eles não importam
nada do visualizador: são o código que se escreveria numa aula.

### Adicionar uma estrutura

1. Crie `src/vized/estruturas/<nome>/codigo.py` com a implementação.
2. Crie `src/vized/estruturas/<nome>/cenario.py` com uma lista `CENARIOS`.
3. Registre em `src/vized/estruturas/__init__.py`.

Uma estrutura pode ter vários cenários (ex.: inserir, remover, buscar).

## Testes

    pytest                                        # corretude + snapshots
    VIZED_ATUALIZAR=1 pytest tests/test_desenhos.py   # regrava snapshots após mudança intencional

- `tests/test_codigo.py`: as estruturas funcionam (independe do visualizador).
- `tests/test_desenhos.py`: o desenho de pontos da linha do tempo não mudou.
- `tests/test_cli.py`: `vized arquivo.py` (globais, limite, erros, saída, interface).
- `tests/test_heap.py`: o heap achatado (ciclos, sets, slots, opacos, JSON).

## Página web

    pip install -e ".[web]"
    python web/gerar_pagina.py        # Linux/macOS (usa o módulo pty)

Roda o app num terminal virtual, grava a tela a cada passo e gera
`web/passo-a-passo.html`, que abre em qualquer navegador.

## Próximos passos

O objetivo é visualizar **qualquer código**, não só as estruturas deste
repositório. O plano, em etapas, está em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Outros

`exemplos/comparacao-ferramentas/`: a primeira versão, comparando ANSI, rich e curses.
