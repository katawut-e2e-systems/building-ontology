# building-ontology

CSV-driven Python project for generating Turtle (`.ttl`) ontology files with Brick, BOT, and custom schema prefixes.

## Project layout

```text
data/building-management-csv/   Example CSV source data
ontology/                       Generated ontology output
src/building_ontology/          Python package and CLI
tests/                          Regression tests
```

## CSV contract

The builder expects three CSV files in an input directory:

- `prefixes.csv`: Turtle prefixes shared by every generated file.
- `ontologies.csv`: one row per output ontology module with its URI, label, output path, and imported ontologies.
- `triples.csv`: RDF statements for each module.

### prefixes.csv

| column | meaning |
| --- | --- |
| `prefix` | QName prefix used in Turtle |
| `namespace` | Namespace IRI for the prefix |

### ontologies.csv

| column | meaning |
| --- | --- |
| `module_id` | Logical module key used by `triples.csv` |
| `ontology_uri` | Ontology IRI written at the top of the file |
| `label` | `rdfs:label` for the ontology |
| `output_file` | Relative path written under the selected output directory |
| `imports` | Pipe-delimited list of ontology IRIs imported by the module |

### triples.csv

| column | meaning |
| --- | --- |
| `module_id` | Target module from `ontologies.csv` |
| `subject` | RDF subject, typically a QName |
| `predicate` | RDF predicate, typically a QName or `a` |
| `object` | RDF object value |
| `object_kind` | `qname`, `iri`, or `literal` |
| `datatype` | Optional literal datatype QName |
| `language` | Optional literal language tag |

Custom schemas are supported by adding their prefixes to `prefixes.csv` and using those QNames in `triples.csv`.

## Usage

Generate the example ontology files in this repository:

```bash
PYTHONPATH=src python -m building_ontology data/building-management-csv ontology
```

Or install the package and use the console script:

```bash
pip install -e .
build-ontology data/building-management-csv ontology
```

## Example output structure

```text
ontology/
├── building-management.ttl
└── modules/
    ├── composition.ttl
    ├── controls.ttl
    ├── electrical-systems.ttl
    ├── hvac-systems.ttl
    └── site-structure.ttl
```

## Generated example responsibilities

- `ontology/building-management.ttl`: root ontology and imports.
- `ontology/modules/site-structure.ttl`: campus/building/storey/space topology.
- `ontology/modules/hvac-systems.ttl`: HVAC assets, relationships, and sensing points.
- `ontology/modules/electrical-systems.ttl`: electrical panels, metering, and lighting assets.
- `ontology/modules/controls.ttl`: BMS/control-level assets and related telemetry points.
- `ontology/modules/composition.ttl`: assembly layer that imports and composes the other modules.
