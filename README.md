# Scratch Dynaconf

Here I'll experiment trying to implement dynaconf from scratch,
so I can test the design solutions I have in mind for it.

## Backlog

- core:
    - [x] Implement core Tree components (nodes, bucket, setting, etc)
    - Implement basic Tree crud and basic conveniences

- docs:
    - Add and setup mkdocs documentation
    - Add API Reference, examples and doc tests for Tree + Tree components

- operations:
    - Implement public settings acessor with raw type evaluation
    - Implement @format evaluation with string interpolation

- general:
    - organize modules "export names". Eg. `from core import Tree, PathNode`
    - organize shared types and types of classes (to avoid circular imports)


## Design (WIP)

Module roles:

- operations:
    responsible for specialized operations
- managers:
    responsible for calling and orchestrating operations
- shell:
    responsible for providing UI/UX

Module structure:

- core: core data store and retrieve operations (data-struct)
- io: data stream operations
- validation: data validation operations
- evaluation: data evaluation operations

## Details (WIP)

- io
    - files: toml, yaml, etc
    - memory:
        - env: env variables
        - python: python objects
        - services: redis, vault, etc

- evaluation

