"""Main application entry point."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, TabbedContent, TabPane


class VespersApp(App):
    """A Textual application for Vespers."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield Label("Dashboard content")
            with TabPane("Task", id="task"):
                yield Label("Task content")
        yield Footer()


def main():
    """Run the Vespers application."""
    app = VespersApp()
    app.run()


if __name__ == "__main__":
    main()
