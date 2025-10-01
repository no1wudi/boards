# AGENTS.md

## Build, Lint, and Test Commands
- Configure NuttX: `python nxtool.py configure <board_config> <nuttx_path> [--preset <preset>] [--cmake]`
- Build NuttX: `python nxtool.py build <nuttx_path> [--target <target>]`
- Flash firmware: `python nxtool.py flash <nuttx_path> [--port <port>] [--openocd <path>]`
- Serial terminal: `python nxtool.py term <nuttx_path> [--port <port>] [--python <python_exe>]`
- No direct test/lint runner; run nxtool commands individually via CLI

## Project Structure
```
tool/
├── nxtool.py          # Main CLI entry point
├── core/              # Core functionality modules
│   ├── __init__.py
│   ├── builder.py     # Build logic (Make/CMake)
│   ├── flasher.py     # Flash logic (ESP32/STM32)
│   ├── config.py      # Configuration logic
│   └── terminal.py    # Serial terminal logic
├── utils/             # Utility modules
│   ├── __init__.py
│   ├── kconfig.py     # Kconfig parsing
│   └── helpers.py     # Common utilities
├── cli/               # CLI interface modules
│   ├── __init__.py
│   └── commands.py    # CLI command definitions
└── AGENTS.md          # This file
```

## Code Style Guidelines
- Follow PEP8: 4-space indentation, snake_case for functions/variables, CapWords for classes
- Import order: standard library, third-party, local modules
- Use docstrings for all functions/classes; type hints optional
- Error handling: use try/except, print clear errors, exit nonzero on failure
- Naming: descriptive, avoid abbreviations except for well-known terms
- Formatting: max line length 120, prefer f-strings
- Avoid global mutable state; encapsulate logic in classes
- Use argparse for CLI parsing
- Use black to auto-format code
- Modular design: separate concerns into core/, utils/, and cli/ packages
