import logging
import tkinter as tk
from pathlib import Path
from typing import Any

import customtkinter as ctk
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

from everybase import Schema, Storage, ValidationError


install_rich_traceback(show_locals=True)
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("everybase")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("EveryBase")
        self.geometry("900x650")
        self.minsize(700, 500)

        schema_path = Path(__file__).parent / "configs" / "DUMMY_entrys.jsonc"
        self.schema = Schema.from_file(schema_path)
        self.storage = Storage(":memory:", self.schema)
        self.inputs: dict[str, tk.Variable] = {}
        self._build_layout()
        self._refresh_records()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(self, text="EveryBase", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="New entry", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w"
        )
        for row, field in enumerate(self.schema.fields, start=1):
            ctk.CTkLabel(form, text=f"{field.name} ({field.field_type})").grid(
                row=row, column=0, padx=15, pady=6, sticky="w"
            )
            if field.field_type == "bool":
                variable: tk.Variable = tk.BooleanVar(value=field.default is True)
                ctk.CTkCheckBox(form, text="", variable=variable).grid(
                    row=row, column=1, padx=15, pady=6, sticky="w"
                )
            else:
                variable = tk.StringVar(value="" if field.default is None else str(field.default))
                ctk.CTkEntry(form, textvariable=variable).grid(
                    row=row, column=1, padx=15, pady=6, sticky="ew"
                )
            self.inputs[field.name] = variable

        self.status = ctk.CTkLabel(form, text="", wraplength=250, justify="left")
        self.status.grid(row=len(self.schema.fields) + 1, column=0, columnspan=2, padx=15, pady=8, sticky="w")
        ctk.CTkButton(form, text="Add entry", command=self._add_entry).grid(
            row=len(self.schema.fields) + 2, column=0, columnspan=2, padx=15, pady=(5, 15), sticky="ew"
        )

        records = ctk.CTkFrame(self)
        records.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        records.grid_rowconfigure(1, weight=1)
        records.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(records, text="Stored entries", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=15, pady=(15, 10), sticky="w"
        )
        self.record_list = ctk.CTkScrollableFrame(records, corner_radius=0)
        self.record_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.record_list.grid_columnconfigure(0, weight=1)

    def _add_entry(self) -> None:
        values: dict[str, Any] = {}
        for field in self.schema.fields:
            value = self.inputs[field.name].get()
            if field.field_type == "bool":
                values[field.name] = bool(value)
            elif value != "":
                values[field.name] = value
        try:
            self.storage.create(values)
        except ValidationError as error:
            self.status.configure(text=str(error), text_color="#ff6b6b")
            return
        for variable in self.inputs.values():
            if isinstance(variable, tk.BooleanVar):
                variable.set(True)
            else:
                variable.set("")
        self.status.configure(text="Entry added.", text_color="#78d381")
        self._refresh_records()

    def _refresh_records(self) -> None:
        for child in self.record_list.winfo_children():
            child.destroy()
        for row, record in enumerate(self.storage.list()):
            text = "  |  ".join(f"{field.name}: {record.get(field.name, '')}" for field in self.schema.fields)
            ctk.CTkLabel(self.record_list, text=text, anchor="w").grid(
                row=row, column=0, padx=10, pady=8, sticky="ew"
            )

    def destroy(self) -> None:
        self.storage.close()
        super().destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()
