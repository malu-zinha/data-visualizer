# vized — contexto para o Claude Code

## Objetivo do projeto

Visualizar no terminal, passo a passo, **qualquer código Python**: o código
roda linha a linha num painel e a memória (estruturas de dados, referências,
pilha de chamadas) aparece desenhada ao lado.

Estado atual: a interface e o motor de rastreio funcionam, mas as
visualizações são **escritas à mão por estrutura** (`src/vized/estruturas/*/cenario.py`).
O próximo passo é a versão genérica descrita em `docs/ROADMAP.md`.

## Comandos

```bash
pip install -e ".[dev]"            # instala em modo editável + pytest
vized                              # abre a interface (ou: python -m vized)
pytest                             # testes de corretude e snapshots
VIZED_ATUALIZAR=1 pytest tests/test_desenhos.py   # regrava snapshots (só após mudança intencional)
pip install -e ".[web]" && python web/gerar_pagina.py   # gera web/passo-a-passo.html (Linux/macOS)
```

Terminal com pelo menos 130 colunas para a interface.

## Arquitetura

- `src/vized/nucleo/rastreador.py` — executa sob `sys.settrace`; o evento
  `line` dispara ANTES de a linha executar. Cada `Passo` guarda a pilha de
  chamadas e uma cópia das variáveis (um único `deepcopy` com memo
  compartilhado, para preservar quem aponta para quem) e um mapa
  id(cópia) → id(original), usado para endereços `@xxxx` estáveis.
- `nucleo/canvas.py` — grade de caracteres com **tags semânticas**
  (`novo`, `destaque`, `foco`, `ponteiro`...). O desenho nunca escolhe cor;
  a interface traduz tag → estilo.
- `nucleo/layout.py` — árvore por percurso em ordem, `floresta` (nós soltos
  ou com dois pais durante rotações), composição lado a lado.
- `nucleo/cenario.py` — contrato `Cenario(preparar, executar, desenhar)`;
  só `executar` é rastreado.
- `estruturas/<nome>/codigo.py` — o código observado (aparece no painel).
  Não importa nada do visualizador.
- `estruturas/<nome>/cenario.py` — prepara, executa e desenha.
- `estruturas/__init__.py` — registro; a ordem define as abas.
- `interface/app_textual.py` — app textual (código, memória, estrutura).
- `web/` — grava a tela do app num pseudo-terminal (pyte) e gera uma página.
- `exemplos/comparacao-ferramentas/` — primeira versão (ANSI, rich, curses);
  não faz parte do pacote.

## Convenções

- Nomes, comentários, mensagens e textos da interface em **português**.
- Código com **comentários explicando linha a linha** o que não for óbvio;
  a autora quer entender o raciocínio, não só o resultado.
- Nos arquivos `codigo.py`, linhas com no máximo ~52 caracteres (cabem no painel).
- Ao se dirigir à autora ou em textos gerados para ela, use o **feminino**.
- Toda mudança de desenho deve manter `pytest` passando; snapshots só são
  regravados quando a mudança visual é intencional, e isso deve ser dito.
- Prefira explicar o porquê das decisões de design nas respostas.

## Commits — regra obrigatória

- **Nunca** adicione `Co-Authored-By`, "Generated with Claude Code",
  `Claude-Session` ou qualquer outra atribuição ao Claude em commits ou PRs.
  A autoria é exclusivamente da autora.
- `.claude/settings.json` já desativa a atribuição, e `.githooks/commit-msg`
  remove essas linhas como garantia extra (ativar com
  `git config core.hooksPath .githooks`).
- Mensagens de commit em português, curtas, no imperativo ou descritivas
  (ex.: "núcleo: achata o heap em vez de copiar").
