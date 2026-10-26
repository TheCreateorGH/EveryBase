import tempfile
import unittest
from pathlib import Path

from everybase import EntryNotFoundError, Schema, SchemaError, Storage, ValidationError


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = Schema.from_mapping(
            {
                "name": {"field_type": "str_trimmed", "required": True, "unique": True},
                "age": {"field_type": "uint8", "required": True},
                "active": {"field_type": "bool", "default": True},
            }
        )
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self.temp_dir.name) / "test.db", self.schema)

    def tearDown(self) -> None:
        self.storage.close()
        self.temp_dir.cleanup()

    def test_create_applies_defaults_and_round_trips(self) -> None:
        entry = self.storage.create({"name": "Alice", "age": 30})
        self.assertEqual(entry["active"], True)
        self.assertEqual(self.storage.get(entry["id"]), entry)

    def test_invalid_and_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.storage.create({"name": "Alice", "age": 300})
        with self.assertRaises(ValidationError):
            self.storage.create({"name": "Alice", "age": 30, "unknown": 1})

    def test_unique_values_are_enforced_on_create_and_update(self) -> None:
        first = self.storage.create({"name": "Alice", "age": 30})
        with self.assertRaises(ValidationError):
            self.storage.create({"name": "Alice", "age": 31})
        second = self.storage.create({"name": "Bob", "age": 31})
        with self.assertRaises(ValidationError):
            self.storage.update(second["id"], {"name": "Alice"})
        self.assertEqual(self.storage.get(first["id"])["name"], "Alice")

    def test_update_validates_the_complete_record(self) -> None:
        entry = self.storage.create({"name": "Alice", "age": 30})
        with self.assertRaises(ValidationError):
            self.storage.update(entry["id"], {"age": -1})

    def test_delete_and_missing_records(self) -> None:
        entry = self.storage.create({"name": "Alice", "age": 30})
        self.storage.delete(entry["id"])
        with self.assertRaises(EntryNotFoundError):
            self.storage.get(entry["id"])

    def test_unknown_schema_type_is_rejected(self) -> None:
        with self.assertRaises(SchemaError):
            Schema.from_mapping({"value": {"field_type": "not_a_type"}})

    def test_invalid_default_is_rejected_when_schema_is_created(self) -> None:
        with self.assertRaises(SchemaError):
            Schema.from_mapping({"age": {"field_type": "uint8", "default": 300}})

    def test_jsonc_schema_file_is_loaded(self) -> None:
        schema = Schema.from_file(Path(__file__).parents[1] / "configs" / "DUMMY_entrys.jsonc")
        self.assertEqual(schema.field("name").field_type, "str_trimmed")
        self.assertTrue(schema.field("email").unique)

    def test_common_catalog_types_validate(self) -> None:
        schema = Schema.from_mapping(
            {
                "phone": {"field_type": "phone"},
                "location": {"field_type": "latitude"},
                "country": {"field_type": "country"},
                "color": {"field_type": "color"},
                "duration": {"field_type": "duration"},
            }
        )
        self.assertEqual(
            schema.validate_entry(
                {
                    "phone": "+44 20 1234 5678",
                    "location": 51.5,
                    "country": "GB",
                    "color": "#00FF00",
                    "duration": "30s",
                }
            )["country"],
            "GB",
        )

    def test_string_values_are_parsed_for_non_string_types(self) -> None:
        schema = Schema.from_mapping(
            {
                "integer": {"field_type": "int"},
                "decimal": {"field_type": "float"},
                "flag": {"field_type": "bool"},
                "items": {"field_type": "list"},
                "metadata": {"field_type": "dict"},
                "payload": {"field_type": "json"},
                "tags": {"field_type": "set"},
                "coordinates": {"field_type": "tuple"},
                "when": {"field_type": "date"},
            }
        )
        entry = schema.validate_entry(
            {
                "integer": "42",
                "decimal": "3.5",
                "flag": "false",
                "items": '["a", 2]',
                "metadata": '{"enabled": true}',
                "payload": '{"count": 2}',
                "tags": '["a", "b"]',
                "coordinates": "[10, 20]",
                "when": "2026-10-26",
            }
        )
        self.assertIsInstance(entry["integer"], int)
        self.assertEqual(entry["integer"], 42)
        self.assertIsInstance(entry["decimal"], float)
        self.assertFalse(entry["flag"])
        self.assertEqual(entry["items"], ["a", 2])
        self.assertEqual(entry["metadata"], {"enabled": True})
        self.assertEqual(entry["tags"], ["a", "b"])
        self.assertEqual(entry["coordinates"], [10, 20])

    def test_invalid_string_parsing_is_rejected(self) -> None:
        schema = Schema.from_mapping(
            {
                "integer": {"field_type": "int"},
                "flag": {"field_type": "bool"},
                "items": {"field_type": "list"},
            }
        )
        with self.assertRaises(ValidationError):
            schema.validate_entry({"integer": "3.5", "flag": "maybe", "items": "not-json"})

    def test_storage_creates_parent_directories(self) -> None:
        database = Path(self.temp_dir.name) / "nested" / "data.db"
        storage = Storage(database, self.schema)
        storage.close()
        self.assertTrue(database.exists())

if __name__ == "__main__":
    unittest.main()
