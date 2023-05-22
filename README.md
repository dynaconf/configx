# Scratch Dynaconf

Here I'll experiment trying to implement dynaconf from scratch,
so I can test the design solutions I have in mind for it.

## Backlog



## Design

### Layer Architecture

- Shell:
    - lib
    - cli
- Controllers:
    - lib_api
    - cli_api
- Services:
    - storage
    - operations

### Project Structure

```
./lib_shell.py
./cli_shell.py

./setting_tree.py
./core (controllers)
    lib.py
    cli.py
    common.py
./storage
    api.py
    data_structure.py
./operations
    api.py
    loading/
    merging/
    validating/
    evaluating/
```

## Details (WIP)

- io
    - files: toml, yaml, etc
    - memory:
        - env: env variables
        - python: python objects
        - services: redis, vault, etc

- evaluation

