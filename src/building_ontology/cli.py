from __future__ import annotations

import argparse
from pathlib import Path

from .ontology import build_ontology_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build-ontology",
        description="Generate Turtle ontology files from CSV source data.",
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing prefixes.csv, ontologies.csv, and triples.csv")
    parser.add_argument("output_dir", type=Path, help="Directory where generated .ttl files will be written")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    written_files = build_ontology_project(args.input_dir, args.output_dir)
    for path in written_files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
