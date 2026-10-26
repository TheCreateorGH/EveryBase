import unittest
from pathlib import Path

from everybase import Schema, Storage
from everybase.tui import EveryBaseShell, _parse_value, build_parser


class TuiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = Schema.from_mapping(
            {
                "name": {"field_type": "str_trimmed", "required": True, "unique": True},
                "age": {"field_type": "uint8", "required": True},
            }
        )
        self.storage = Storage(":memory:", self.schema)

    def tearDown(self) -> None:
        self.storage.close()

    def test_parses_json_values_and_arguments(self) -> None:
        self.assertEqual(_parse_value("42"), 42)
        self.assertEqual(_parse_value('{"enabled": true}'), {"enabled": True})
        arguments = build_parser().parse_args(["--database", "/tmp/everybase-test.db"])
        self.assertEqual(arguments.database, Path("/tmp/everybase-test.db"))

    def test_edit_and_find_use_storage_validation(self) -> None:
        first = self.storage.create({"name": "Alice", "age": 30})
        second = self.storage.create({"name": "Bob", "age": 31})
        shell = EveryBaseShell(self.storage)
        shell.do_edit(f"{second['id']} age=30")
        self.assertEqual(self.storage.get(second["id"])["age"], 30)
        shell.do_find("name=Alice")
        self.assertEqual(self.storage.get(first["id"])["name"], "Alice")


if __name__ == "__main__":
    unittest.main()
