"""Permite rodar com `python -m vized` (ou `vized`, se instalado)."""
from vized.interface.app_textual import VisualizadorApp


def main():
    VisualizadorApp().run()      # abre a interface no terminal


if __name__ == "__main__":
    main()
