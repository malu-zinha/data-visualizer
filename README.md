# vized — veja seu código Python rodando e a memória mudando, passo a passo

O **vized** roda um programa Python e mostra, no terminal, **cada linha
sendo executada** junto com **um desenho da memória** naquele instante:
as variáveis, os objetos, quem aponta para quem e a pilha de chamadas.
Dá para avançar e voltar no tempo, uma linha de cada vez.

```
vized meu_programa.py
```

---

## Para que serve

Quando a gente estuda programação, boa parte do que importa acontece
**dentro** da memória, onde não dá para ver: duas variáveis que apontam
para o mesmo objeto, uma lista alterada dentro de uma função, os nós de
uma lista encadeada sendo religados, a pilha crescendo numa recursão.
O vized **desenha** tudo isso.

Ele é útil para:

- **quem está aprendendo** programação ou estruturas de dados: em vez de
  imaginar o que acontece, você vê;
- **quem ensina**: dá para mostrar um algoritmo linha por linha, indo e
  voltando, com a estrutura desenhada ao lado;
- **quem está depurando um algoritmo pequeno**: dá para ver em que passo
  uma referência foi parar no lugar errado.

Alguns exemplos do que ele ajuda a entender:

| Dúvida comum | O que o vized mostra |
|---|---|
| "Por que minha lista mudou lá fora, se eu só alterei o parâmetro?" | As duas variáveis com setas para a **mesma** lista. |
| "O que acontece com a pilha numa recursão?" | Uma caixa por chamada em aberto, e o caminho percorrido destacado em amarelo. |
| "Como o nó novo entra na lista encadeada?" | O nó nascendo solto e, no passo seguinte, a seta sendo religada (em verde). |
| "O que muda numa rotação de árvore AVL?" | A árvore se partindo em pedaços e se remontando, aresta por aresta. |

A diferença para um depurador comum é que o vized **grava a execução
inteira** antes de mostrar. Por isso você pode voltar atrás quando quiser.
Além disso, ele **desenha** a memória, em vez de listar valores.

---

## Como funciona

Por trás da tela acontecem quatro coisas:

1. **Grava.** O vized roda o seu programa uma vez, do começo ao fim. A
   cada linha, antes de ela executar, anota a pilha de chamadas e o
   conteúdo de todas as variáveis. Isso acontece **antes** de a tela
   abrir. Depois você só navega pela gravação.
2. **Fotografa a memória.** Cada objeto vira uma descrição com um
   endereço (`@ee70`). O mesmo objeto tem o mesmo endereço em todos os
   passos, e é assim que se vê que duas variáveis apontam para a mesma coisa.
3. **Reconhece formas.** Pelo jeito como os objetos se ligam, e **não**
   pelos nomes, o vized percebe que aquilo é uma lista encadeada, uma
   árvore, uma matriz, um grafo... Um objeto com um campo que aponta para
   outro objeto do mesmo tipo é uma lista encadeada, chame-se o campo
   `prox`, `next` ou `zz`.
4. **Desenha e compara.** Cada forma reconhecida ganha um desenho próprio.
   O que não tem forma conhecida aparece como caixas e setas. Por fim, o
   passo é comparado com o anterior para colorir o que acabou de mudar.

---

## Instalação, passo a passo

Você precisa de:

- **Python 3.10 ou mais novo** (confira com `python3 --version`);
- **git**;
- um **terminal com pelo menos 130 colunas** (deixe a janela larga):
  Terminal ou iTerm no macOS, qualquer terminal no Linux, Windows Terminal
  no Windows.

No terminal:

```bash
# 1. baixe o projeto
git clone https://github.com/malu-zinha/data-visualizer.git
cd data-visualizer

# 2. crie um ambiente virtual (uma pasta isolada para as dependências)
python3 -m venv .venv

# 3. ative o ambiente (repita este passo sempre que abrir um terminal novo)
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 4. instale o vized
pip install -e ".[dev]"

# 5. confira
vized --help
```

Se o `vized --help` mostrou a ajuda, está tudo pronto. Para abrir os
exemplos que vêm com o projeto, rode só `vized`.

---

## Primeiro uso: um exemplo completo

### 1. Escreva um programa

Crie um arquivo `meu_programa.py` com uma lista encadeada que recebe
três números, sempre inserindo no início:

```python
class No:
    def __init__(self, valor):
        self.valor = valor
        self.prox = None


def inserir_no_inicio(cabeca, valor):
    novo = No(valor)
    novo.prox = cabeca
    return novo


lista = None
for x in [3, 2, 1]:
    lista = inserir_no_inicio(lista, x)
print("pronto!")
```

Ele é um programa Python comum: não precisa importar nada do vized, e
roda com `python meu_programa.py` também.

### 2. Rode com o vized

```bash
vized meu_programa.py
```

### 3. Entenda a tela

Esta é a tela de verdade no passo 22 de 36: o programa está dentro de
`inserir_no_inicio`, inserindo o 2, e vai executar `novo.prox = cabeca`.

```
 ⭘                                        vized — código Python e memória, passo a passo
 meu_programa.py
╸━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╭─ meu_programa.py · inserir_no_inicio() ──────────────────────────╮╭─ python meu_programa.py ─────────────────────────────────────╮
│    4         self.prox = None                                    ││                                                              │
│    5                                                             ││  lista encadeada · No                                        │
│    6                                                             ││                                                              │
│    7 def inserir_no_inicio(cabeca, valor):                       ││  ┌────┬───┐                                                  │
│    8     novo = No(valor)                                        ││  │ 3  │ ∅ │                                                  │
│ ❱  9     novo.prox = cabeca                                      ││  └────┴───┘                                                  │
│   10     return novo                                             ││   @ee70                                                      │
│   11                                                             ││   prox=None                                                  │
│   12                                                             ││   ▲ lista, cabeca                                            │
│   13 lista = None                                                ││                                                              │
│                                                                  ││  soltos (a cadeia acima não os alcança):                     │
╰───────────────────────────────────────── vai executar a linha 9 ─╯│  ┌────┬───┐                                                  │
╭─ memória ────────────────────────────────────────────────────────╮│  │ 2  │ ∅ │                                                  │
│ pilha de chamadas                                                ││  └────┴───┘                                                  │
│   <module>()  linha 15                                           ││   @f4a0                                                      │
│ ▶   inserir_no_inicio()  linha 9                                 ││   prox=None                                                  │
│                                                                  ││   ▲ novo                                                     │
│ variáveis globais                                                ││                                                              │
│   lista = nó 3 @ee70                                             ││  variáveis globais                                           │
│   x = 2                                                          ││  ┌───────────────────┐                                       │
│                                                                  ││  │ lista  nó 3 @ee70 │                                       │
│ variáveis locais                                                 ││  │ x      2          │                                       │
│   cabeca = nó 3 @ee70                                            ││  └───────────────────┘                                       │
│   valor = 2                                                      ││                                                              │
│   novo = nó 2 @f4a0                                              ││  inserir_no_inicio()                                         │
│                                                                  ││  ┌────────────────────┐                                      │
╰──────────────────────────────────────────────────────────────────╯│  │ cabeca  nó 3 @ee70 │                                      │
╭─ saída ──────────────────────────────────────────────────────────╮│  │ valor   2          │                                      │
│ (nada ainda)                                                     ││                                                              │
╰──────────────────────────────────────────────────────────────────╯╰──────────────────────────────────────────────────────────────╯
 passo 22/36     ❚❚ pausado
 → aba  n próximo  p anterior  space play/pausa  r reinicia  q sair
```

Como ler cada parte:

| Onde | O que mostra |
|---|---|
| **Abas** (topo) | Um programa por aba. Com `vized meu_programa.py` há uma só; com `vized` sem nada, uma por exemplo. |
| **Código** (esquerda, em cima) | O seu arquivo. A linha marcada com `❱` é a que **vai** executar agora, e ainda não executou. O título diz em que função você está. |
| **Memória** (esquerda, no meio) | A **pilha de chamadas**: quem chamou quem, com `▶` na função atual. Embaixo, as variáveis **globais** e as **locais** da função atual. Objetos aparecem como `nó 3 @ee70` (tipo, valor e endereço). |
| **Saída** (esquerda, embaixo) | O que o `print()` já escreveu **até este passo**. |
| **Desenho** (direita) | A memória desenhada. Aqui, a lista encadeada já com o nó 3, e o nó 2 que acabou de ser criado mas ainda está **solto**: nenhum outro nó aponta para ele. Embaixo de cada nó, `▲` indica quais variáveis apontam para ele. Mais abaixo ficam as caixas de variáveis de cada função em aberto. |
| **Barra de status** | Em que passo você está, se está tocando ou pausado, e avisos (programa que terminou com erro, limite de passos). |

Os endereços (`@ee70`) mudam de uma execução para outra, mas ficam fixos
durante a execução. O mesmo endereço significa o mesmo objeto.

### 4. Ande pelo tempo

Aperte `n` para avançar um passo e `p` para voltar. Veja o que acontece
com o desenho:

**Passo 23**: `novo.prox = cabeca` executou. O nó 2 passou a apontar para
o 3, e a seta nova aparece **em verde** no terminal:

```
lista encadeada · No

┌────┬───┐     ┌────┬───┐
│ 2  │ ●─┼────▶│ 3  │ ∅ │
└────┴───┘     └────┴───┘
 @f4a0          @ee70
 prox=@ee70     prox=None
 ▲ novo         ▲ lista, cabeca
```

**Passo 25**: a função retornou e `lista = ...` recebeu o nó 2. Agora é
`lista` que aponta para ele, e a caixa de `inserir_no_inicio()` sumiu,
porque a chamada acabou:

```
lista encadeada · No

┌────┬───┐     ┌────┬───┐
│ 2  │ ●─┼────▶│ 3  │ ∅ │
└────┴───┘     └────┴───┘
 @f4a0          @ee70
 prox=@ee70     prox=None
 ▲ lista

variáveis globais
┌───────────────────┐
│ lista  nó 2 @f4a0 │
│ x      2          │
└───────────────────┘
```

**Passo 36** (o último): a lista ficou 1 → 2 → 3, e o painel de saída
mostra `pronto!`:

```
lista encadeada · No

┌────┬───┐     ┌────┬───┐     ┌────┬───┐
│ 1  │ ●─┼────▶│ 2  │ ●─┼────▶│ 3  │ ∅ │
└────┴───┘     └────┴───┘     └────┴───┘
 @b9b0          @f4a0          @ee70
 prox=@f4a0     prox=@ee70     prox=None
 ▲ lista
```

Repare que em nenhum momento o vized foi avisado de que aquilo era uma
lista encadeada: ele percebeu pelo formato dos objetos.

### 5. Saia

Aperte `q`.

---

## Teclas

| Tecla | O que faz |
|---|---|
| `n` | próximo passo |
| `p` | passo anterior |
| `espaço` | toca a execução sozinha (um passo a cada ~0,5 s); de novo, pausa |
| `r` | volta ao primeiro passo |
| `←` `→` | troca de aba (quando há mais de um programa aberto) |
| `q` | sai |

Se o desenho for maior que o painel da direita, role com o mouse ou o trackpad.

## Cores

| Cor | Significa |
|---|---|
| **verde** | acabou de nascer ou de mudar neste passo: objeto novo, célula alterada, seta religada |
| **amarelo** | seguro por uma chamada ainda em aberto (ex.: o caminho de uma recursão numa árvore); em arrays, as posições apontadas por índices (`▲ j`) |
| **fundo amarelo** | apontado por uma variável da função atual; também o nome da função atual |
| **ciano** | referências (setas, `nó 3 @ee70`) |
| **cinza** | detalhes: endereços, índices, bordas |
| **vermelho** | alerta, ex.: um nó com dois pais no meio de uma rotação |

---

## Usando com os seus programas

```bash
vized caminho/do/programa.py                 # um arquivo seu
vized caminho/do/programa.py --max-passos 500   # muda o limite de passos (padrão: 2000)
vized                                        # abre todos os exemplos, uma aba cada
vized avl                                    # abre só exemplos/avl.py
```

### Dicas para aproveitar melhor

- **Programas pequenos e focados funcionam melhor.** O vized mostra tudo,
  passo a passo: um laço de 10 000 voltas vira milhares de passos.
  Teste o algoritmo com uma entrada pequena, de 5 a 10 elementos.
- **Deixe as entradas fixas no código**, em vez de usar `input()`.
- **Os nomes não importam.** Pode chamar os campos de `prox`, `next`,
  `esquerda` ou como quiser: a forma é reconhecida pelas ligações.
- **O bloco `if __name__ == "__main__":` roda normalmente.**
- **Use `print()` à vontade**: a saída aparece no painel de saída,
  sincronizada com os passos.

### Formas que o vized reconhece

| Forma | Como ele percebe | Desenho |
|---|---|---|
| lista encadeada | objeto com **um** campo que aponta para outro do mesmo tipo | caixas `[valor│●]` ligadas por setas |
| lista duplamente encadeada | **dois** campos assim, e `a.x.y is a` (ida e volta) | caixas com setas `◀───▶` |
| árvore binária | **dois** campos assim, sem volta | árvore com os valores (outros campos entre parênteses, ex.: altura) |
| matriz | lista de listas, todas do mesmo tamanho | grade com índices |
| matriz de adjacência | matriz quadrada só de 0 e 1 | grade com os nomes dos vértices, se houver uma lista deles ao lado |
| lista de adjacência | dicionário `vértice → lista de vértices` | `A → [B] [C]` |
| buckets (tabela hash) | lista de listas de tamanhos diferentes | `[0] ─▶ [ana] ─▶ [leo]` |
| array | lista de números/textos apontada por uma variável | células com índice; variáveis inteiras viram `▲ i` embaixo da posição |
| fila | `collections.deque` apontado por uma variável | células com `frente` e `fim` |
| qualquer outra coisa | — | **caixas e setas**: uma caixa por objeto, setas para as referências |

### Limites (bom saber)

- **`input()` não funciona**: o programa é gravado antes de a tela abrir,
  então não há teclado. O `input()` recebe "fim de entrada" (`EOFError`).
  Troque por um valor fixo.
- **Só as linhas do seu arquivo aparecem passo a passo.** Módulos que ele
  importa rodam normalmente, mas por dentro não são mostrados.
- **Limite de passos**: por padrão, a gravação para em 2000 passos (a
  barra de status avisa). Um `while True` para ali também. Use
  `--max-passos N` para mudar.
- **Erros não perdem nada**: se o programa quebrar, você navega até o
  passo do erro, e a barra de status mostra a mensagem.
- **Objetos da biblioteca padrão** (arquivos abertos, datas, `random`...)
  aparecem pelo texto que o Python mostraria (`datetime.date(2026, 9, 28)`),
  sem os campos internos.
- **Desenhos muito grandes são cortados**: até 60 objetos nas caixas e
  setas, 12 itens por caixa e 30 células por array.
- **Definir uma classe também é executar código**: nos primeiros passos,
  enquanto o Python lê o corpo de uma `class No:`, a pilha mostra `No()`.
- Argumentos de linha de comando para o seu programa (`sys.argv`) ainda
  não são repassados.

---

## Exemplos incluídos

Estão em `exemplos/`. Abra todos com `vized` ou um só pelo nome
(`vized bst`).

| Exemplo | O que observar |
|---|---|
| `bubble` | as trocas no array (em verde) e `▲ passada, j` marcando as posições comparadas |
| `lista_encadeada` | o nó novo nascendo solto e sendo ligado no fim da lista |
| `pilha_fila` | uma pilha sobre lista e uma fila circular sobre vetor, com `inicio` e `fim` dando a volta |
| `bst` | a recursão descendo a árvore: o caminho fica em amarelo |
| `avl` | as rotações: a árvore se parte em pedaços e se remonta |
| `grafo` | a BFS com matriz e lista de adjacência, a `fila` e a `ordem` de visita |
| `hash` | cada chave caindo no seu bucket |
| `turma` | um dicionário de listas de objetos, desenhado como caixas e setas |

---

## Problemas comuns

| Sintoma | Solução |
|---|---|
| `command not found: vized` | Ative o ambiente virtual: `source .venv/bin/activate`. |
| A tela aparece espremida ou cortada | Deixe o terminal mais largo (130 colunas ou mais) ou diminua a fonte. |
| `pasta exemplos/ não encontrada` | Instale com `pip install -e ".[dev]"` a partir da pasta do projeto, ou passe um arquivo: `vized meu_programa.py`. |
| A barra diz "parou no limite de passos" | Use uma entrada menor ou aumente o limite: `--max-passos 5000`. |
| `EOFError` na barra de status | O programa usa `input()`: troque por um valor fixo. |

---

## Para quem vai mexer no código

### Organização

    src/vized/
    ├── cli.py                  # `vized`, `vized arquivo.py`, `vized <exemplo>`
    ├── nucleo/
    │   ├── rastreador.py       # sys.settrace: um Passo por linha (pilha + variáveis + heap)
    │   ├── heap.py             # memória → {endereço: descrição rasa} (JSON puro)
    │   ├── vista.py            # heap → objetos leves (para desenhar com n.esq)
    │   ├── diferenca.py        # o que mudou entre dois passos (cores)
    │   ├── canvas.py           # grade de caracteres com tags semânticas
    │   ├── cenario.py          # uma execução gravada = uma aba
    │   └── memoria.py          # textos do painel de memória
    ├── deteccao/
    │   └── formas.py           # regras de forma, olhando só o grafo dos objetos
    ├── renderizadores/
    │   ├── automatico.py       # escolhe o desenho de cada forma detectada
    │   ├── generico.py         # qualquer memória: caixas e setas
    │   └── arvore.py, lista.py, array.py, sequencia.py, grafo.py, buckets.py
    └── interface/
        └── app_textual.py      # a tela (feita com textual)

O fluxo é `rastrear → achatar → detectar forma → desenhar → destacar`.
O desenho nunca escolhe cor: ele marca trechos com tags (`novo`,
`destaque`, `foco`...), e a interface traduz cada tag em estilo.

### Testes

    pytest                                             # tudo
    VIZED_ATUALIZAR=1 pytest tests/test_desenhos.py    # regrava snapshots (só após mudança intencional)

- `tests/test_desenhos.py`: cada exemplo, pelo fluxo completo, desenha igual
  às snapshots em `tests/snapshots/`.
- `tests/test_codigo.py`: os exemplos funcionam (independe do visualizador).
- `tests/test_cli.py`: `vized arquivo.py` (globais, limite, erros, saída, interface).
- `tests/test_heap.py`: a "fotografia" da memória (ciclos, sets, slots, JSON).
- `tests/test_generico.py`: caixas e setas para qualquer programa
  (+ snapshots em `tests/snapshots/generico/`).
- `tests/test_formas.py`: reconhecimento de cada forma.
- `tests/test_diferenca.py`: as cores de "o que mudou".

Para acrescentar um exemplo, crie `exemplos/<nome>.py`. Ele vira uma aba do
`vized` e entra nos testes de snapshot (a primeira execução do `pytest`
grava as snapshots dele).

### Página web

    pip install -e ".[web]"
    python web/gerar_pagina.py        # Linux/macOS (usa o módulo pty)

Roda o app num terminal virtual, grava a tela a cada passo de cada exemplo
e gera `web/passo-a-passo.html`, que abre em qualquer navegador.

### Histórico

O caminho de "desenhos feitos à mão para cada estrutura" até "qualquer
código" está em [`docs/ROADMAP.md`](docs/ROADMAP.md): etapas 1 a 6, cada
uma com uma tag `etapa-N` no git. `exemplos/comparacao-ferramentas/`
guarda a primeira versão, comparando ANSI, rich e curses.
