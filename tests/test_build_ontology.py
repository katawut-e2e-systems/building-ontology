from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from building_ontology.csv_loader import CsvProjectError, load_project
from building_ontology.ontology import build_ontology_project

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "data" / "building-management-csv"
EXPECTED_DIR = REPO_ROOT / "ontology"


class CsvLoaderTests(unittest.TestCase):
    def test_rejects_unknown_module_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "prefixes.csv").write_text("prefix,namespace\nex,https://example.com/#\n", encoding="utf-8")
            (temp_path / "ontologies.csv").write_text(
                "module_id,ontology_uri,label,output_file,imports\nroot,https://example.com/root,Root,root.ttl,\n",
                encoding="utf-8",
            )
            (temp_path / "triples.csv").write_text(
                "module_id,subject,predicate,object,object_kind,datatype,language\nmissing,ex:s,a,ex:Thing,qname,,\n",
                encoding="utf-8",
            )

            with self.assertRaises(CsvProjectError):
                load_project(temp_path)


class OntologyBuildTests(unittest.TestCase):
    def test_build_example_project_matches_repository_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            written_files = build_ontology_project(INPUT_DIR, temp_dir)
            self.assertTrue(written_files)

            for expected_path in EXPECTED_DIR.rglob("*.ttl"):
                generated_path = Path(temp_dir) / expected_path.relative_to(EXPECTED_DIR)
                self.assertTrue(generated_path.exists(), f"Missing generated file: {generated_path}")
                self.assertEqual(generated_path.read_text(encoding="utf-8"), expected_path.read_text(encoding="utf-8"))

    def test_build_supports_custom_schema_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            input_dir.mkdir()
            (input_dir / "prefixes.csv").write_text(
                "prefix,namespace\n"
                "rdfs,http://www.w3.org/2000/01/rdf-schema#\n"
                "owl,http://www.w3.org/2002/07/owl#\n"
                "custom,https://example.com/custom#\n",
                encoding="utf-8",
            )
            (input_dir / "ontologies.csv").write_text(
                "module_id,ontology_uri,label,output_file,imports\n"
                "custom-module,https://example.com/custom-module,Custom Module,custom.ttl,\n",
                encoding="utf-8",
            )
            (input_dir / "triples.csv").write_text(
                "module_id,subject,predicate,object,object_kind,datatype,language\n"
                "custom-module,custom:Asset_01,a,custom:Equipment,qname,,\n"
                "custom-module,custom:Asset_01,rdfs:label,Custom Equipment,literal,,\n",
                encoding="utf-8",
            )

            build_ontology_project(input_dir, temp_path / "output")

            rendered = (temp_path / "output" / "custom.ttl").read_text(encoding="utf-8")
            self.assertIn("@prefix custom: <https://example.com/custom#> .", rendered)
            self.assertIn("custom:Asset_01", rendered)
            self.assertIn("custom:Equipment", rendered)


if __name__ == "__main__":
    unittest.main()
