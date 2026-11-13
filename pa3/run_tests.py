#!/usr/bin/env python3
"""Local test runner for PA3.

Part 1 generates a Java parser in a temporary directory and uses ParseCheck,
the same grammar-only harness as Gradescope. It needs a JDK but no C++ code.
Part 2 and Part 3 are separate executables:
  * build/sysy_typecheck  -> type-check diagnostics on stderr (Part 2),
  * build/sysy_callgraph  -> Mermaid call graph on stdout (Part 3).

Test layout (local convenience; the OJ uses its own hidden cases):
  test/part1/valid/*.c     syntactically valid programs   (zero syntax errors)
  test/part1/invalid/*.c   syntactically invalid programs  (syntax errors)
  test/part2/<name>.c + .ans   Part 2 expected stderr
                               (only "Error type N at Line M" and the
                                "No semantic errors..." line are compared)
  test/part3/<name>.c + .ans   Part 3 expected stdout (Mermaid, exact)

As in PA2, every part2/part3 case is named `public_testN` or `hidden_testN`.
The two prefixes are the two case types: the local runner runs both, while the
OJ keeps the hidden cases private.

Usage:
    python3 run_tests.py             run all parts
    python3 run_tests.py --part1    Part 1 (grammar) only
    python3 run_tests.py --part2    Part 2 (type checking) only
    python3 run_tests.py --part3    Part 3 (call graph) only
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
BIN_TYPECHECK = os.path.join(BUILD_DIR, "sysy_typecheck")
BIN_CALLGRAPH = os.path.join(BUILD_DIR, "sysy_callgraph")
TEST_DIR = os.path.join(ROOT, "test")
PART1_DIR = os.path.join(TEST_DIR, "part1")
PART2_DIR = os.path.join(TEST_DIR, "part2")
PART3_DIR = os.path.join(TEST_DIR, "part3")

ERROR_PREFIX = re.compile(r"^(Error type \d+ at Line \d+)")


def case_kind(stem):
    """Classify a case by its filename prefix (public_ / hidden_)."""
    if stem.startswith("public_"):
        return "public"
    if stem.startswith("hidden_"):
        return "hidden"
    return "other"


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


def normalize_stderr(text):
    """Keep only the parts the judge looks at: error kind + line number."""
    kept = []
    for line in text.splitlines():
        m = ERROR_PREFIX.match(line)
        if m:
            kept.append(m.group(1))
        elif line.strip():
            kept.append(line.strip())
    return "\n".join(kept)


def ensure_binary(binary):
    """Build `binary` (its CMake target has the same name) if it is missing.

    Building only this one target keeps Part 2 and Part 3 independent: a
    submission that implements just one part still builds and runs.
    """
    if os.path.exists(binary):
        return None
    cfg = subprocess.run(["cmake", "-S", ROOT, "-B", BUILD_DIR],
                         capture_output=True, text=True)
    if cfg.returncode != 0:
        return "cmake configure failed:\n" + (cfg.stderr or cfg.stdout).strip()
    target = os.path.basename(binary)
    build = subprocess.run(["cmake", "--build", BUILD_DIR, "--target", target,
                            "-j"], capture_output=True, text=True)
    if build.returncode != 0:
        return (f"cmake build of {target} failed:\n"
                + (build.stderr or build.stdout).strip())
    if not os.path.exists(binary):
        return f"{binary} not found after building"
    return None


def prepare_part1(work):
    """Generate and compile only the grammar, without CMake or student C++."""
    jar = os.environ.get("ANTLR_JAR")
    if jar:
        jar = os.path.abspath(jar)
    else:
        jars = sorted(glob.glob(os.path.join(ROOT, "lib", "antlr-*-complete.jar")))
        if not jars:
            raise RuntimeError("lib/ 下未找到 ANTLR jar")
        jar = jars[0]
    for name in ("SysYLexer.g4", "SysYParser.g4"):
        shutil.copy2(os.path.join(ROOT, "grammar", name), work)
    shutil.copy2(os.path.join(PART1_DIR, "ParseCheck.java"), work)
    result = subprocess.run(
        ["java", "-jar", jar, "SysYLexer.g4", "SysYParser.g4"],
        cwd=work, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError("ANTLR generation failed:\n" +
                           (result.stderr or result.stdout).strip())
    sources = sorted(glob.glob(os.path.join(work, "*.java")))
    result = subprocess.run(["javac", "-cp", jar, *sources], cwd=work,
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError("javac failed:\n" +
                           (result.stderr or result.stdout).strip())
    return work + os.pathsep + jar


def run_part1():
    print("[----------] Part 1: grammar (valid / invalid syntax)")
    cases = ([(p, True) for p in sorted(glob.glob(
        os.path.join(PART1_DIR, "valid", "*.c")))] +
        [(p, False) for p in sorted(glob.glob(
            os.path.join(PART1_DIR, "invalid", "*.c")))])
    if not cases:
        print(f"{RED}[  ERROR   ]{RESET} no cases found under {PART1_DIR}")
        return 0, 0, []
    with tempfile.TemporaryDirectory(prefix="pa3_part1_") as work:
        try:
            classpath = prepare_part1(work)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            print(f"{RED}[  ERROR   ]{RESET} Part 1 preparation failed: {exc}")
            return 0, len(cases), ["part1/*"]
        return run_parser_cases(cases, classpath)


def run_parser_cases(cases, classpath):
    passed, failed = 0, []
    for in_path, want_valid in cases:
        directory = "valid" if want_valid else "invalid"
        name = f"part1/{directory}/" + os.path.basename(in_path)[:-2]
        print(f"[ RUN      ] {name}")
        start = time.perf_counter()
        try:
            result = subprocess.run(["java", "-cp", classpath, "ParseCheck", in_path],
                                    capture_output=True, text=True, timeout=10)
            match = re.search(r"^errors=(\d+)$", result.stdout, re.M)
            errors = int(match.group(1)) if match else None
            ok = (result.returncode == 0 and errors is not None and
                  ((errors == 0) if want_valid else (errors > 0)))
            detail = "" if ok else (
                f"expected {'zero syntax errors' if want_valid else 'syntax errors'}, "
                f"got exit {result.returncode}, errors={errors}\n{result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            ok, detail = False, str(exc)
        elapsed = int((time.perf_counter() - start) * 1000)
        report_case(name, ok, elapsed, detail)
        passed += ok
        if not ok:
            failed.append(name)
    return passed, len(cases), failed


def run_output_cases(case_dir, label, binary, stream, normalize=None):
    print(f"[----------] {label}")
    cases = sorted(glob.glob(os.path.join(case_dir, "*.c")))
    if not cases:
        print(f"{RED}[  ERROR   ]{RESET} no cases found in {case_dir}")
        return 0, 0, []
    error = ensure_binary(binary)
    if error:
        print(f"{RED}[  ERROR   ]{RESET} {error}")
        return 0, len(cases), [f"{os.path.basename(case_dir)}/*"]

    passed, failed = 0, []
    by_kind = {}
    for in_path in cases:
        stem = os.path.basename(in_path)[:-2]
        name = os.path.basename(case_dir) + "/" + stem
        kind = case_kind(stem)
        by_kind.setdefault(kind, [0, 0])
        print(f"[ RUN      ] {name}")
        start = time.perf_counter()
        result = subprocess.run([binary, in_path], capture_output=True, text=True)
        elapsed = int((time.perf_counter() - start) * 1000)
        ans_path = in_path[:-2] + ".ans"
        with open(ans_path, encoding="utf-8") as f:
            expected = f.read()
        actual = result.stderr if stream == "stderr" else result.stdout
        if normalize:
            expected, actual = normalize(expected), normalize(actual)
        ok = result.returncode == 0 and expected == actual
        detail = "" if ok else diff_detail(expected, actual)
        if result.returncode != 0 and result.stderr.strip():
            detail = (detail + "\n" + result.stderr.strip()).strip()
        report_case(name, ok, elapsed, detail)
        passed += ok
        by_kind[kind][0] += ok
        by_kind[kind][1] += 1
        if not ok:
            failed.append(name)
    summary = ", ".join(f"{kind} {ok}/{total}"
                        for kind, (ok, total) in sorted(by_kind.items()))
    if summary:
        print(f"[----------]   {summary}")
    return passed, len(cases), failed


def main():
    parser = argparse.ArgumentParser(description="Run PA3 tests.")
    parser.add_argument("--part1", action="store_true", help="Part 1 (grammar) only")
    parser.add_argument("--part2", action="store_true", help="Part 2 (type checking) only")
    parser.add_argument("--part3", action="store_true", help="Part 3 (call graph) only")
    args = parser.parse_args()
    selected = args.part1 or args.part2 or args.part3
    run_p1 = args.part1 or not selected
    run_p2 = args.part2 or not selected
    run_p3 = args.part3 or not selected

    start = time.perf_counter()
    print("[==========] PA3: Part 1 (grammar) + Part 2 (type check) + Part 3 (call graph)")

    p1 = p2 = p3 = (0, 0, [])
    if run_p1:
        p1 = run_part1()
        print(f"[----------] Part 1: {p1[0]}/{p1[1]} passed")
    if run_p2:
        p2 = run_output_cases(PART2_DIR, "Part 2: type checking (stderr)",
                              BIN_TYPECHECK, "stderr", normalize_stderr)
        print(f"[----------] Part 2: {p2[0]}/{p2[1]} passed")
    if run_p3:
        p3 = run_output_cases(PART3_DIR, "Part 3: call graph (stdout)",
                              BIN_CALLGRAPH, "stdout")
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
