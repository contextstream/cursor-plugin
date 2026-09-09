"""Fictional exporter used only for an opt-in ContextStream demonstration."""
import csv
import io
import json
from collections.abc import Mapping, Sequence

FIELDS = ("id", "name")

def serialize_csv(rows: Sequence[Mapping[str, str]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()

def serialize_json(rows: Sequence[Mapping[str, str]]) -> str:
    return json.dumps(list(rows), ensure_ascii=False)
