#!/usr/bin/env python3
"""Local test runner for PA2.

Part 1 - grammar (grammar/TOMLLexer.g4 + grammar/TOMLParser.g4):
    test/part1/valid/*.in.toml    parser.toml() must report no syntax errors
    test/part1/invalid/*.in.toml  parser.toml() must report at least one error

    The judge only looks at this observable behaviour, never at the shape of
    the parse tree, so any correct way of splitting the grammar passes.
    See test/part1/README.md.

Part 2 - formatter, no comments involved (build/toml_formatter):
    test/part2/*.in.toml          output must equal *.out.toml exactly

Part 3 - formatter, comments preserved:
    test/part3/*.in.toml          output must equal *.out.toml exactly

Usage:
    python3 run_tests.py            run all three parts
    python3 run_tests.py --part1    run only Part 1 (grammar)
    python3 run_tests.py --part2    run only Part 2 (formatting)
    python3 run_tests.py --part3    run only Part 3 (comments)

Part 1 needs a JDK (javac) and the ANTLR tool jar, found via $ANTLR_JAR or
lib/antlr-*.jar.
"""
import argparse
import difflib
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, "build")
BIN = os.path.join(BUILD_DIR, "toml_formatter")
GRAMMAR_DIR = os.path.join(ROOT, "grammar")
TEST_DIR = os.path.join(ROOT, "test")
PART1_DIR = os.path.join(TEST_DIR, "part1")
PART2_DIR = os.path.join(TEST_DIR, "part2")
PART3_DIR = os.path.join(TEST_DIR, "part3")

ERROR_RE = re.compile(r"^errors=(\d+)$", re.M)

if sys.stdout.isatty():
    GREEN, RED, RESET = "\033[0;32m", "\033[0;31m", "\033[0m"
else:
    GREEN = RED = RESET = ""


def report_case(name, passed, elapsed_ms, detail=""):
    if passed:
        print(f"{GREEN}[       OK ]{RESET} {name} ({elapsed_ms} ms)")
    else:
        print(f"{RED}[  FAILED  ]{RESET} {name} ({elapsed_ms} ms)")
        for line in detail.splitlines():
            print(f"  {line}")


def diff_detail(expected, actual, limit=30):
    lines = list(difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected", tofile="actual"))
    if len(lines) > limit:
        lines = lines[:limit] + ["...\n"]
    return "".join(lines).rstrip("\n")


def find_antlr_jar():
    candidates = [os.environ.get("ANTLR_JAR", "")]
    candidates += sorted(glob.glob(os.path.join(ROOT, "lib", "antlr-*.jar")))
    candidates += sorted(glob.glob("lib/antlr-*.jar"))
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


def build_part1_harness():
    """Generate + compile the Java target of the grammar and the helper.

    Returns (tmp_dir, classpath, error_message).
    """
    jar = find_antlr_jar()
    if jar is None:
        return None, None, ("ANTLR jar not found; set $ANTLR_JAR or put "
                            "antlr-*.jar under ./lib/")
    if shutil.which("javac") is None:
        return None, None, "javac not found; Part 1 needs a JDK"

    tmp = tempfile.mkdtemp(prefix="pa2_part1_")
    for g4 in sorted(glob.glob(os.path.join(GRAMMAR_DIR, "*.g4"))):
        shutil.copy(g4, tmp)
    helper = os.path.join(PART1_DIR, "ParseCheck.java")
    if not os.path.isfile(helper):
        shutil.rmtree(tmp, ignore_errors=True)
        return None, None, f"{helper} is missing"
    shutil.copy(helper, tmp)

    gen = subprocess.run(
        ["java", "-jar", jar, "TOMLLexer.g4", "TOMLParser.g4"],
        cwd=tmp, capture_output=True, text=True, timeout=180)
    if gen.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        return None, None, ("failed to generate Java sources from grammar/:\n"
                            + (gen.stderr.strip() or gen.stdout.strip()))

    java_files = sorted(glob.glob(os.path.join(tmp, "*.java")))
    build = subprocess.run(
        ["javac", "-cp", jar] + [os.path.basename(f) for f in java_files],
        cwd=tmp, capture_output=True, text=True, timeout=300)
    if build.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        return None, None, ("javac failed on the generated grammar:\n"
                            + build.stderr.strip())
    return tmp, tmp + os.pathsep + jar, None


def run_part1():
    print("[----------] Part 1: grammar (TOMLParser.g4)")
    valid = sorted(glob.glob(os.path.join(PART1_DIR, "valid", "*.in.toml")))
    invalid = sorted(glob.glob(os.path.join(PART1_DIR, "invalid", "*.in.toml")))
    cases = [(path, True) for path in valid] + [(path, False) for path in invalid]
    if not cases:
        print(f"{RED}[  ERROR   ]{RESET} no cases found under {PART1_DIR}")
        return 0, 0, []

    tmp, classpath, error = build_part1_harness()
    if classpath is None:
        print(f"{RED}[  ERROR   ]{RESET} {error}")
        return 0, len(cases), ["part1/*"]

    passed, failed = 0, []
    try:
        for in_path, want_valid in cases:
            directory = "valid" if want_valid else "invalid"
            stem = os.path.basename(in_path)[: -len(".in.toml")]
            name = f"part1/{directory}/{stem}"
            print(f"[ RUN      ] {name}")
            start = time.perf_counter()
            result = subprocess.run(
                ["java", "-cp", classpath, "ParseCheck", in_path],
                capture_output=True, text=True, timeout=60)
            elapsed = int((time.perf_counter() - start) * 1000)

            match = ERROR_RE.search(result.stdout)
            errors = int(match.group(1)) if match else -1
            if result.returncode != 0 or errors < 0:
                ok = False
                detail = "could not run the parser:\n" + result.stderr.strip()
            elif want_valid:
                ok = errors == 0
                detail = ("" if ok else
                          f"expected a clean parse, got {errors} syntax error(s)")
            else:
                ok = errors >= 1
                detail = ("" if ok else
                          "input was accepted by parser.toml(); it must be rejected")
            if not ok:
                tree = next((line for line in result.stdout.splitlines()
                             if line.startswith("tree=")), "")
                if tree:
                    detail = (detail + "\n" + tree).strip()

            report_case(name, ok, elapsed, detail)
            passed += ok
            if not ok:
                failed.append(name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return passed, len(cases), failed


def ensure_binary():
    if os.path.exists(BIN):
        return None
    cfg = subprocess.run(["cmake", "-S", ROOT, "-B", BUILD_DIR],
                         capture_output=True, text=True)
    if cfg.returncode != 0:
        return "cmake configure failed:\n" + (cfg.stderr or cfg.stdout).strip()
    build = subprocess.run(["cmake", "--build", BUILD_DIR, "-j"],
                           capture_output=True, text=True)
    if build.returncode != 0:
        return "cmake build failed:\n" + (build.stderr or build.stdout).strip()
    if not os.path.exists(BIN):
        return f"{BIN} not found after building"
    return None


def run_formatter(case_dir, label):
    print(f"[----------] {label}")
    cases = sorted(glob.glob(os.path.join(case_dir, "*.in.toml")))
    if not cases:
        print(f"{RED}[  ERROR   ]{RESET} no cases found in {case_dir}")
        return 0, 0, []

    error = ensure_binary()
    if error is not None:
        print(f"{RED}[  ERROR   ]{RESET} {error}")
        return 0, len(cases), [f"{os.path.basename(case_dir)}/*"]

    passed, failed = 0, []
    for in_path in cases:
        name = f"{os.path.basename(case_dir)}/" + os.path.basename(in_path)[: -len(".in.toml")]
        print(f"[ RUN      ] {name}")
        start = time.perf_counter()
        result = subprocess.run([BIN, in_path], capture_output=True, text=True)
        elapsed = int((time.perf_counter() - start) * 1000)
        out_path = in_path[: -len(".in.toml")] + ".out.toml"
        with open(out_path, encoding="utf-8") as f:
            expected = f.read()
        # Formatting must match byte for byte, so no whitespace normalisation.
        ok = result.returncode == 0 and result.stdout == expected
        detail = "" if ok else diff_detail(expected, result.stdout)
        if result.returncode != 0 and result.stderr.strip():
            detail = (detail + "\n" + result.stderr.strip()).strip()
        report_case(name, ok, elapsed, detail)
        passed += ok
        if not ok:
            failed.append(name)
    return passed, len(cases), failed


def main():
    parser = argparse.ArgumentParser(description="Run PA2 tests.")
    parser.add_argument("--part1", action="store_true",
                        help="run only Part 1 (grammar)")
    parser.add_argument("--part2", action="store_true",
                        help="run only Part 2 (formatting)")
    parser.add_argument("--part3", action="store_true",
                        help="run only Part 3 (comments)")
    args = parser.parse_args()
    selected = args.part1 or args.part2 or args.part3
    run_p1 = args.part1 or not selected
    run_p2 = args.part2 or not selected
    run_p3 = args.part3 or not selected

    start = time.perf_counter()
    print("[==========] PA2: Part 1 (grammar) + Part 2 (formatting) + Part 3 (comments)")

    p1 = p2 = p3 = (0, 0, [])
    if run_p1:
        p1 = run_part1()
        print(f"[----------] Part 1: {p1[0]}/{p1[1]} passed")
    if run_p2:
        p2 = run_formatter(PART2_DIR, "Part 2: formatting (toml_formatter)")
        print(f"[----------] Part 2: {p2[0]}/{p2[1]} passed")
    if run_p3:
        p3 = run_formatter(PART3_DIR, "Part 3: comments (toml_formatter)")
        print(f"[----------] Part 3: {p3[0]}/{p3[1]} passed")

    total_ms = int((time.perf_counter() - start) * 1000)
    passed = p1[0] + p2[0] + p3[0]
    total = p1[1] + p2[1] + p3[1]
    failed = p1[2] + p2[2] + p3[2]
    parts = []
    if run_p1:
        parts.append(f"Part 1: {p1[0]}/{p1[1]}")
    if run_p2:
        parts.append(f"Part 2: {p2[0]}/{p2[1]}")
    if run_p3:
        parts.append(f"Part 3: {p3[0]}/{p3[1]}")
    print(f"[==========] {total} tests ran ({total_ms} ms); {', '.join(parts)}")
    if passed:
        print(f"{GREEN}[  PASSED  ]{RESET} {passed} tests.")
    if failed:
        print(f"{RED}[  FAILED  ]{RESET} {len(failed)} tests, listed below:")
        for name in failed:
            print(f"{RED}[  FAILED  ]{RESET} {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
