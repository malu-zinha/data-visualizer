"""Interface textual: código executando à esquerda, estrutura à direita.

Uso:
    python -m vized
Teclas: ← → estrutura · n/p próximo/anterior · espaço play/pausa · r reinicia · q sai
"""
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Static, Tab, Tabs

from vized.estruturas import CENARIOS
from vized.nucleo.memoria import resumo
from vized.nucleo.rastreador import fonte

# Tags do desenho.py → estilos rich (inclui "foco": variável do frame atual)
ESTILOS = {
    "normal": "", "titulo": "bold", "destaque": "bold yellow",
    "novo": "bold green", "ok": "bright_blue", "fronteira": "magenta",
    "ponteiro": "cyan", "fraco": "bright_black", "alerta": "bold red",
    "foco": "bold black on yellow",
}


def para_text(canvas):
    """Canvas → rich.Text, trecho a trecho com o estilo de cada tag."""
    texto = Text(no_wrap=True)
    for i, segmentos in enumerate(canvas.linhas()):
        if i:
            texto.append("\n")
        for pedaco, tag in segmentos:
            texto.append(pedaco, style=ESTILOS[tag])
    return texto


class VisualizadorApp(App):
    TITLE = "Estruturas de dados"
    SUB_TITLE = "código e memória, passo a passo"
    CSS = """
    #corpo { height: 1fr; }
    #lateral { width: 68; }
    #codigo {
        height: 1fr;
        border: round $accent;
        border-title-color: $accent;
        padding: 0 1;
    }
    #memoria {
        height: auto;
        max-height: 16;
        border: round $secondary;
        border-title-color: $secondary;
        padding: 0 1;
    }
    #palco { border: round $primary; border-title-color: $primary; padding: 1 2; }
    #desenho { width: auto; }
    #status { height: 1; padding: 0 1; background: $boost; }
    """
    BINDINGS = [
        Binding("right", "estrutura(1)", "estrutura", priority=True),
        Binding("left", "estrutura(-1)", "", show=False, priority=True),
        Binding("n", "passo(1)", "próximo"),
        Binding("p", "passo(-1)", "anterior"),
        Binding("space", "play", "play/pausa"),
        Binding("r", "reiniciar", "reinicia"),
        Binding("q", "quit", "sair"),
    ]

    def __init__(self):
        super().__init__()
        self.cenarios = CENARIOS
        for c in self.cenarios:
            _ = c.passos                         # grava as linhas do tempo antes de abrir
        self.atual = 0                           # cenário (aba) ativo
        self.indice = 0                          # passo dentro da linha do tempo
        self.tocando = False                     # modo play ligado?

    def compose(self) -> ComposeResult:
        yield Header()
        yield Tabs(*[Tab(c.nome, id=f"c{i}") for i, c in enumerate(self.cenarios)],
                   id="abas")
        with Horizontal(id="corpo"):
            with Vertical(id="lateral"):
                yield Static(id="codigo")        # função atual com a linha destacada
                yield Static(id="memoria")       # pilha de chamadas + variáveis
            with ScrollableContainer(id="palco"):
                yield Static(id="desenho")       # a estrutura naquele instante
        yield Static(id="status")
        yield Footer()

    def on_mount(self):
        # timer do modo play: começa pausado e chama avancar() a cada 0,45 s
        self.timer = self.set_interval(0.45, self.avancar, pause=True)
        self.redesenhar()

    # ── troca de aba ──────────────────────────────────────────────────────
    def on_tabs_tab_activated(self, evento: Tabs.TabActivated):
        self.atual = int(evento.tab.id[1:])      # "c3" → 3
        self.indice = 0
        self.pausar()
        self.redesenhar()

    def action_estrutura(self, delta):
        proximo = (self.atual + delta) % len(self.cenarios)
        self.query_one(Tabs).active = f"c{proximo}"   # dispara on_tabs_tab_activated

    # ── navegação no tempo ───────────────────────────────────────────────
    def action_passo(self, delta):
        self.pausar()
        self.mover(delta)

    def mover(self, delta):
        ultimo = len(self.cenarios[self.atual].passos) - 1
        self.indice = max(0, min(ultimo, self.indice + delta))   # não sai da linha do tempo
        self.redesenhar()

    def action_play(self):
        if self.tocando:
            self.pausar()
        else:
            if self.indice == len(self.cenarios[self.atual].passos) - 1:
                self.indice = 0                   # no fim, play recomeça
            self.tocando = True
            self.timer.resume()
        self.redesenhar()

    def pausar(self):
        self.tocando = False
        if hasattr(self, "timer"):
            self.timer.pause()

    def avancar(self):
        if self.indice >= len(self.cenarios[self.atual].passos) - 1:
            self.pausar()                         # chegou ao fim da linha do tempo
            self.redesenhar()
        else:
            self.mover(1)

    def action_reiniciar(self):
        self.pausar()
        self.indice = 0
        self.redesenhar()

    # ── desenho das áreas ────────────────────────────────────────────────
    def redesenhar(self):
        cenario = self.cenarios[self.atual]
        passo = cenario.passos[self.indice]
        topo = passo.topo

        # 1) código: só a função no topo da pilha, com a linha atual destacada
        linhas, primeira = fonte(topo.codigo)
        codigo = self.query_one("#codigo", Static)
        codigo.update(Syntax("".join(linhas), "python", theme="monokai",
                             line_numbers=True, start_line=primeira,
                             highlight_lines={topo.linha}, background_color="default"))
        codigo.border_title = f"{topo.funcao}()"
        codigo.border_subtitle = (f"retornando na linha {topo.linha}"
                                  if passo.evento == "return"
                                  else f"vai executar a linha {topo.linha}")

        # 2) memória: pilha de chamadas (base → topo) e variáveis do topo
        mem = Text(no_wrap=True, overflow="ellipsis")
        mem.append("pilha de chamadas\n", style="bold")
        for k, q in enumerate(passo.quadros):
            no_topo = k == len(passo.quadros) - 1
            mem.append(f"{'▶ ' if no_topo else '  '}{'  ' * k}{q.funcao}()",
                       style="bold yellow" if no_topo else "")
            mem.append(f"  linha {q.linha}\n", style="bright_black")
        mem.append("\nvariáveis locais\n", style="bold")
        for nome, valor in topo.locais.items():
            mem.append(f"  {nome}", style="bold cyan")
            mem.append(f" = {resumo(valor, passo)}\n")
        if passo.evento == "return":
            mem.append("  retorna", style="bold green")
            mem.append(f" {resumo(passo.retorno, passo)}\n")
        memoria = self.query_one("#memoria", Static)
        memoria.update(mem)
        memoria.border_title = "memória"

        # 3) estrutura, desenhada a partir da cópia daquele instante
        self.query_one("#desenho", Static).update(para_text(cenario.desenhar(passo)))
        self.query_one("#palco").border_title = cenario.operacao

        # 4) barra de status
        estado = "▶ tocando" if self.tocando else "❚❚ pausado"
        self.query_one("#status", Static).update(
            f"passo {self.indice + 1}/{len(cenario.passos)}     {estado}")
