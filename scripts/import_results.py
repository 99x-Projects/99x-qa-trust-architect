#!/usr/bin/env python3
"""Normalise automated test result files for QA Trust Architect (stdlib only).

Reads JUnit XML (pytest, Jest/Vitest junit reporters, Playwright, Maven Surefire, Gradle, ...)
and Visual Studio TRX (dotnet test --logger trx) and prints one JSON document:

  {"files": [...], "totals": {"passed": n, "failed": n, "skipped": n, "total": n},
   "tests": [{"name", "classname", "result", "durationMs", "message", "tcIds", "categories", "source"}]}

result is one of passed | failed | skipped. tcIds are QA Trust test case ids (TC-001) found in the
test name, class name, categories/traits or properties — so tag automated tests with their TC id
to get them linked automatically.

Usage:
  python import_results.py <file-or-glob> [...] [--format auto|junit|trx] [--only-failed]
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

TC_RE = re.compile(r"\bTC-\d{3,}\b")
TRX_NS = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"


def tc_ids(*texts):
    found = []
    for t in texts:
        if t:
            found += TC_RE.findall(t)
    return sorted(set(found))


def secs_to_ms(value):
    try:
        return int(round(float(value) * 1000))
    except (TypeError, ValueError):
        return None


def trx_duration_ms(value):
    # "00:00:01.2345678"
    if not value:
        return None
    m = re.match(r"(\d+):(\d+):(\d+(?:\.\d+)?)", value)
    if not m:
        return None
    h, mnt, s = m.groups()
    return int(round((int(h) * 3600 + int(mnt) * 60 + float(s)) * 1000))


def parse_junit(root, source):
    tests = []
    for case in root.iter("testcase"):
        name = case.get("name", "")
        classname = case.get("classname", "") or case.get("class", "")
        result, message = "passed", None
        for child in case:
            tag = child.tag.lower()
            if tag in ("failure", "error"):
                result = "failed"
                message = (child.get("message") or (child.text or "")).strip()[:500]
                break
            if tag == "skipped":
                result = "skipped"
                message = (child.get("message") or "").strip()[:500] or None
        props = [f"{p.get('name', '')}={p.get('value', '')}" for p in case.iter("property")]
        tests.append({
            "name": name, "classname": classname, "result": result,
            "durationMs": secs_to_ms(case.get("time")), "message": message,
            "categories": props, "tcIds": tc_ids(name, classname, *props), "source": source,
        })
    return tests


def parse_trx(root, source):
    categories = {}
    for ut in root.iter(f"{TRX_NS}UnitTest"):
        cats = [c.get("TestCategory", "") for c in ut.iter(f"{TRX_NS}TestCategoryItem")]
        props = [f"{p.findtext(f'{TRX_NS}Key', '')}={p.findtext(f'{TRX_NS}Value', '')}"
                 for p in ut.iter(f"{TRX_NS}Property")]
        method = ut.find(f"{TRX_NS}TestMethod")
        classname = method.get("className", "") if method is not None else ""
        categories[ut.get("id")] = (cats + props, classname)
    outcome_map = {"passed": "passed", "failed": "failed", "error": "failed", "timeout": "failed",
                   "aborted": "failed", "notexecuted": "skipped", "inconclusive": "skipped"}
    tests = []
    for r in root.iter(f"{TRX_NS}UnitTestResult"):
        cats, classname = categories.get(r.get("testId"), ([], ""))
        name = r.get("testName", "")
        result = outcome_map.get((r.get("outcome") or "").lower(), "skipped")
        msg = r.find(f"{TRX_NS}Output/{TRX_NS}ErrorInfo/{TRX_NS}Message")
        tests.append({
            "name": name, "classname": classname, "result": result,
            "durationMs": trx_duration_ms(r.get("duration")),
            "message": (msg.text or "").strip()[:500] if msg is not None and msg.text else None,
            "categories": cats, "tcIds": tc_ids(name, classname, *cats), "source": source,
        })
    return tests


def parse_file(path, fmt):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        sys.exit(f"Cannot parse {path}: {e}")
    if fmt == "auto":
        fmt = "trx" if root.tag.startswith(TRX_NS) or root.tag == "TestRun" else "junit"
    return parse_trx(root, path) if fmt == "trx" else parse_junit(root, path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paths", nargs="+")
    p.add_argument("--format", choices=["auto", "junit", "trx"], default="auto")
    p.add_argument("--only-failed", action="store_true")
    args = p.parse_args()

    files = []
    for pattern in args.paths:
        matches = glob.glob(pattern, recursive=True)
        files += matches if matches else ([pattern] if os.path.isfile(pattern) else [])
    files = sorted(set(files))
    if not files:
        sys.exit("No result files found for: " + " ".join(args.paths))

    tests = []
    for f in files:
        tests += parse_file(f, args.format)
    totals = {k: sum(1 for t in tests if t["result"] == k) for k in ("passed", "failed", "skipped")}
    totals["total"] = len(tests)
    if args.only_failed:
        tests = [t for t in tests if t["result"] == "failed"]
    print(json.dumps({"files": files, "totals": totals, "tests": tests}, indent=2))


if __name__ == "__main__":
    main()
