"""Main application entry point."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class VespersApp(App):
    """A Textual application for Vespers."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()


def main():
    """Run the Vespers application."""
    app = VespersApp()
    app.run()


if __name__ == "__main__":
    main()
