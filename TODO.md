# OnTrack TODO


---


###  `tests/` — no `__init__.py`

`tests/` has no `__init__.py`. While `pytest` discovers tests without it, absolute
imports inside tests (e.g. `from core.solver import ...`) require the repo root on
`sys.path`. This works with `pytest` run from the `ontrack/` directory but may fail
when run from the repo root or in certain CI configurations.

**TODO:** Add an empty `tests/__init__.py`, or add `pythonpath = ["."]` to
`pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

---


