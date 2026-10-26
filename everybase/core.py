from __future__ import annotations

import json
import re
import sqlite3
import uuid
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


Validator = Callable[[Any], Any]


def load_jsonc(path: str | Path) -> dict[str, Any]:
    """Load a JSON or JSONC object while preserving comment-like text in strings."""
    source = Path(path).read_text(encoding="utf-8")
    output: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(source):
        character = source[index]
        if character == '"' and not escaped:
            in_string = not in_string
        if not in_string and character == "/" and index + 1 < len(source) and source[index + 1] == "/":
            while index < len(source) and source[index] != "\n":
                index += 1
            continue
        output.append(character)
        escaped = character == "\\" and not escaped
        if character != "\\":
            escaped = False
        index += 1
    parsed = json.loads("".join(output))
    if not isinstance(parsed, dict):
        raise SchemaError("Configuration root must be an object.")
    return parsed


class EveryBaseError(Exception):
    """Base exception for EveryBase errors."""


class SchemaError(EveryBaseError):
    """Raised when a schema is malformed or references an unknown type."""


class ValidationError(EveryBaseError):
    """Raised when an entry does not satisfy its schema."""


class EntryNotFoundError(EveryBaseError):
    """Raised when an entry identifier does not exist."""


def _ensure_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a string")
    return value


def _ensure_int(value: Any) -> int:
    if isinstance(value, str):
        value = value.strip()
        if not re.fullmatch(r"[+-]?\d+", value):
            raise ValueError("must be an integer")
        try:
            return int(value)
        except ValueError as error:
            raise ValueError("must be an integer") from error
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("must be an integer")
    return value


def _ensure_float(value: Any) -> float:
    if isinstance(value, str):
        value = value.strip()
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value):
            raise ValueError("must be a number")
        try:
            return float(value)
        except ValueError as error:
            raise ValueError("must be a number") from error
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("must be a number")
    return float(value)


def _ensure_bool(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
        raise ValueError("must be true or false")
    if not isinstance(value, bool):
        raise ValueError("must be a boolean")
    return value


def _ensure_date(value: Any) -> str:
    value = _ensure_string(value)
    date.fromisoformat(value)
    return value


def _ensure_time(value: Any) -> str:
    value = _ensure_string(value)
    time.fromisoformat(value)
    return value


def _ensure_datetime(value: Any) -> str:
    value = _ensure_string(value)
    datetime.fromisoformat(value)
    return value


def _ensure_email(value: Any) -> str:
    value = _ensure_string(value)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValueError("must be a valid email address")
    return value


def _ensure_url(value: Any) -> str:
    value = _ensure_string(value)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("must be a valid HTTP or HTTPS URL")
    return value


def _ensure_uuid(value: Any) -> str:
    value = _ensure_string(value)
    uuid.UUID(value)
    return value


def _ensure_list(value: Any) -> list[Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("must be a JSON array") from error
    if not isinstance(value, list):
        raise ValueError("must be a list")
    return value


def _ensure_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("must be a JSON object") from error
    if not isinstance(value, dict):
        raise ValueError("must be an object")
    if not all(isinstance(key, str) for key in value):
        raise ValueError("object keys must be strings")
    return value


def _ensure_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    try:
        json.dumps(value)
    except (TypeError, ValueError) as error:
        raise ValueError("must be JSON-serializable") from error
    return value


def _ensure_ipv4(value: Any) -> str:
    import ipaddress

    value = _ensure_string(value)
    if not isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address):
        raise ValueError("must be an IPv4 address")
    return value


def _ensure_ipv6(value: Any) -> str:
    import ipaddress

    value = _ensure_string(value)
    if not isinstance(ipaddress.ip_address(value), ipaddress.IPv6Address):
        raise ValueError("must be an IPv6 address")
    return value


def _ensure_phone(value: Any) -> str:
    value = _ensure_string(value)
    if not re.fullmatch(r"\+?[0-9][0-9 ()-]{5,}[0-9]", value):
        raise ValueError("must be a valid phone number")
    return value


def _ensure_mac(value: Any) -> str:
    value = _ensure_string(value)
    if not re.fullmatch(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", value):
        raise ValueError("must be a valid MAC address")
    return value


def _ensure_hex(value: Any) -> str:
    value = _ensure_string(value)
    if not re.fullmatch(r"(?:0x)?[0-9A-Fa-f]+", value):
        raise ValueError("must be a hexadecimal value")
    return value


def _ensure_color(value: Any) -> str:
    value = _ensure_string(value)
    if not (
        re.fullmatch(r"#[0-9A-Fa-f]{3,8}", value)
        or re.fullmatch(r"rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)", value)
        or re.fullmatch(r"[A-Za-z]+", value)
    ):
        raise ValueError("must be a color name, hex color, or rgb() value")
    return value


def _ensure_currency(value: Any) -> str:
    value = _ensure_string(value)
    if not re.fullmatch(r"[A-Za-z]{3}\s?-?\d+(?:\.\d{1,2})?", value) and not re.fullmatch(
        r"[$€£¥]-?\d+(?:\.\d{1,2})?", value
    ):
        raise ValueError("must be a currency amount")
    return value


def _ensure_duration(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            return float(value) if "." in value else int(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)?(?:ms|s|m|h|d)", value):
        return value
    raise ValueError("must be a non-negative number or duration string")


def _ensure_passthrough(value: Any) -> Any:
    return _ensure_json(value)


def _ensure_set(value: Any) -> list[Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("must be a JSON array") from error
    if not isinstance(value, (set, frozenset, list, tuple)):
        raise ValueError("must be a set or JSON array")
    values = list(value)
    if len(values) != len({_ensure_json_value_key(item) for item in values}):
        raise ValueError("must contain unique values")
    return values


def _ensure_tuple(value: Any) -> list[Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("must be a JSON array") from error
    if not isinstance(value, tuple | list):
        raise ValueError("must be a tuple or JSON array")
    return list(value)


def _ensure_json_value_key(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True)
    except (TypeError, ValueError) as error:
        raise ValueError("must contain JSON-compatible values") from error


def _ensure_range(
    validator: Validator, minimum: int | float | None = None, maximum: int | float | None = None
) -> Validator:
    def wrapped(value: Any) -> Any:
        result = validator(value)
        if minimum is not None and result < minimum:
            raise ValueError(f"must be at least {minimum}")
        if maximum is not None and result > maximum:
            raise ValueError(f"must be at most {maximum}")
        return result

    return wrapped


class TypeRegistry:
    """Registry of field type validators."""

    def __init__(self) -> None:
        self._validators: dict[str, Validator] = {}
        self._register_builtins()

    def register(self, name: str, validator: Validator) -> None:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
            raise ValueError("type names must start with a letter and contain only letters, numbers, or _")
        if name in self._validators:
            raise ValueError(f"type '{name}' is already registered")
        self._validators[name] = validator

    def validate(self, type_name: str, value: Any) -> Any:
        try:
            validator = self._validators[type_name]
        except KeyError as error:
            raise SchemaError(f"Unknown field type '{type_name}'.") from error
        try:
            return validator(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{type_name}: {error}") from error

    def has(self, type_name: str) -> bool:
        return type_name in self._validators

    def _register_builtins(self) -> None:
        builtins: dict[str, Validator] = {
            "str": _ensure_string,
            "int": _ensure_int,
            "float": _ensure_float,
            "bool": _ensure_bool,
            "positive": _ensure_range(_ensure_int, minimum=1),
            "positive0": _ensure_range(_ensure_int, minimum=0),
            "negative": _ensure_range(_ensure_int, maximum=-1),
            "negative0": _ensure_range(_ensure_int, maximum=0),
            "positivle": _ensure_range(_ensure_float, minimum=1),
            "positivle0": _ensure_range(_ensure_float, minimum=0),
            "negativle": _ensure_range(_ensure_float, maximum=-1),
            "negativle0": _ensure_range(_ensure_float, maximum=0),
            "zero": _ensure_range(_ensure_float, minimum=0, maximum=0),
            "nonzero": lambda value: value if _ensure_float(value) != 0 else (_ for _ in ()).throw(ValueError("must not be zero")),
            "uint": _ensure_range(_ensure_int, minimum=0),
            "uint8": _ensure_range(_ensure_int, minimum=0, maximum=255),
            "int8": _ensure_range(_ensure_int, minimum=-128, maximum=127),
            "int16": _ensure_range(_ensure_int, minimum=-32768, maximum=32767),
            "int32": _ensure_range(_ensure_int, minimum=-2147483648, maximum=2147483647),
            "percent": _ensure_range(_ensure_float, minimum=0, maximum=100),
            "percent0": _ensure_range(_ensure_float, minimum=0, maximum=1),
            "ratio": _ensure_range(_ensure_float, minimum=0, maximum=1),
            "char": lambda value: value if isinstance(value, str) and len(value) == 1 else (_ for _ in ()).throw(ValueError("must contain exactly one character")),
            "text": _ensure_string,
            "word": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"\S+", value)) else (_ for _ in ()).throw(ValueError("must contain one non-whitespace word")),
            "username": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9_-]+", value)) else (_ for _ in ()).throw(ValueError("contains unsupported characters")),
            "password": _ensure_string,
            "str_alpha": lambda value: value if isinstance(value, str) and value.isalpha() else (_ for _ in ()).throw(ValueError("must contain only letters")),
            "str_alphanumeric": lambda value: value if isinstance(value, str) and value.isalnum() else (_ for _ in ()).throw(ValueError("must contain only letters and numbers")),
            "str_numeric": lambda value: value if isinstance(value, str) and value.isnumeric() else (_ for _ in ()).throw(ValueError("must contain only numbers")),
            "str_lower": lambda value: value if _ensure_string(value).islower() else (_ for _ in ()).throw(ValueError("must be lowercase")),
            "str_upper": lambda value: value if _ensure_string(value).isupper() else (_ for _ in ()).throw(ValueError("must be uppercase")),
            "str_trimmed": lambda value: value if _ensure_string(value) == value.strip() else (_ for _ in ()).throw(ValueError("must not have leading or trailing whitespace")),
            "str_slug": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value)) else (_ for _ in ()).throw(ValueError("must be lowercase kebab-case")),
            "date": _ensure_date,
            "time": _ensure_time,
            "datetime": _ensure_datetime,
            "email": _ensure_email,
            "url": _ensure_url,
            "uuid": _ensure_uuid,
            "ipv4": _ensure_ipv4,
            "ipv6": _ensure_ipv6,
            "phone": _ensure_phone,
            "mac": _ensure_mac,
            "hex": _ensure_hex,
            "color": _ensure_color,
            "currency": _ensure_currency,
            "latitude": _ensure_range(_ensure_float, minimum=-90, maximum=90),
            "longitude": _ensure_range(_ensure_float, minimum=-180, maximum=180),
            "timezone": _ensure_string,
            "locale": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})?", value)) else (_ for _ in ()).throw(ValueError("must be a locale identifier")),
            "country": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"[A-Z]{2}", value)) else (_ for _ in ()).throw(ValueError("must be an uppercase two-letter country code")),
            "language": lambda value: value if isinstance(value, str) and bool(re.fullmatch(r"[a-z]{2,3}", value)) else (_ for _ in ()).throw(ValueError("must be a lowercase two- or three-letter language code")),
            "timestamp": _ensure_range(_ensure_int, minimum=0),
            "duration": _ensure_duration,
            "list": _ensure_list,
            "dict": _ensure_dict,
            "json": _ensure_json,
            "set": _ensure_set,
            "tuple": _ensure_tuple,
            "nullable": _ensure_passthrough,
            "optional": _ensure_passthrough,
            "constant": _ensure_passthrough,
            "path": _ensure_string,
            "file": _ensure_string,
            "directory": _ensure_string,
        }
        self._validators.update(builtins)


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    field_type: str
    required: bool = False
    unique: bool = False
    default: Any = None


class Schema:
    def __init__(self, fields: Iterable[FieldDefinition], registry: TypeRegistry | None = None) -> None:
        self.registry = registry or TypeRegistry()
        self.fields = tuple(fields)
        names = [field.name for field in self.fields]
        if not names or len(names) != len(set(names)):
            raise SchemaError("A schema must contain at least one uniquely named field.")
        for field in self.fields:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field.name):
                raise SchemaError(f"Invalid field name '{field.name}'.")
            if not isinstance(field.required, bool) or not isinstance(field.unique, bool):
                raise SchemaError(f"Field '{field.name}' requires boolean 'required' and 'unique' values.")
            if not self.registry.has(field.field_type):
                raise SchemaError(f"Unknown field type '{field.field_type}'.")
            if field.default is not None:
                try:
                    self.registry.validate(field.field_type, field.default)
                except ValueError as error:
                    raise SchemaError(f"Invalid default for '{field.name}': {error}") from error

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any], registry: TypeRegistry | None = None) -> Schema:
        if not isinstance(mapping, Mapping) or not mapping:
            raise SchemaError("Schema must be a non-empty object.")
        fields = []
        for name, definition in mapping.items():
            if name == "$schema":
                continue
            if not isinstance(definition, Mapping):
                raise SchemaError(f"Definition for '{name}' must be an object.")
            if "field_type" not in definition:
                raise SchemaError(f"Field '{name}' is missing 'field_type'.")
            fields.append(
                FieldDefinition(
                    name=name,
                    field_type=definition["field_type"],
                    required=definition.get("required", False),
                    unique=definition.get("unique", False),
                    default=definition.get("default"),
                )
            )
        return cls(fields, registry)

    @classmethod
    def from_file(cls, path: str | Path, registry: TypeRegistry | None = None) -> Schema:
        return cls.from_mapping(load_jsonc(path), registry)

    def validate_entry(self, entry: Mapping[str, Any], *, partial: bool = False) -> dict[str, Any]:
        if not isinstance(entry, Mapping):
            raise ValidationError("Entry must be an object.")
        known = {field.name for field in self.fields}
        unknown = set(entry) - known
        if unknown:
            raise ValidationError(f"Unknown fields: {', '.join(sorted(unknown))}.")

        result: dict[str, Any] = {}
        errors: list[str] = []
        for field in self.fields:
            present = field.name in entry
            value = entry.get(field.name)
            if not present:
                if partial:
                    continue
                if field.required and field.default is None:
                    errors.append(f"{field.name}: is required")
                    continue
                if field.default is not None:
                    value = field.default
                else:
                    continue
            try:
                result[field.name] = self.registry.validate(field.field_type, value)
            except (SchemaError, ValueError) as error:
                errors.append(f"{field.name}: {error}")
        if errors:
            raise ValidationError("; ".join(errors))
        return result

    def field(self, name: str) -> FieldDefinition:
        for field in self.fields:
            if field.name == name:
                return field
        raise KeyError(name)


class Storage:
    """SQLite-backed storage for records validated by a schema."""

    def __init__(self, database: str | Path, schema: Schema) -> None:
        self.schema = schema
        database_path = Path(database)
        if str(database_path) != ":memory:":
            database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(database))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> Storage:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def create(self, entry: Mapping[str, Any], entry_id: str | None = None) -> dict[str, Any]:
        validated = self.schema.validate_entry(entry)
        identifier = entry_id or str(uuid.uuid4())
        try:
            payload = json.dumps(validated, sort_keys=True)
        except (TypeError, ValueError) as error:
            raise ValidationError("Entry contains a value that cannot be stored as JSON.") from error
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            self._check_unique(validated)
            self.connection.execute(
                "INSERT INTO entries (id, data) VALUES (?, ?)",
                (identifier, payload),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as error:
            self.connection.rollback()
            raise ValidationError(f"Entry id '{identifier}' already exists.") from error
        except ValidationError:
            self.connection.rollback()
            raise
        return {"id": identifier, **validated}

    def get(self, entry_id: str) -> dict[str, Any]:
        row = self.connection.execute("SELECT id, data FROM entries WHERE id = ?", (entry_id,)).fetchone()
        if row is None:
            raise EntryNotFoundError(f"Entry '{entry_id}' was not found.")
        return {"id": row["id"], **json.loads(row["data"])}

    def list(self) -> list[dict[str, Any]]:
        rows = self.connection.execute("SELECT id, data FROM entries ORDER BY created_at, id").fetchall()
        return [{"id": row["id"], **json.loads(row["data"])} for row in rows]

    def update(self, entry_id: str, changes: Mapping[str, Any]) -> dict[str, Any]:
        current = self.get(entry_id)
        current.pop("id")
        current.update(changes)
        validated = self.schema.validate_entry(current)
        try:
            payload = json.dumps(validated, sort_keys=True)
        except (TypeError, ValueError) as error:
            raise ValidationError("Entry contains a value that cannot be stored as JSON.") from error
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            self._check_unique(validated, excluding=entry_id)
            self.connection.execute(
                "UPDATE entries SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (payload, entry_id),
            )
            self.connection.commit()
        except ValidationError:
            self.connection.rollback()
            raise
        return {"id": entry_id, **validated}

    def delete(self, entry_id: str) -> None:
        cursor = self.connection.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.connection.commit()
        if cursor.rowcount == 0:
            raise EntryNotFoundError(f"Entry '{entry_id}' was not found.")

    def _check_unique(self, entry: Mapping[str, Any], excluding: str | None = None) -> None:
        unique_fields = [field.name for field in self.schema.fields if field.unique and field.name in entry]
        if not unique_fields:
            return
        rows = self.connection.execute("SELECT id, data FROM entries").fetchall()
        for row in rows:
            if row["id"] == excluding:
                continue
            existing = json.loads(row["data"])
            for field in unique_fields:
                if existing.get(field) == entry[field]:
                    raise ValidationError(f"{field}: value must be unique")
