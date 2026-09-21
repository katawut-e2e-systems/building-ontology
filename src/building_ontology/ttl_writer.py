from __future__ import annotations

from collections import OrderedDict

from .models import OntologyModule, Prefix, Triple


class TurtleRenderError(ValueError):
    """Raised when a Turtle document cannot be rendered."""


def render_module(prefixes: list[Prefix], module: OntologyModule) -> str:
    lines: list[str] = []
    used_prefixes = _used_prefixes(module)
    declared_prefixes = {prefix.prefix for prefix in prefixes}
    missing_prefixes = used_prefixes.difference(declared_prefixes)
    if missing_prefixes:
        missing = ", ".join(sorted(missing_prefixes))
        raise TurtleRenderError(f"Module '{module.module_id}' references undeclared prefixes: {missing}")
    for prefix in prefixes:
        if prefix.prefix not in used_prefixes:
            continue
        lines.append(f"@prefix {prefix.prefix}: <{prefix.namespace}> .")

    lines.append("")
    lines.extend(_render_ontology_block(module))

    grouped = _group_triples_by_subject(module.triples)
    if grouped:
        lines.append("")
        for index, (subject, triples) in enumerate(grouped.items()):
            lines.extend(_render_subject_block(subject, triples))
            if index < len(grouped) - 1:
                lines.append("")

    lines.append("")
    return "\n".join(lines)


def _render_ontology_block(module: OntologyModule) -> list[str]:
    lines = [
        f"<{module.ontology_uri}>",
        "  a owl:Ontology ;",
        f'  rdfs:label "{_escape_literal(module.label)}" ;',
    ]
    if module.imports:
        first_import, *remaining_imports = module.imports
        lines.append(f"  owl:imports <{first_import}>")
        for import_uri in remaining_imports[:-1]:
            lines[-1] = f"{lines[-1]} ,"
            lines.append(f"    <{import_uri}>")
        if remaining_imports:
            lines[-1] = f"{lines[-1]} ,"
            lines.append(f"    <{remaining_imports[-1]}> .")
        else:
            lines[-1] = f"{lines[-1]} ."
    else:
        lines[-1] = lines[-1][:-1] + "."
    return lines


def _used_prefixes(module: OntologyModule) -> set[str]:
    used = {"owl", "rdfs"}
    for triple in module.triples:
        used.update(_extract_prefixes(triple.subject))
        used.update(_extract_prefixes(triple.predicate))
        if triple.object_kind == "qname":
            used.update(_extract_prefixes(triple.object_value))
        if triple.datatype:
            used.update(_extract_prefixes(triple.datatype))
    return used


def _extract_prefixes(value: str) -> set[str]:
    if value == "a" or ":" not in value or value.startswith("<"):
        return set()
    return {value.split(":", maxsplit=1)[0]}


def _group_triples_by_subject(triples: list[Triple]) -> OrderedDict[str, list[Triple]]:
    grouped: OrderedDict[str, list[Triple]] = OrderedDict()
    for triple in triples:
        grouped.setdefault(triple.subject, []).append(triple)
    return grouped


def _render_subject_block(subject: str, triples: list[Triple]) -> list[str]:
    lines = [subject]
    for index, triple in enumerate(triples):
        terminator = " ;" if index < len(triples) - 1 else " ."
        rendered_object = _render_object(triple)
        lines.append(f"  {triple.predicate} {rendered_object}{terminator}")
    return lines


def _render_object(triple: Triple) -> str:
    if triple.object_kind == "qname":
        return triple.object_value
    if triple.object_kind == "iri":
        return f"<{triple.object_value}>"
    if triple.object_kind == "literal":
        literal = f'"{_escape_literal(triple.object_value)}"'
        if triple.datatype:
            return f"{literal}^^{triple.datatype}"
        if triple.language:
            return f"{literal}@{triple.language}"
        return literal
    raise TurtleRenderError(f"Unsupported object kind: {triple.object_kind}")


def _escape_literal(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
