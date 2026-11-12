#!/usr/bin/env python3
"""ste_check.py - compatibility wrapper: same as "python3 scripts/ste.py check FILE ...".

Kept so that existing CI calls keep working. See scripts/ste.py for all options.
Standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ste  # noqa: E402

if __name__ == "__main__":
    sys.exit(ste.main(["check"] + sys.argv[1:]))
