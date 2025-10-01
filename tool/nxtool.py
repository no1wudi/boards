#!/usr/bin/env python3

"""
nxtool - Unified CLI tool for NuttX board development tasks.
Consolidates functionality from build, configure, flash, and terminal modules.
"""

import os
import sys

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.commands import main

if __name__ == "__main__":
    main()
