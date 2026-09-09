"""Fictional in-process API facade. No web server or external requests."""
from collections.abc import Mapping, Sequence
from exporters import serialize_csv, serialize_json

def export_report(rows: Sequence[Mapping[str, str]], format: str = "csv") -> str:
    if format == "csv":
        return serialize_csv(rows)
    if format == "json":
        return serialize_json(rows)
    raise ValueError("Unsupported export format")
