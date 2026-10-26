"""Interactive terminal interface for the EveryBase package."""

from __future__ import annotations

import argparse
import cmd
import json
import shlex
from pathlib import Path
from typing import Any

from .core import EveryBaseError, Schema, Storage, ValidationError


DEFAULT_SCHEMA = Path(__file__).parents[1] / "configs" / "DUMMY_entrys.jsonc"
DEFAULT_DATABASE = Path.home() / ".local" / "share" / "everybase" / "everybase.db"


def _parse_value(raw: str) -> Any:
    """Parse JSON literals while leaving ordinary text unchanged."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


class EveryBaseShell(cmd.Cmd):
    """Command shell backed by one schema-aware storage instance."""
    intro = "EveryBase TUI. Type 'help' for commands."
    prompt = "everybase> "

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self.storage = storage

    def do_list(self, _line: str) -> None:
        """list: Show all stored entries."""
        entries = self.storage.list()
        if not entries:
            print("No entries.")
            return
        for entry in entries:
            print(json.dumps(entry, ensure_ascii=False, sort_keys=True))

    def do_add(self, _line: str) -> None:
        """add: Add an entry by prompting for every schema field."""
        values: dict[str, Any] = {}
        for field in self.storage.schema.fields:
            default = "" if field.default is None else f" [{field.default}]"
            raw = input(f"{field.name} ({field.field_type}){default}: ")
            if not raw and field.default is None:
                continue
            values[field.name] = _parse_value(raw) if raw else field.default
        try:
            entry = self.storage.create(values)
        except ValidationError as error:
            print(f"Error: {error}")
            return
        print(json.dumps(entry, ensure_ascii=False, sort_keys=True))

    def do_show(self, line: str) -> None:
        """show ID: Show one entry."""
        arguments = shlex.split(line)
        if len(arguments) != 1:
            print("Usage: show ID")
            return
        try:
            print(json.dumps(self.storage.get(arguments[0]), ensure_ascii=False, sort_keys=True))
        except EveryBaseError as error:
            print(f"Error: {error}")

    def do_delete(self, line: str) -> None:
        """delete ID: Delete one entry."""
        arguments = shlex.split(line)
        if len(arguments) != 1:
            print("Usage: delete ID")
            return
        try:
            self.storage.delete(arguments[0])
        except EveryBaseError as error:
            print(f"Error: {error}")
            return
        print("Deleted.")

    def do_edit(self, line: str) -> None:
        """edit ID field=value [...]: Update fields on an entry."""
        arguments = shlex.split(line)
        if len(arguments) < 2:
            print("Usage: edit ID field=value [...]")
            return
        entry_id, assignments = arguments[0], arguments[1:]
        changes: dict[str, Any] = {}
        for assignment in assignments:
            if "=" not in assignment:
                print(f"Invalid assignment: {assignment}")
                return
            field_name, raw_value = assignment.split("=", 1)
            if not field_name:
                print(f"Invalid assignment: {assignment}")
                return
            changes[field_name] = _parse_value(raw_value)
        try:
            entry = self.storage.update(entry_id, changes)
        except EveryBaseError as error:
            print(f"Error: {error}")
            return
        print(json.dumps(entry, ensure_ascii=False, sort_keys=True))

    def do_find(self, line: str) -> None:
        """find field=value: Show entries whose field equals the parsed value."""
        arguments = shlex.split(line)
        if len(arguments) != 1 or "=" not in arguments[0]:
            print("Usage: find field=value")
            return
        field_name, raw_value = arguments[0].split("=", 1)
        expected = _parse_value(raw_value)
        try:
            self.storage.schema.field(field_name)
        except KeyError:
            print(f"Error: unknown field '{field_name}'")
            return
        matches = [
            entry for entry in self.storage.list()
            if entry.get(field_name) == expected
        ]
        for entry in matches:
            print(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        if not matches:
            print("No matching entries.")

    def do_schema(self, _line: str) -> None:
        """schema: Show the active schema."""
        for field in self.storage.schema.fields:
            flags = []
            if field.required:
                flags.append("required")
            if field.unique:
                flags.append("unique")
            print(f"{field.name}: {field.field_type} ({', '.join(flags) or 'optional'})")

    def do_quit(self, _line: str) -> bool:
        """quit: Exit EveryBase."""
        return True

    do_exit = do_quit


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the TUI."""
    parser = argparse.ArgumentParser(description="EveryBase schema-driven TUI")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    return parser


def main(argv: list[str] | None = None) -> None:
    """Load the configured schema and run the interactive shell."""
    arguments = build_parser().parse_args(argv)
    schema = Schema.from_file(arguments.schema)
    with Storage(arguments.database, schema) as storage:
        EveryBaseShell(storage).cmdloop()


if __name__ == "__main__":
    main()
