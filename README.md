# vized: código Python e memória, passo a passo, no terminal

Visualizador de **qualquer programa Python**: o código roda linha a linha
no painel da esquerda e a memória daquele instante aparece desenhada à
direita. Listas encadeadas, árvores, matrizes, grafos, tabelas hash,
arrays e filas são reconhecidos pela **forma** (como os objetos se ligam,
não pelos nomes) e ganham desenho próprio; todo o resto aparece como
caixas e setas, no estilo do Python Tutor.

## Instalação e uso

    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -e ".[dev]"

    vized                                        # os exemplos de exemplos/, uma aba cada
    vized meu_programa.py                        # qualquer arquivo
    vized avl                                    # atalho para exemplos/avl.py
    vized meu_programa.py --max-passos 500       # limite da linha do tempo (padrão 2000)

Teclas: ← → aba · n / p próximo/anterior · espaço play/pausa · r reinicia · q sai.
Use um terminal com pelo menos 130 colunas.

A tela mostra:

- o arquivo, com a linha que **vai** executar destacada;
- a pilha de chamadas e as variáveis globais e locais;
- o que o `print()` escreveu até aquele passo;
- a memória desenhada. Verde = acabou de nascer ou de mudar (nó novo,
  célula trocada, seta religada); amarelo = seguro por uma chamada em
  aberto (ex.: o caminho de uma recursão); fundo amarelo = apontado por
  uma variável da função atual.

Laços infinitos param no limite de passos; um erro no programa não perde
os passos gravados até ele; `input()` recebe fim de arquivo (não há
teclado durante a gravação).

## Exemplos

`exemplos/`: `bubble`, `lista_encadeada`, `pilha_fila`, `bst`, `avl`,
`grafo`, `hash` e `turma` (dicionário de listas de objetos). São programas
comuns, que rodam com `python` também; eles não importam nada do vized.
Para acrescentar um, basta criar `exemplos/<nome>.py`: ele vira uma aba e
entra nos testes de snapshot.

## Como funciona

    vized programa.py
      → rastrear         sys.settrace: um passo por linha executada
      → achatar          memória → {endereço: descrição rasa} (JSON puro)
      → detectar forma   lista? árvore? matriz? array? (pelo grafo do heap)
      → desenhar         desenho da forma + caixas e setas para o resto
      → destacar         o que mudou desde o passo anterior

    src/vized/
    ├── cli.py                  # `vized`, `vized arquivo.py`, `vized <exemplo>`
    ├── nucleo/
    │   ├── rastreador.py       # sys.settrace: Passo = pilha + variáveis + heap
    │   ├── heap.py             # memória → {endereço: descrição rasa}
    │   ├── vista.py            # heap → objetos leves (para desenhar com n.esq)
    │   ├── diferenca.py        # o que mudou entre dois passos (destaques)
    │   ├── canvas.py           # grade de caracteres com tags semânticas
    │   ├── cenario.py          # uma execução rastreada = uma aba
    │   └── memoria.py          # textos do painel de memória
    ├── deteccao/
    │   └── formas.py           # regras de forma, olhando só o grafo
    ├── renderizadores/
    │   ├── automatico.py       # escolhe o desenho de cada forma detectada
    │   ├── generico.py         # qualquer heap: caixas e setas
    │   └── arvore.py, lista.py, array.py, sequencia.py, grafo.py, buckets.py
    └── interface/
        └── app_textual.py      # código, memória, saída e desenho

O desenho nunca escolhe cor: ele marca trechos com tags (`novo`,
`destaque`, `foco`...) e a interface traduz tag → estilo.

## Testes

    pytest                                             # tudo
    VIZED_ATUALIZAR=1 pytest tests/test_desenhos.py    # regrava snapshots (só após mudança intencional)

- `tests/test_desenhos.py`: cada exemplo, pelo fluxo completo, desenha igual
  às snapshots em `tests/snapshots/`.
- `tests/test_codigo.py`: os exemplos funcionam (independe do visualizador).
- `tests/test_cli.py`: `vized arquivo.py` (globais, limite, erros, saída, interface).
- `tests/test_heap.py`: o heap achatado (ciclos, sets, slots, opacos, JSON).
- `tests/test_generico.py`: caixas e setas para qualquer programa
  (+ snapshots em `tests/snapshots/generico/`).
- `tests/test_formas.py`: detecção de cada forma.
- `tests/test_diferenca.py`: destaques por diferença entre passos (tags).

## Página web

    pip install -e ".[web]"
    python web/gerar_pagina.py        # Linux/macOS (usa o módulo pty)

Roda o app num terminal virtual, grava a tela a cada passo de cada exemplo
e gera `web/passo-a-passo.html`, que abre em qualquer navegador.

## Histórico

O caminho de "cenários desenhados à mão" até "qualquer código" está em
[`docs/ROADMAP.md`](docs/ROADMAP.md) (etapas 1 a 6, cada uma com uma tag
`etapa-N` no git). `exemplos/comparacao-ferramentas/` guarda a primeira
versão, comparando ANSI, rich e curses.
