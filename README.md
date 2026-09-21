# building-ontology

Building management ontology with a well-defined Turtle (`.ttl`) structure using Brick and BOT schemas.

## Ontology structure

```text
ontology/
├── building-management.ttl
└── modules/
    ├── site-structure.ttl
    ├── hvac-systems.ttl
    ├── electrical-systems.ttl
    ├── controls.ttl
    └── composition.ttl
```

## File responsibilities

- `ontology/building-management.ttl`: root ontology and imports.
- `ontology/modules/site-structure.ttl`: campus/building/storey/space topology (BOT + Brick classes).
- `ontology/modules/hvac-systems.ttl`: HVAC assets, relationships, and sensing points.
- `ontology/modules/electrical-systems.ttl`: electrical panels, metering, and lighting assets.
- `ontology/modules/controls.ttl`: BMS/control-level assets and related telemetry points.
- `ontology/modules/composition.ttl`: cross-module composition links (e.g., building-to-system asset membership).
