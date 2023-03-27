# User Interface


## Appshell

Object that provided dot access and other utilities acess
to settings.

### Auto-completion and Type Hints

Should provide both, like so:

```python
settings = Appshell(Settings)
settings.age

# while typing
settings.a # suggest: 'age'

reveal_type(settings.age) # out: int
```

But how this auto-completions and type hints work?

