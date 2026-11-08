#!/usr/bin/env python3
"""Azure DevOps Test Plans helper for QA Trust Architect (stdlib only).

Auth: personal access token in env var ADO_PAT (Work Items R/W + Test Management R/W).
Org/project: --org-url / --project, or env ADO_ORG_URL / ADO_PROJECT.

Env file: variables are also loaded from a dotenv file (--env-file, default ./.env in the
current directory = project root). Variables already set in the process environment always
win over the file. Configure the path via `secrets.envFile` in qa-trust.config.yaml.

Commands:
  upsert-testcase --input tc.json [--requirement <workItemId>]
      Create or update a Test Case from a canonical test case (JSON form of
      templates/test-case.*.yaml). Prints {"id": <id>, "action": "created|updated"}.
  ensure-suite --plan <planId> --requirement <workItemId>
      Return (or create) the requirement-based suite for a work item. Prints {"suiteId": <id>}.
  add-to-suite --plan <planId> --suite <suiteId> --ids 1,2,3
      Add existing test cases to a static suite.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

API = "7.1"
AUTOMATION_STATUS = {
    "candidate": "Planned",
    "automated": "Automated",
    "already-automated": "Automated",
    "manual-only": "Not Automated",
    "exploratory": "Not Automated",
}


def load_env_file(path):
    """Minimal dotenv loader: KEY=VALUE lines, # comments, optional quotes, optional 'export '.
    Never overrides variables already present in the environment."""
    if not path or not os.path.isfile(path):
        return 0
    loaded = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            elif " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            if key and key not in os.environ:
                os.environ[key] = value
                loaded += 1
    return loaded


class Ado:
    def __init__(self, org_url, project):
        pat = os.environ.get("ADO_PAT")
        if not pat:
            sys.exit("ADO_PAT environment variable is not set")
        if not org_url or not project:
            sys.exit("Organization URL and project are required (--org-url/--project or ADO_ORG_URL/ADO_PROJECT)")
        self.base = f"{org_url.rstrip('/')}/{urllib.parse.quote(project)}"
        self.auth = "Basic " + base64.b64encode(f":{pat}".encode()).decode()

    def call(self, method, path, body=None, content_type="application/json"):
        sep = "&" if "?" in path else "?"
        url = f"{self.base}/_apis/{path}{sep}api-version={API}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", self.auth)
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            sys.exit(f"ADO {method} {path} failed: {e.code} {e.read().decode(errors='replace')[:500]}")


# ── canonical → ADO conversion ────────────────────────────────────────────

def _param(text):
    """Convert <placeholder> to ADO @parameter syntax."""
    return re.sub(r"<([A-Za-z_][\w-]*)>", r"@\1", text)


def gherkin_to_steps(gherkin):
    steps, given, mode = [], [], None
    for line in gherkin.splitlines():
        s = line.strip()
        if not s or s.startswith(("Scenario", "Examples", "|", "#", "Feature", "Background")):
            continue
        kw, _, rest = s.partition(" ")
        kw = kw.lower()
        if kw == "and" or kw == "but":
            kw = mode or "given"
        if kw == "given":
            given.append(rest)
            mode = "given"
        elif kw == "when":
            steps.append({"action": rest, "expected": ""})
            mode = "when"
        elif kw == "then":
            if not steps:
                steps.append({"action": "(observe)", "expected": ""})
            sep = "; " if steps[-1]["expected"] else ""
            steps[-1]["expected"] += sep + rest
            mode = "then"
    if given:
        steps.insert(0, {"action": "Preconditions: " + "; ".join(given), "expected": ""})
    return steps


def steps_xml(steps):
    parts = [f'<steps id="0" last="{len(steps) + 1}">']
    for i, st in enumerate(steps, start=2):
        a = escape(_param(st.get("action", "")))
        x = escape(_param(st.get("expected", "")))
        stype = "ValidateStep" if x else "ActionStep"
        parts.append(
            f'<step id="{i}" type="{stype}">'
            f'<parameterizedString isformatted="true">{a}</parameterizedString>'
            f'<parameterizedString isformatted="true">{x}</parameterizedString>'
            f"<description/></step>"
        )
    parts.append("</steps>")
    return "".join(parts)


def html_table(columns, rows):
    head = "".join(f"<th>{escape(str(c))}</th>" for c in columns)
    body = "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in r) + "</tr>" for r in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def examples_from_gherkin(gherkin):
    rows = [l.strip() for l in gherkin.splitlines() if l.strip().startswith("|")]
    if not rows:
        return None, None
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    return cells[0], cells[1:]


def build_description(tc):
    parts = [f"<p><b>{escape(tc['id'])}</b> — {escape(tc.get('objective', ''))}</p>"]
    if tc.get("preconditions"):
        parts.append("<p><b>Preconditions</b></p><ul>" + "".join(f"<li>{escape(p)}</li>" for p in tc["preconditions"]) + "</ul>")
    if tc.get("format") == "gherkin":
        cols, rows = examples_from_gherkin(tc.get("gherkin", ""))
        if cols:
            parts.append("<p><b>Examples</b></p>" + html_table(cols, rows))
        parts.append("<p><b>Gherkin</b></p><pre>" + escape(tc.get("gherkin", "")) + "</pre>")
    elif tc.get("data"):
        parts.append("<p><b>Data</b></p>" + html_table(tc["data"]["columns"], tc["data"]["rows"]))
    traces = tc.get("traces", {})
    parts.append("<p><b>Traces</b>: " + escape(", ".join(sum((v for v in traces.values() if isinstance(v, list)), []))) + "</p>")
    if tc.get("basis") == "provisional":
        parts.append("<p><b>Basis: provisional</b> (" + escape(", ".join(tc.get("basisRefs", []))) + ")</p>")
    return "".join(parts)


def build_tags(tc):
    tags = ["qa-trust", tc["id"]]
    tags += tc.get("traces", {}).get("acceptanceCriteria", [])
    tags += tc.get("technique", [])
    if tc.get("basis") == "provisional":
        tags.append("provisional")
    return "; ".join(dict.fromkeys(tags))


# ── commands ──────────────────────────────────────────────────────────────

def upsert_testcase(ado, args):
    with open(args.input, encoding="utf-8") as f:
        tc = json.load(f)
    steps = gherkin_to_steps(tc["gherkin"]) if tc.get("format") == "gherkin" else tc.get("steps", [])
    fields = {
        "System.Title": f"{tc['id']} {tc['title']}",
        "Microsoft.VSTS.Common.Priority": int(tc.get("priority", 2)),
        "Microsoft.VSTS.TCM.Steps": steps_xml(steps),
        "System.Description": build_description(tc),
        "System.Tags": build_tags(tc),
        "Microsoft.VSTS.TCM.AutomationStatus": AUTOMATION_STATUS.get(
            tc.get("automation", {}).get("status", "candidate"), "Not Automated"),
    }
    ops = [{"op": "add", "path": f"/fields/{k}", "value": v} for k, v in fields.items()]
    existing = tc.get("externalIds", {}).get("azure-devops")
    if existing:
        res = ado.call("PATCH", f"wit/workitems/{existing}", ops, "application/json-patch+json")
        action = "updated"
    else:
        if args.requirement:
            ops.append({"op": "add", "path": "/relations/-", "value": {
                "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                "url": f"{ado.base}/_apis/wit/workItems/{args.requirement}"}})
        res = ado.call("POST", "wit/workitems/$Test%20Case", ops, "application/json-patch+json")
        action = "created"
    print(json.dumps({"id": res.get("id"), "action": action}))


def ensure_suite(ado, args):
    plan = ado.call("GET", f"testplan/Plans/{args.plan}")
    suites = ado.call("GET", f"testplan/Plans/{args.plan}/suites").get("value", [])
    for s in suites:
        if s.get("suiteType") == "requirementTestSuite" and str(s.get("requirementId")) == str(args.requirement):
            print(json.dumps({"suiteId": s["id"], "action": "existing"}))
            return
    body = {"suiteType": "requirementTestSuite", "requirementId": int(args.requirement),
            "parentSuite": {"id": plan["rootSuite"]["id"]}, "name": f"Requirement {args.requirement}"}
    res = ado.call("POST", f"testplan/Plans/{args.plan}/suites", body)
    created = res["value"][0] if isinstance(res.get("value"), list) else res
    print(json.dumps({"suiteId": created.get("id"), "action": "created"}))


def add_to_suite(ado, args):
    body = [{"workItem": {"id": int(i)}} for i in args.ids.split(",") if i.strip()]
    ado.call("POST", f"testplan/Plans/{args.plan}/Suites/{args.suite}/TestCase", body)
    print(json.dumps({"added": len(body)}))


def main():
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--env-file", default=".env")
    known, _ = pre.parse_known_args()
    load_env_file(known.env_file)

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--env-file", default=".env", help="dotenv file to load (default ./.env)")
    p.add_argument("--org-url", default=os.environ.get("ADO_ORG_URL"))
    p.add_argument("--project", default=os.environ.get("ADO_PROJECT"))
    sub = p.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("upsert-testcase"); u.add_argument("--input", required=True); u.add_argument("--requirement")
    e = sub.add_parser("ensure-suite"); e.add_argument("--plan", required=True); e.add_argument("--requirement", required=True)
    a = sub.add_parser("add-to-suite"); a.add_argument("--plan", required=True); a.add_argument("--suite", required=True); a.add_argument("--ids", required=True)
    sub.add_parser("convert", help="Dry run: print ADO fields for --input without calling ADO").add_argument("--input", required=True)
    args = p.parse_args()

    if args.cmd == "convert":
        with open(args.input, encoding="utf-8") as f:
            tc = json.load(f)
        steps = gherkin_to_steps(tc["gherkin"]) if tc.get("format") == "gherkin" else tc.get("steps", [])
        print(json.dumps({"steps": steps, "stepsXml": steps_xml(steps), "tags": build_tags(tc)}, indent=2))
        return

    ado = Ado(args.org_url, args.project)
    {"upsert-testcase": upsert_testcase, "ensure-suite": ensure_suite, "add-to-suite": add_to_suite}[args.cmd](ado, args)


if __name__ == "__main__":
    main()
