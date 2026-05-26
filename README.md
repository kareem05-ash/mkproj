# mkproj

> A professional, extensible project scaffolding CLI.

[![CI](https://github.com/kareem05-ash/mkproj/actions/workflows/ci.yml/badge.svg)](https://github.com/kareem05-ash/mkproj/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Features

| Capability | Details |
|---|---|
| 🚀 **One-command scaffolding** | `mkproj myapp` creates a full project structure |
| 📁 **Template system** | Folder-based templates — add new ones with zero code changes |
| 🔤 **Token replacement** | `{{project_name}}` replaced in file names and content |
| 🎨 **Rich terminal output** | Colored success/failure messages with a project tree |
| 🧩 **Library API** | Use `from mkproj import create_project` in other tools |
| 🪟 **Cross-platform** | Works on Windows, Linux, and macOS |
| ✅ **Typed & tested** | Full type annotations, mypy strict, pytest suite |

---

## Installation

```bash
git clone https://github.com/kareem05-ash/mkproj.git
cd mkproj
pip install -e ".[dev]"
```

---

## Quick start

```bash
# Default template (cpp)
mkproj myproject

# Select a template
mkproj myproject --template python
mkproj myproject --template cpp

# Create in a specific directory
mkproj myproject --template python --dest ~/projects

# List available templates
mkproj templates
```

### Example output

```
myproject
├── src/
├── include/
├── build/
├── tests/
├── docs/
├── scripts/
├── README.md
├── .gitignore
└── Makefile

╭─────────────────────────────────────────╮
│ ✓ Project created successfully          │
│   Template : cpp                        │
│   Location : /home/user/myproject       │
╰─────────────────────────────────────────╯

  cd /home/user/myproject
```

---

## Available templates

| Template | Description |
|---|---|
| `cpp` | C++17 project with Makefile, src/, include/, tests/ |
| `python` | Python package with pyproject.toml, src layout, tests/ |
| `embedded` | Bare-metal / embedded C project |
| `web` | Static web project with src/, public/, tests/ |

---

## Adding a custom template

1. Create a folder under `templates/`:
   ```
   templates/
   └── mytemplate/
       ├── src/
       ├── README.md
       └── ...
   ```
2. Use `{{project_name}}` anywhere in file **names** or file **content**.
3. Run `mkproj myapp --template mytemplate`. Done.

No code changes required.

---

## Python API

```python
from mkproj import create_project

result = create_project(
    name="myapp",
    template="python",
    destination=Path("~/projects").expanduser(),
)

if result:
    print(f"Created at: {result.project_path}")
else:
    print(f"Failed: {result.error}")
```

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `MKPROJ_DEFAULT_TEMPLATE` | `cpp` | Template used when `--template` is omitted |
| `MKPROJ_ROOT` | CWD | Parent directory for new projects |

Future: `~/.config/mkproj/config.toml` support is architected in — no other changes needed when implemented.

---

## Project structure

```
mkproj/
├── mkproj/
│   ├── __init__.py       # Public API
│   ├── cli.py            # Typer CLI + Rich output
│   ├── core.py           # Orchestration: validate → resolve → scaffold
│   ├── engine.py         # Filesystem engine (copy, mkdir, token replace)
│   ├── config.py         # Configuration resolution
│   └── exceptions.py     # Typed domain exceptions
├── templates/
│   ├── cpp/
│   ├── python/
│   ├── embedded/
│   └── web/
├── tests/
│   ├── test_core.py
│   ├── test_engine.py
│   └── test_cli.py
└── pyproject.toml
```

---

## Running tests

```bash
pytest
pytest --cov=mkproj --cov-report=term-missing
```

---

## Roadmap

- [ ] Interactive mode (`mkproj` with no args)
- [ ] TOML config file (`~/.config/mkproj/config.toml`)
- [ ] Custom template directory (`--templates-dir`)
- [ ] `--dry-run` flag
- [ ] `mkproj init` to initialise templates in current directory
- [ ] git init integration (separate utility)

---

## License

MIT
