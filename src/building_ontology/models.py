from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Prefix:
    prefix: str
    namespace: str


@dataclass(frozen=True)
class Triple:
    module_id: str
    subject: str
    predicate: str
    object_value: str
    object_kind: str = "qname"
    datatype: str | None = None
    language: str | None = None


@dataclass
class OntologyModule:
    module_id: str
    ontology_uri: str
    label: str
    output_file: str
    imports: list[str] = field(default_factory=list)
    triples: list[Triple] = field(default_factory=list)


@dataclass
class OntologyProject:
    prefixes: list[Prefix]
    modules: list[OntologyModule]
