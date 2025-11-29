"""Dashboard widgets for the Vespers application."""

import re
from typing import Optional

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
        readability=None,
        dialogue_mix=None,
        lexical_variety=None,
        cadence=None,
        chapter_edits=None,
        **kwargs,
    ):
        """Initialize the dashboard chart.

        Args:
            completed_tasks: List of dicts with 'date' and 'count' keys
            words_written: List of dicts with 'date' and 'words' keys
            outline: List of parent outline items
            recent_activity: List of dicts describing recent actions
            readability: Dict containing readability metrics
            dialogue_mix: Dict summarizing amount of dialogue vs narration
            lexical_variety: Dict with vocabulary richness metrics
            cadence: Dict describing sentence/paragraph cadence metrics
            chapter_edits: Dict with per-chapter edit activity data
        """
        super().__init__(**kwargs)
        self.completed_tasks = completed_tasks or []
        self.words_written = words_written or []
        self.outline = outline or []
        self.recent_activity = recent_activity or []
        self.readability = readability or {}
        self.dialogue_mix = dialogue_mix or {}
        self.lexical_variety = lexical_variety or {}
        self.cadence = cadence or {}
        self.chapter_edits = chapter_edits or {}
        self._dialogue_bar_width = 28
        self._readability_bar_width = 28
        self._readability_max_grade = 20.0

    def render(self) -> Panel:
        """Render the dashboard chart as a Rich Panel."""
        has_tasks = bool(self.completed_tasks)
        has_words = bool(self.words_written)
        has_outline = bool(self.outline)
        has_activity = bool(self.recent_activity)
        readability_entries = (
            self.readability.get("entries") if isinstance(self.readability, dict) else None
        )
        has_readability = bool(readability_entries)
        dialogue_entries = (
            self.dialogue_mix.get("entries") if isinstance(self.dialogue_mix, dict) else None
        )
        has_dialogue = bool(dialogue_entries)
        lexical_entries = (
            self.lexical_variety.get("entries") if isinstance(self.lexical_variety, dict) else None
        )
        has_lexical = bool(lexical_entries)
        cadence_entries = self.cadence.get("entries") if isinstance(self.cadence, dict) else None
        has_cadence = bool(cadence_entries)
        chapter_entries = (
            self.chapter_edits.get("chapters") if isinstance(self.chapter_edits, dict) else None
        )
        has_chapter_edits = bool(chapter_entries)

        if not (
            has_tasks
            or has_words
            or has_outline
            or has_activity
            or has_readability
            or has_dialogue
            or has_lexical
            or has_cadence
            or has_chapter_edits
        ):
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
        readability_panel = self._build_readability_panel()
        dialogue_panel = self._build_dialogue_panel()
        lexical_panel = self._build_lexical_panel()
        cadence_panel = self._build_cadence_panel()
        chapter_panel = self._build_chapter_edits_panel()

        left_column = Group(task_panel, Text(""), words_panel, Text(""), activity_panel)
        middle_column = Group(chapter_panel, Text(""), outline_panel)
        right_column = Group(
            readability_panel,
            Text(""),
            dialogue_panel,
            Text(""),
            lexical_panel,
            Text(""),
            cadence_panel,
        )

        grid = Table.grid(padding=(0, 1))
        for _ in range(3):
            grid.add_column(width=80, justify="left")
        grid.add_row(left_column, middle_column, right_column)

        return Panel(
            grid,
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
                Text("Units Completed per day", style="dim"),
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
                Text("✍️  Words Written", style="bold #00bfff"),
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
            parent_titles = [parent.get("title", "Untitled") for parent in self.outline[:3]]
            parent_summary = (
                Text(f"Parents: {', '.join(parent_titles)}", style="dim")
                if parent_titles
                else Text("")
            )
            body = Group(
                Text("🗂  Outline Progress", style="bold #7fff00"),
                Text("Tracking parent storyline progress", style="dim"),
                parent_summary,
                Text(""),
                self._build_outline_table(),
            )
        return Panel(body, title="Outline", border_style="#7fff00", padding=(1, 1))

    def _build_activity_panel(self) -> Panel:
        """Create the recent activity panel content."""
        if not self.recent_activity:
            body = Text("No recent activity logged.", style="italic dim")
        else:
            entry_texts = []
            for entry in self.recent_activity[:6]:
                description = entry.get("description", "Activity")
                ago = entry.get("ago", "just now")
                entry_texts.append(Text(f"• {description}", overflow="fold"))
                quoted_subjects = re.findall(r"'([^']+)'", description)
                for subject in quoted_subjects:
                    entry_texts.append(Text(f"   {subject}", style="dim"))
                entry_texts.append(Text(f"   ({ago})", style="dim"))
            body = Group(
                Text("🔔 Recent Activity", style="bold #ba55d3"),
                *entry_texts,
            )

        return Panel(body, title="Recent", border_style="#ba55d3", padding=(1, 1))

    def _build_readability_panel(self) -> Panel:
        """Create the readability blend panel content."""
        data = self.readability if isinstance(self.readability, dict) else {}
        entries = data.get("entries", []) if data else []
        target_grade = data.get("target_grade", "—") if data else "—"
        target_min_grade, target_max_grade = self._parse_readability_target_range(target_grade)

        if not entries:
            body = Text("No readability metrics yet.", style="italic dim")
        else:
            table = Table(expand=True, pad_edge=False, show_edge=False)
            table.add_column("Day", style="bold #9370db")
            table.add_column("Blend", justify="left")
            table.add_column("Avg Sent", justify="right")
            table.add_column("Sent/Para", justify="right")

            top_indicator, bottom_indicator = self._build_readability_target_lines(
                target_min_grade, target_max_grade
            )
            if top_indicator:
                table.add_row("", top_indicator, "", "")

            for entry in entries[:5]:
                label = entry.get("label", "—")
                fk_grade = entry.get("fk_grade")
                avg_sentence_length = entry.get("avg_sentence_length")
                sentences_per_paragraph = entry.get("sentences_per_paragraph")
                bar = self._build_readability_bar(fk_grade).copy()
                if isinstance(fk_grade, (int, float)):
                    bar.append(f" {fk_grade:.1f}", style="bold white")
                else:
                    bar.append(" —", style="dim")
                table.add_row(
                    label,
                    bar,
                    f"{avg_sentence_length}" if avg_sentence_length is not None else "—",
                    f"{sentences_per_paragraph}" if sentences_per_paragraph is not None else "—",
                )

            if bottom_indicator:
                table.add_row("", bottom_indicator, "", "")

            arrow_annotations: list[str] = []
            if target_max_grade is not None:
                arrow_annotations.append(f"↓ high {target_max_grade:g}")
            if target_min_grade is not None:
                arrow_annotations.append(f"↑ low {target_min_grade:g}")
            target_summary = " • ".join([f"Target F-K grade: {target_grade}", *arrow_annotations])

            body = Group(
                Text("📚 Readability Blend", style="bold #9370db"),
                Text(target_summary, style="dim"),
                Text(""),
                table,
            )

        return Panel(body, title="Readability", border_style="#9370db", padding=(1, 1))

    def _build_dialogue_panel(self) -> Panel:
        """Create the dialogue versus narration panel content."""
        data = self.dialogue_mix if isinstance(self.dialogue_mix, dict) else {}
        entries = data.get("entries", []) if data else []
        target_ratio = data.get("target_ratio", "—") if data else "—"
        target_dialogue, target_narration = self._parse_target_mix(target_ratio)

        if not entries:
            body = Text("No dialogue mix data yet.", style="italic dim")
        else:
            table = Table.grid(padding=(0, 1))
            table.add_column("Segment", style="bold #ffa07a", ratio=1)
            table.add_column("Mix", justify="left", ratio=3)
            table.add_column("Pct", justify="right")

            top_indicator, bottom_indicator = self._build_dialogue_target_lines(target_dialogue)
            if top_indicator:
                table.add_row("", top_indicator, "")

            for entry in entries[:5]:
                label = entry.get("label", "—")
                dialogue_pct = entry.get("dialogue_percent")
                narration_pct = entry.get("narration_percent")
                bar = self._build_dialogue_bar(
                    dialogue_pct,
                    narration_pct,
                    target_dialogue,
                )
                has_values = isinstance(dialogue_pct, (int, float)) and isinstance(
                    narration_pct, (int, float)
                )
                pct_text = Text(
                    (f"{dialogue_pct:.0f}% / {narration_pct:.0f}%" if has_values else "—"),
                    style="dim",
                )
                table.add_row(label, bar, pct_text)

            if bottom_indicator:
                table.add_row("", bottom_indicator, "")

            arrow_annotations: list[str] = []
            if isinstance(target_dialogue, (int, float)):
                arrow_annotations.append(f"↓ dial {target_dialogue:g}%")
            if isinstance(target_narration, (int, float)):
                arrow_annotations.append(f"↑ narr {target_narration:g}%")
            target_summary = " • ".join([f"Target mix: {target_ratio}", *arrow_annotations])

            body = Group(
                Text("🗣️ Dialogue vs Narration", style="bold #ffa07a"),
                Text(target_summary, style="dim"),
                Text(""),
                table,
            )

        return Panel(body, title="Dialogue Mix", border_style="#ffa07a", padding=(1, 1))

    def _parse_readability_target_range(
        self, target_grade: Optional[str]
    ) -> tuple[Optional[float], Optional[float]]:
        """Extract lower/upper readability target grades from text."""
        if not target_grade or not isinstance(target_grade, str):
            return None, None

        numbers = [float(match) for match in re.findall(r"(\d+(?:\.\d+)?)", target_grade)]
        if not numbers:
            return None, None

        min_value = min(numbers)
        max_value = max(numbers)
        return min_value, max_value

    def _build_readability_bar(self, fk_grade: Optional[float]) -> Text:
        """Render a horizontal bar to show F-K grade."""
        width = self._readability_bar_width
        max_grade = self._readability_max_grade

        if not isinstance(fk_grade, (int, float)):
            return Text("—" * width, style="dim")

        grade = max(0.0, min(max_grade, float(fk_grade)))
        filled = round((grade / max_grade) * width)

        bar = Text()
        for idx in range(width):
            if idx < filled:
                bar.append(Text("▄", style="bold #9370db"))
            else:
                bar.append(Text("▁", style="grey35"))
        return bar

    def _build_readability_target_lines(
        self,
        min_grade: Optional[float],
        max_grade: Optional[float],
    ) -> tuple[Optional[Text], Optional[Text]]:
        """Create top/bottom arrow markers aligned with the readability bars."""

        def _line(value: Optional[float], symbol: str) -> Optional[Text]:
            index = self._grade_to_bar_index(value)
            if index is None:
                return None
            chars = [" "] * self._readability_bar_width
            chars[index] = symbol
            return Text("".join(chars), style="bold white")

        return _line(max_grade, "↓"), _line(min_grade, "↑")

    def _grade_to_bar_index(self, value: Optional[float]) -> Optional[int]:
        """Convert a grade value to a bar index within readability bars."""
        if value is None or not isinstance(value, (int, float)):
            return None

        width = self._readability_bar_width
        max_grade = self._readability_max_grade
        grade = max(0.0, min(max_grade, float(value)))
        if width <= 1:
            return 0
        return max(0, min(width - 1, round((grade / max_grade) * (width - 1))))

    def _parse_target_mix(
        self, target_ratio: Optional[str]
    ) -> tuple[Optional[float], Optional[float]]:
        """Extract target dialogue/narration percentages from text."""
        if not target_ratio or not isinstance(target_ratio, str):
            return None, None

        numbers = re.findall(r"(\d+(?:\.\d+)?)", target_ratio)
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
        if numbers:
            value = float(numbers[0])
            return value, 100 - value
        return None, None

    def _build_dialogue_bar(
        self,
        dialogue_pct: Optional[float],
        narration_pct: Optional[float],
        target_dialogue: Optional[float],
    ) -> Text:
        """Render a horizontal bar showing dialogue vs narration."""
        bar_width = self._dialogue_bar_width

        if not isinstance(dialogue_pct, (int, float)) or not isinstance(
            narration_pct, (int, float)
        ):
            return Text("—" * bar_width, style="dim")

        dialogue_pct = max(0.0, min(100.0, float(dialogue_pct)))
        dialogue_length = round((dialogue_pct / 100) * bar_width)

        bar_line = Text()
        for idx in range(bar_width):
            if idx < dialogue_length:
                bar_line.append(Text("▄", style="bold #ffa07a"))
            else:
                bar_line.append(Text("▁", style="grey35"))

        return bar_line

    def _build_dialogue_target_lines(
        self, target_dialogue: Optional[float]
    ) -> tuple[Optional[Text], Optional[Text]]:
        """Create shared arrow indicators for the dialogue bar column."""
        if not isinstance(target_dialogue, (int, float)):
            return None, None

        bar_width = self._dialogue_bar_width
        target_ratio = max(0.0, min(100.0, float(target_dialogue)))
        target_idx = max(0, min(bar_width - 1, round((target_ratio / 100) * (bar_width - 1))))

        def _line(symbol: str) -> Text:
            chars = [" "] * bar_width
            chars[target_idx] = symbol
            return Text("".join(chars), style="bold white")

        return _line("↓"), _line("↑")

    def _build_lexical_panel(self) -> Panel:
        """Create the lexical variety panel content."""
        data = self.lexical_variety if isinstance(self.lexical_variety, dict) else {}
        entries = data.get("entries", []) if data else []
        target_ttr = data.get("target_ttr")
        target_unique = data.get("target_unique_words")

        if not entries:
            body = Text("No lexical data yet.", style="italic dim")
        else:
            table = Table(expand=True, pad_edge=False, show_edge=False)
            table.add_column("Segment", style="bold #20b2aa")
            table.add_column("TTR", justify="right")
            table.add_column("Unique", justify="right")
            table.add_column("Rare", justify="right")

            for entry in entries[:5]:
                label = entry.get("label", "—")
                ttr = entry.get("ttr")
                unique_words = entry.get("unique_words")
                rare_words = entry.get("rare_words")
                table.add_row(
                    label,
                    f"{ttr:.2f}" if isinstance(ttr, (int, float)) else "—",
                    f"{unique_words:,}" if isinstance(unique_words, (int, float)) else "—",
                    f"{rare_words:,}" if isinstance(rare_words, (int, float)) else "—",
                )

            targets_text = []
            if isinstance(target_ttr, (int, float)):
                targets_text.append(f"Target TTR: {target_ttr:.2f}")
            if isinstance(target_unique, (int, float)):
                targets_text.append(f"Unique goal: {target_unique:,}")

            body = Group(
                Text("🔤 Lexical Variety", style="bold #20b2aa"),
                Text(" • ".join(targets_text) if targets_text else "", style="dim"),
                Text(""),
                table,
            )

        return Panel(body, title="Lexical", border_style="#20b2aa", padding=(1, 1))

    def _build_cadence_panel(self) -> Panel:
        """Create the sentence and paragraph cadence panel content."""
        data = self.cadence if isinstance(self.cadence, dict) else {}
        entries = data.get("entries", []) if data else []
        target_sentence_length = data.get("target_sentence_length")
        target_sentences_per_paragraph = data.get("target_sentences_per_paragraph")

        if not entries:
            body = Text("No cadence data yet.", style="italic dim")
        else:
            table = Table(expand=True, pad_edge=False, show_edge=False)
            table.add_column("Segment", style="bold #ffd700")
            table.add_column("Sent Len", justify="right")
            table.add_column("Sent/Para", justify="right")
            table.add_column("Para/Scene", justify="right")

            for entry in entries[:5]:
                label = entry.get("label", "—")
                avg_sentence_length = entry.get("avg_sentence_length")
                sentences_per_paragraph = entry.get("sentences_per_paragraph")
                paragraphs_per_scene = entry.get("paragraphs_per_scene")
                table.add_row(
                    label,
                    f"{avg_sentence_length}" if avg_sentence_length is not None else "—",
                    f"{sentences_per_paragraph}" if sentences_per_paragraph is not None else "—",
                    f"{paragraphs_per_scene}" if paragraphs_per_scene is not None else "—",
                )

            summary_bits = []
            if isinstance(target_sentence_length, (int, float)):
                summary_bits.append(f"Target sentence length: {target_sentence_length}")
            if isinstance(target_sentences_per_paragraph, (int, float)):
                summary_bits.append(f"Sentences/paragraph goal: {target_sentences_per_paragraph}")

            body = Group(
                Text("⏱️ Sentence & Paragraph Cadence", style="bold #ffd700"),
                Text(" • ".join(summary_bits) if summary_bits else "", style="dim"),
                Text(""),
                table,
            )

        return Panel(body, title="Cadence", border_style="#ffd700", padding=(1, 1))

    def _build_chapter_edits_panel(self) -> Panel:
        """Create the chapter edits and file activity panel."""
        data = self.chapter_edits if isinstance(self.chapter_edits, dict) else {}
        chapters = data.get("chapters", []) if data else []
        touch_window = data.get("target_touch_window")

        if not chapters:
            body = Text("No chapter edit history yet.", style="italic dim")
        else:
            sorted_chapters = sorted(
                chapters,
                key=lambda entry: entry.get("edit_sessions", 0),
                reverse=True,
            )
            table = Table(expand=True, pad_edge=False, show_edge=False)
            table.add_column("Chapter", style="bold #ff69b4")
            table.add_column("+Add", justify="right")
            table.add_column("-Del", justify="right")
            table.add_column("Sessions", justify="right")
            table.add_column("Net", justify="right")

            for entry in sorted_chapters[:6]:
                name = entry.get("name", "—")
                additions = entry.get("additions", 0)
                deletions = entry.get("deletions", 0)
                sessions = entry.get("edit_sessions", 0)
                net = None
                if isinstance(additions, (int, float)) and isinstance(deletions, (int, float)):
                    net = additions - deletions
                table.add_row(
                    name,
                    f"{additions:,}" if isinstance(additions, (int, float)) else "—",
                    f"{deletions:,}" if isinstance(deletions, (int, float)) else "—",
                    f"{sessions}" if isinstance(sessions, (int, float)) else "—",
                    f"{net:+,}" if isinstance(net, (int, float)) else "—",
                )

            most = sorted_chapters[0] if sorted_chapters else None
            least_entry = sorted_chapters[-1] if sorted_chapters else None

            summary_bits: list[str] = []
            if most:
                summary_bits.append(
                    "Most edited:"
                    f" {most.get('name', '—')}"
                    f" ({most.get('edit_sessions', 0)} sessions)"
                )
            if least_entry and least_entry is not most:
                summary_bits.append(
                    "Needs love:"
                    f" {least_entry.get('name', '—')}"
                    f" ({least_entry.get('edit_sessions', 0)} session(s))"
                )
            if touch_window:
                summary_bits.append(touch_window)

            body = Group(
                Text("🗃️ Chapter Edit Pulse", style="bold #ff69b4"),
                Text(" • ".join(summary_bits), style="dim"),
                Text(""),
                table,
            )

        return Panel(body, title="Chapter Edits", border_style="#ff69b4", padding=(1, 1))

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
