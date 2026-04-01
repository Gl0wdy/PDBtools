import asyncio
import csv
import json
import os
import traceback
import random
from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from account import AccountManager
from parser import PDBParser

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")
BOARD_DIR    = os.path.join(BASE_DIR, "data", "board")
LABELED_DIR  = os.path.join(BASE_DIR, "data", "labeled")


class Shell:
    def __init__(self):
        self.console = Console()
        self.manager = AccountManager()
        self.running = True

    def run(self):
        try:
            asyncio.run(self._loop())
        except KeyboardInterrupt:
            self.console.print("\n[dim]Bye![/dim]")

    # ── UI ────────────────────────────────────────────────

    def _header(self):
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold green]PDB Parser[/bold green]\n[dim]personality-database.com[/dim]",
            border_style="green"
        ))
        if self.manager.current_account:
            self.console.print(
                f"[dim]Account: [green]{self.manager.current_account.name}[/green][/dim]\n"
            )

    def _pause(self):
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

    def _menu(self, title: str, items: dict) -> str:
        self.console.rule(f"[bold]{title}[/bold]")
        for key, label in items.items():
            self.console.print(f"  [cyan]{key}[/cyan]  {label}")
        return Prompt.ask("\nChoice", choices=list(items.keys()))

    def _accounts_table(self) -> bool:
        if not self.manager.accounts:
            self.console.print("[yellow]No saved accounts[/yellow]\n")
            return False

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Account")
        table.add_column("ID", style="dim")

        for i, acc in enumerate(self.manager.accounts):
            marker = "[green]●[/green] " if acc == self.manager.current_account else "  "
            table.add_row(str(i), f"{marker}{acc.name}", str(acc.id))

        self.console.print(table)
        self.console.print()
        return True

    def _error(self, e: BaseException):
        self.console.print(f"[red]Error: {type(e).__name__}: {e}[/red]")
        self.console.print(f"[dim]{traceback.format_exc()}[/dim]")

    # ── Save ──────────────────────────────────────────────

    async def _save(self, data: list, folder: str, prefix: str, id: int):
        if not data:
            self.console.print("[yellow]No data to save[/yellow]")
            return

        fmt          = Prompt.ask("Save as", choices=["json", "csv"], default="json")
        default_name = f"{prefix}_{id}.{fmt}"
        name         = Prompt.ask("Filename", default=default_name)

        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)

        if fmt == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        self.console.print(f"[green]✓[/green] Saved → [bold]{path}[/bold]")

    # ── Loops ─────────────────────────────────────────────

    async def _loop(self):
        while self.running:
            self._header()
            choice = self._menu("Main Menu", {
                "1": "Accounts",
                "2": "Parsing",
                "3": "ML stuff",
                "4": "Exit",
            })
            match choice:
                case "1": await self._accounts_loop()
                case "2": await self._parse_loop()
                case "3": await self._ml_loop()
                case "4": await self._exit()

    async def _accounts_loop(self):
        while True:
            self._header()
            self._accounts_table()
            choice = self._menu("Accounts", {
                "1": "Select account",
                "2": "Add account",
                "3": "Delete account",
                "4": "Back",
            })
            match choice:
                case "1": await self._select_account()
                case "2": await self._add_account()
                case "3": await self._delete_account()
                case "4": break

    async def _parse_loop(self):
        if not self.manager.current_account:
            self._header()
            self.console.print("[red]Select an account first[/red]")
            self._pause()
            return

        while True:
            self._header()
            choice = self._menu("Parsing", {
                "1": "Profiles",
                "2": "Board posts",
                "3": "Back",
            })
            match choice:
                case "1": await self._parse_profiles()
                case "2": await self._parse_board()
                case "3": break

    async def _ml_loop(self):
        while True:
            self._header()
            choice = self._menu("ML stuff", {
                "1": "Label profiles",
                "2": "Back",
            })
            match choice:
                case "1": await self._label_profiles()
                case "2": break

    # ── ML handlers ───────────────────────────────────────

    def _list_profile_files(self):
        files = []
        if os.path.exists(PROFILES_DIR):
            for f in os.listdir(PROFILES_DIR):
                if f.endswith(".json") or f.endswith(".csv"):
                    files.append(f)
        return sorted(files)

    def _load_profile_file(self, filename):
        path = os.path.join(PROFILES_DIR, filename)
        if filename.endswith(".json"):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        else:
            with open(path, encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))

    def _extract_label_row(self, comment, score):
        return {
            "profile_id":     comment.get("_profile_id"),
            "profile_name":   comment.get("_profile_name"),
            "comment_id":     comment.get("id"),
            "text":           comment.get("comment", ""),
            "score":          score,
            "points":         comment.get("points"),
            "vote_count":     comment.get("vote_count"),
            "vote_count_down": comment.get("vote_count_down"),
            "reply_count":    comment.get("reply_count"),
            "reputation":     comment.get("reputation"),
            "is_pinned":      comment.get("is_pinned"),
            "is_mod":         comment.get("is_mod"),
            "character_length": comment.get("character_length"),
            "theVote":        comment.get("theVote", ""),
            "user_mbti":      comment.get("user_mbti", ""),
            "user_title":     comment.get("user_title", ""),
            "create_date":    comment.get("create_date"),
        }

    async def _label_profiles(self):
        self._header()

        files = self._list_profile_files()
        if not files:
            self.console.print("[yellow]No profile files found.[/yellow]")
            self._pause()
            return

        self.console.rule("[bold]Select file[/bold]")
        for i, f in enumerate(files):
            self.console.print(f"  [cyan]{i}[/cyan]  {f}")

        idx = IntPrompt.ask("\nFile #", default=0)
        if not (0 <= idx < len(files)):
            self.console.print("[red]Invalid index[/red]")
            self._pause()
            return

        filename = files[idx]

        try:
            profiles = self._load_profile_file(filename)
        except BaseException as e:
            self._error(e)
            self._pause()
            return

        # ── Собираем ВСЕ комментарии ───────────────────────

        all_comments = []

        for profile in profiles:
            profile_name = profile.get("mbti_profile", "Unknown")
            profile_id = profile.get("id")

            for comment in profile.get("comments", []):
                if comment.get("comment", "").strip():
                    comment["_profile_name"] = profile_name
                    comment["_profile_id"] = profile_id
                    all_comments.append(comment)

        if not all_comments:
            self.console.print("[yellow]No comments found[/yellow]")
            self._pause()
            return

        random.shuffle(all_comments)

        self.console.print(
            f"\n[green]Loaded [bold]{len(all_comments)}[/bold] comments "
            f"from [bold]{len(profiles)}[/bold] profiles[/green]"
        )
        self.console.print("[dim]Score from 0.0 to 1.0. Type 'exit' to stop.[/dim]")
        self._pause()

        labeled = []

        for i, comment in enumerate(all_comments):
            self._header()

            self.console.rule(
                f"[bold]Comment {i + 1} / {len(all_comments)}[/bold]"
            )

            self.console.print(
                f"[cyan]Profile:[/cyan] "
                f"{comment.get('_profile_name')} "
                f"[dim](ID: {comment.get('_profile_id')})[/dim]\n"
            )

            meta = Table.grid(padding=(0, 2))
            meta.add_column(style="dim")
            meta.add_column()

            meta.add_row("Comment ID", str(comment.get("id", "—")))
            meta.add_row("Vote", str(comment.get("theVote", "—")))
            meta.add_row("Points", str(comment.get("points", "—")))
            meta.add_row("Replies", str(comment.get("reply_count", "—")))
            meta.add_row("Pinned", str(comment.get("is_pinned", "—")))
            meta.add_row("Length", str(comment.get("character_length", "—")))

            self.console.print(meta)
            self.console.print()

            text = comment.get("comment", "").strip()
            self.console.print(Panel(
                text[:1500] + ("..." if len(text) > 1500 else ""),
                border_style="dim"
            ))
            self.console.print()

            raw = Prompt.ask("[cyan]Score[/cyan] (0.0–1.0 or 'exit')")

            if raw.strip().lower() == "exit":
                break

            try:
                score = float(raw.strip())
                if not (0.0 <= score <= 1.0):
                    raise ValueError
            except ValueError:
                self.console.print("[red]Invalid score[/red]")
                continue

            labeled.append(self._extract_label_row(comment, score))

        if not labeled:
            self.console.print("[yellow]Nothing labeled.[/yellow]")
            self._pause()
            return

        self.console.print(
            f"\n[green]✓[/green] Labeled: [bold]{len(labeled)}[/bold] comments\n"
        )

        file_id = filename.split("_")[-1].split(".")[0]
        default_name = f"{file_id}_dataset.csv"
        name = Prompt.ask("Dataset filename", default=default_name)

        os.makedirs(LABELED_DIR, exist_ok=True)
        path = os.path.join(LABELED_DIR, name)

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=labeled[0].keys())
            writer.writeheader()
            writer.writerows(labeled)

        self.console.print(f"[green]✓[/green] Saved → [bold]{path}[/bold]")
        self._pause()

    async def _exit(self):
        self.console.print("\n[dim]Bye![/dim]")
        self.running = False


if __name__ == "__main__":
    Shell().run()