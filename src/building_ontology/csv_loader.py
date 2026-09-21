from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import OntologyModule, OntologyProject, Prefix, Triple

PREFIX_FILE = "prefixes.csv"
ONTOLOGY_FILE = "ontologies.csv"
TRIPLE_FILE = "triples.csv"


class CsvProjectError(ValueError):
    """Raised when the CSV project is invalid."""


REQUIRED_PREFIX_COLUMNS = {"prefix", "namespace"}
REQUIRED_ONTOLOGY_COLUMNS = {"module_id", "ontology_uri", "label", "output_file", "imports"}
REQUIRED_TRIPLE_COLUMNS = {"module_id", "subject", "predicate", "object", "object_kind", "datatype", "language"}
ALLOWED_OBJECT_KINDS = {"qname", "iri", "literal"}
QNAME_PATTERN = re.compile(r"^[A-Za-z_][\\w.-]*:[^\\s]+$")
LANGUAGE_PATTERN = re.compile(r"^[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*$")


def load_project(input_dir: Path) -> OntologyProject:
    prefixes = _load_prefixes(input_dir / PREFIX_FILE)
    modules = _load_modules(input_dir / ONTOLOGY_FILE)
    _load_triples(input_dir / TRIPLE_FILE, modules)
    return OntologyProject(prefixes=prefixes, modules=list(modules.values()))


def _load_prefixes(path: Path) -> list[Prefix]:
    rows = _read_rows(path, REQUIRED_PREFIX_COLUMNS)
    prefixes: list[Prefix] = []
    seen: set[str] = set()
    for row in rows:
        prefix = row["prefix"].strip()
        namespace = row["namespace"].strip()
        if not prefix or not namespace:
            raise CsvProjectError(f"Invalid prefix row in {path.name}: {row}")
        if prefix in seen:
            raise CsvProjectError(f"Duplicate prefix '{prefix}' in {path.name}")
        seen.add(prefix)
        prefixes.append(Prefix(prefix=prefix, namespace=namespace))
    return prefixes


def _load_modules(path: Path) -> dict[str, OntologyModule]:
    rows = _read_rows(path, REQUIRED_ONTOLOGY_COLUMNS)
    modules: dict[str, OntologyModule] = {}
    for row in rows:
        module_id = row["module_id"].strip()
        if not module_id:
            raise CsvProjectError(f"Missing module_id in {path.name}: {row}")
        if module_id in modules:
            raise CsvProjectError(f"Duplicate module_id '{module_id}' in {path.name}")
        ontology_uri = row["ontology_uri"].strip()
        label = row["label"].strip()
        output_file = row["output_file"].strip()
        if not ontology_uri or not label or not output_file:
            raise CsvProjectError(f"Invalid ontology row in {path.name}: {row}")
        imports = [value.strip() for value in row["imports"].split("|") if value.strip()]
        modules[module_id] = OntologyModule(
            module_id=module_id,
            ontology_uri=ontology_uri,
            label=label,
            output_file=output_file,
            imports=imports,
        )
    return modules


def _load_triples(path: Path, modules: dict[str, OntologyModule]) -> None:
    rows = _read_rows(path, REQUIRED_TRIPLE_COLUMNS)
    for row in rows:
        module_id = row["module_id"].strip()
        if module_id not in modules:
            raise CsvProjectError(f"Triple references unknown module_id '{module_id}' in {path.name}")
        object_kind = (row["object_kind"].strip() or "qname").lower()
        if object_kind not in ALLOWED_OBJECT_KINDS:
            raise CsvProjectError(
                f"Unsupported object_kind '{object_kind}' in {path.name}; expected one of {sorted(ALLOWED_OBJECT_KINDS)}"
            )
        subject = row["subject"].strip()
        predicate = row["predicate"].strip()
        object_value = row["object"].strip()
        if not subject or not predicate or not object_value:
            raise CsvProjectError(f"Invalid triple row in {path.name}: {row}")
        datatype = row["datatype"].strip() or None
        language = row["language"].strip() or None
        if object_kind != "literal" and (datatype or language):
            raise CsvProjectError("Only literal objects can define datatype or language")
        if datatype and language:
            raise CsvProjectError("Literal objects cannot define both datatype and language")
        if datatype and not QNAME_PATTERN.match(datatype):
            raise CsvProjectError(f"Invalid datatype QName '{datatype}' in {path.name}")
        if language and not LANGUAGE_PATTERN.match(language):
            raise CsvProjectError(f"Invalid language tag '{language}' in {path.name}")
        modules[module_id].triples.append(
            Triple(
                module_id=module_id,
                subject=subject,
                predicate=predicate,
                object_value=object_value,
                object_kind=object_kind,
                datatype=datatype,
                language=language,
            )
        )


def _read_rows(path: Path, required_columns: set[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise CsvProjectError(f"Missing required CSV file: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise CsvProjectError(f"CSV file has no header row: {path}")
        missing = required_columns.difference(reader.fieldnames)
        if missing:
            missing_columns = ", ".join(sorted(missing))
            raise CsvProjectError(f"Missing required columns in {path.name}: {missing_columns}")
        return [dict(row) for row in reader]
