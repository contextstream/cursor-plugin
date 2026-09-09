"""Fixture contract tests, not model evaluations."""
import csv
import io
import json
import unittest
from report_api import export_report

class ExportContractTests(unittest.TestCase):
    def test_default_remains_csv(self):
        self.assertEqual(export_report([{"id":"1","name":"Harbor"}]), "id,name\n1,Harbor\n")
    def test_explicit_csv(self):
        self.assertEqual(export_report([],"csv"),"id,name\n")
    def test_json_is_additive(self):
        rows=[{"id":"1","name":"Harbor"}]
        self.assertEqual(json.loads(export_report(rows,"json")),rows)
    def test_csv_escaping(self):
        rows=[{"id":"1","name":"A, B \"quoted\""}]
        self.assertEqual(list(csv.DictReader(io.StringIO(export_report(rows)))),rows)
    def test_invalid_format(self):
        with self.assertRaises(ValueError): export_report([],"unsupported")
    def test_contract_column_order(self):
        self.assertEqual(export_report([{"name":"Harbor","id":"1"}]).splitlines()[0],"id,name")

if __name__ == "__main__": unittest.main()
