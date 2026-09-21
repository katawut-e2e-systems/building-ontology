from __future__ import annotations

from pathlib import Path

from .csv_loader import load_project
from .models import OntologyProject
from .ttl_writer import render_module


def load_ontology_project(input_dir: str | Path) -> OntologyProject:
    return load_project(Path(input_dir))


def build_ontology_project(input_dir: str | Path, output_dir: str | Path) -> list[Path]:
    project = load_ontology_project(input_dir)
    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    written_files: list[Path] = []

    for module in project.modules:
        target = _resolve_output_path(output_root, module.output_file)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_module(project.prefixes, module), encoding="utf-8")
        written_files.append(target)

    return written_files


def _resolve_output_path(output_root: Path, output_file: str) -> Path:
    if not output_file.strip():
        raise ValueError("Ontology output path must not be empty")
    relative_path = Path(output_file)
    if relative_path.is_absolute():
        raise ValueError(f"Ontology output path must be relative: {output_file}")
    target = (output_root / relative_path).resolve()
    try:
        target.relative_to(output_root)
    except ValueError as error:
        raise ValueError(f"Ontology output path escapes output directory: {output_file}") from error
    return target
