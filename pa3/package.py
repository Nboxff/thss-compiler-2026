#!/usr/bin/env python3
"""Run "python package.py" in the project root to produce pa3.zip for
submission."""
import os
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(ROOT, "pa3.zip")


def collect_entries():
    entries = [
        ("CMakeLists.txt", "CMakeLists.txt"),
        ("grammar/SysYLexer.g4", "grammar/SysYLexer.g4"),
        ("grammar/SysYParser.g4", "grammar/SysYParser.g4"),
    ]
    include_dir = os.path.join(ROOT, "include")
    for name in sorted(os.listdir(include_dir)):
        rel = os.path.join("include", name)
        entries.append((rel, rel))
    src_dir = os.path.join(ROOT, "src")
    for name in sorted(os.listdir(src_dir)):
        if name.endswith((".cpp", ".h")):
            rel = os.path.join("src", name)
            entries.append((rel, rel))
    return entries


def main():
    # Make sure src/ contains the latest ANTLR4 generated code.
    subprocess.run(["make", "antlr"], cwd=ROOT, check=True)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_rel, arcname in collect_entries():
            zf.write(os.path.join(ROOT, src_rel), arcname)
    print(f"Generated {ZIP_PATH}")


if __name__ == "__main__":
    main()
