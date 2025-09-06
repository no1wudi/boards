# AGENTS.md

## Build, Lint, and Test Commands
- Configure NuttX: `python configure.py --nuttx <nuttx_dir> <board_config>`
  - Add `--cmake` for CMake-based builds
- Flash firmware: `python flash.py <nuttx_dir> [--port <port>]`
- Simulate board: `python simulate.py <nuttx_dir> [--qemu-options ...]`
- Serial terminal: `python term.py <nuttx_dir> [--port <port>]`
- No direct test/lint runner; run scripts individually via CLI

## Code Style Guidelines
- Follow PEP8: 4-space indentation, snake_case for functions/variables, CapWords for classes
- Import order: standard library, third-party, local modules
- Use docstrings for all functions/classes; type hints optional
- Error handling: use try/except, print clear errors, exit nonzero on failure
- Naming: descriptive, avoid abbreviations except for well-known terms
- Formatting: max line length 120, prefer f-strings
- Avoid global mutable state; encapsulate logic in classes
- Use argparse for CLI parsing
- Scripts should be executable as main (`if __name__ == "__main__": main()`)
- Use black to auto-format code
