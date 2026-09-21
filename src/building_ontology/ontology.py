from __future__ import annotations

from pathlib import Path

from .csv_loader import load_project
from .models import OntologyProject
from .ttl_writer import render_module


def load_ontology_project(input_dir: str | Path) -> OntologyProject:
    return load_project(Path(input_dir))


def build_ontology_project(input_dir: str | Path, output_dir: str | Path) -> list[Path]:
    project = load_ontology_project(input_dir)
    output_root = Path(output_dir)
    written_files: list[Path] = []

    for module in project.modules:
        target = output_root / module.output_file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_module(project.prefixes, module), encoding="utf-8")
        written_files.append(target)

    return written_files
