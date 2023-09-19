# [WIP] ConfigX - Settings Management

<!--toc:start-->
- [[WIP] ConfigX - Settings Management](#wip-configx-settings-management)
  - [Prototype Phase](#prototype-phase)
    - [What's new](#whats-new)
    - [Installing and Testing](#installing-and-testing)
<!--toc:end-->

## Prototype Phase

The purpose of this branch is to build a proof-of-concept of some new design ideas
involving analogies with front-end concept Virtual-Dom. The code and tests should
be as minimal as possible to make the core data-flow work properly, with the expected
transformations.

Optimizations can be addressed later, as the validation of this will provide greater
modularity.

### What's new

When compared to the previous draft, some new terminology, ideas and concepts are:

- ElementNode vs ComponentNode (by extension, Pure and Mixed trees)
- Reconcile process
- Diff-based merge
- Validation on the lib frontend
- More robust Node API (class types + meteadata property)

### Installing and Testing

The prototype project is under src/proto and tests are in tests/proto.

```bash
poetry install
pytest --no-summary -v
```
