"""Dashboard widgets for the Vespers application."""

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static


class DashboardChart(Static):
    """A widget that displays productivity metrics for the dashboard."""

    DEFAULT_CSS = """
    DashboardChart {
        width: 100%;
        min-height: 12;
        padding: 1;
    }
    """

    def __init__(
        self,
        completed_tasks=None,
        words_written=None,
        outline=None,
        recent_activity=None,
        **kwargs,
    ):
        """Initialize the dashboard chart.

        Args:
            completed_tasks: List of dicts with 'date' and 'count' keys
            words_written: List of dicts with 'date' and 'words' keys
            outline: List of parent outline items
            recent_activity: List of dicts describing recent actions
        """
        super().__init__(**kwargs)
        self.completed_tasks = completed_tasks or []
        self.words_written = words_written or []
        self.outline = outline or []
        self.recent_activity = recent_activity or []

    def render(self) -> Panel:
        """Render the dashboard chart as a Rich Panel."""
        has_tasks = bool(self.completed_tasks)
        has_words = bool(self.words_written)
        has_outline = bool(self.outline)
        has_activity = bool(self.recent_activity)

        if not (has_tasks or has_words or has_outline or has_activity):
            message = Text("No productivity data yet.", style="italic dim")
            return Panel(
                message,
                title="Productivity",
                border_style="cyan",
                padding=(1, 2),
            )

        task_panel = self._build_task_panel()
        outline_panel = self._build_outline_panel()
        words_panel = self._build_words_panel()
        activity_panel = self._build_activity_panel()

        left_column = Group(task_panel, Text(""), words_panel)

        right_column = Group(outline_panel, Text(""), activity_panel)

        columns = Columns(
            [left_column, right_column],
            expand=True,
            equal=True,
        )

        return Panel(
            columns,
            title="Progress Overview",
            border_style="cyan",
            padding=(1, 2),
        )

    def _build_task_panel(self) -> Panel:
        """Create the tasks panel content."""
        if not self.completed_tasks:
            body = Text("No tasks have been completed yet.", style="italic dim")
        else:
            total_tasks = sum(task["count"] for task in self.completed_tasks)
            body = Group(
                Text("🍅 Tasks Completed", style="bold #ff8c00"),
                Text(f"Total tasks completed: {total_tasks}", style="bold white"),
                Text(""),
                self._build_tasks_table(),
            )
        return Panel(body, title="Tasks", border_style="#ff8c00", padding=(1, 1))

    def _build_words_panel(self) -> Panel:
        """Create the words-written panel content."""
        if not self.words_written:
            body = Text("No writing data recorded yet.", style="italic dim")
        else:
            total_words = sum(entry["words"] for entry in self.words_written)
            body = Group(
                Text("✍️ Words Written", style="bold #00bfff"),
                Text(f"Total words written: {total_words:,}", style="bold white"),
                Text(""),
                self._build_words_table(),
            )
        return Panel(body, title="Words", border_style="#00bfff", padding=(1, 1))

    def _build_outline_panel(self) -> Panel:
        """Create the outline progress panel content."""
        if not self.outline:
            body = Text("No outline progress recorded yet.", style="italic dim")
        else:
            body = Group(
                Text("🗂 Outline Progress", style="bold #7fff00"),
                Text("Tracking parent storyline progress", style="dim"),
                Text(""),
                self._build_outline_table(),
            )
        return Panel(body, title="Outline", border_style="#7fff00", padding=(1, 1))

    def _build_activity_panel(self) -> Panel:
        """Create the recent activity panel content."""
        if not self.recent_activity:
            body = Text("No recent activity logged.", style="italic dim")
        else:
            entries = []
            for entry in self.recent_activity[:6]:
                description = entry.get("description", "Activity")
                ago = entry.get("ago", "just now")
                entries.append(f"• {description} ({ago})")
            body = Group(
                Text("🔔 Recent Activity", style="bold #ba55d3"),
                Text("\n".join(entries)),
            )

        return Panel(body, title="Recent", border_style="#ba55d3", padding=(1, 1))

    def _build_tasks_table(self) -> Table:
        """Create a Rich table showing daily task counts."""
        table = Table(expand=True, pad_edge=False, show_edge=False)
        table.add_column("Date", style="bold #ff8c00", justify="center")
        table.add_column("Tasks", justify="right")
        table.add_column("Units Completed", justify="left")

        for task in self.completed_tasks:
            date = task["date"]
            count = task["count"]
            units = self._build_task_units(count)
            table.add_row(date, str(count), units)

        return table

    def _build_words_table(self) -> Table:
        """Create a Rich table showing daily words written."""
        table = Table(expand=True, pad_edge=False, show_edge=False)
        table.add_column("Date", style="bold #00bfff", justify="center")
        table.add_column("Words", justify="right")
        table.add_column("Progress", justify="left")

        for entry in self.words_written:
            date = entry["date"]
            words = entry["words"]
            bar = self._build_word_boxes(words)

            table.add_row(date, f"{words:,}", bar)
        return table

    def _build_outline_table(self) -> Table:
        """Create a table summarizing parent outline progress."""
        table = Table(expand=True, pad_edge=False, show_edge=False)
        table.add_column("Parent", style="bold #7fff00")
        table.add_column("Total", justify="right")
        table.add_column("Done", justify="right")
        table.add_column("Progress", justify="left")

        for parent in self.outline[:15]:
            children = parent.get("children", [])
            total, completed = self._count_outline_children(children)
            progress_boxes = self._build_progress_boxes(total, completed)

            table.add_row(
                parent.get("title", "Untitled"),
                str(total),
                str(completed),
                progress_boxes,
            )
        return table

    def _count_outline_children(self, nodes: list[dict], depth: int = 1) -> tuple[int, int]:
        """Count total/completed tasks within outline nodes up to 3 levels."""
        total = 0
        completed = 0

        if depth > 3:
            return total, completed

        for node in nodes:
            total += 1
            if node.get("completed"):
                completed += 1
            child_nodes = node.get("children", [])
            if child_nodes:
                sub_total, sub_completed = self._count_outline_children(child_nodes, depth + 1)
                total += sub_total
                completed += sub_completed
        return total, completed

    def _build_progress_boxes(self, total: int, completed: int) -> Text:
        """Render progress boxes with completed in green and remaining in gray."""
        if total <= 0:
            return Text("—", style="dim")

        boxes: list[Text] = []
        for _ in range(max(0, min(completed, total))):
            boxes.append(Text("■", style="bold #7fff00"))
        for _ in range(max(0, total - completed)):
            boxes.append(Text("·", style="grey50"))

        # Insert thin spaces between boxes for readability while keeping alignment consistent
        progress = Text()
        for idx, box in enumerate(boxes):
            if idx:
                progress.append(" ")
            progress.append(box)
        return progress

    def _build_word_boxes(self, words: int) -> Text:
        """Render goal boxes (20 per day, orange for completed, gray for remaining)."""
        goal_boxes = 20
        words_per_box = 100
        completed_boxes = min(goal_boxes, max(0, words // words_per_box))

        progress = Text()
        for idx in range(goal_boxes):
            if idx:
                progress.append(" ")
            if idx < completed_boxes:
                progress.append(Text("■", style="bold #00bfff"))
            else:
                progress.append(Text("·", style="grey50"))

        if words > goal_boxes * words_per_box:
            progress.append(Text(" +", style="bold #00bfff"))

        return progress

    def _build_task_units(self, count: int) -> Text:
        """Render task units as orange boxes up to 16 with remaining as center dots."""
        total_units = 16
        completed_units = min(total_units, max(0, int(count)))

        progress = Text()
        for idx in range(total_units):
            if idx:
                progress.append(" ")
            if idx < completed_units:
                progress.append(Text("■", style="bold #ff8c00"))
            else:
                progress.append(Text("·", style="grey50"))

        if count > total_units:
            progress.append(Text(" +", style="bold #ff8c00"))

        return progress
