#!/usr/bin/env python3
"""Azure DevOps Boards / Test Plans helper for QA Trust Architect (stdlib only).

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
  create-bug --input def.json --key <workItemKey> [--requirement <id>] [--test-cases 1,2]
             [--attach file ...] [--type Bug] [--copy-area-iteration]
      Create a defect from a CONFIRMED canonical defect (refuses drafts). Idempotent via the
      tag qa-def:<key>/<DEF-id>. Prints {"id": <id>, "action": "created|existing"}.
  get-states --ids 1,2,3
      Print {"<id>": {"state": ..., "reason": ...}} for work items.
  comment --id <id> --text-file note.md [--state <state>]
      Add a comment (Markdown) and optionally change state.
  publish-run --input run.json --plan <planId> --suite <suiteId>
      Create a test run for the given test cases' points, set outcomes, complete it.
      Prints {"runId": .., "results": {"<tcId>": <resultId>}, "skipped": [..]}.
  convert / convert-bug --input <file>
      Dry run: print what would be sent, without calling ADO.
"""
import argparse
import base64
import datetime
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

    def upload(self, file_path):
        """Upload an attachment; returns its URL."""
        name = os.path.basename(file_path)
        url = f"{self.base}/_apis/wit/attachments?fileName={urllib.parse.quote(name)}&api-version={API}"
        with open(file_path, "rb") as f:
            data = f.read()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", self.auth)
        req.add_header("Content-Type", "application/octet-stream")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())["url"]
        except urllib.error.HTTPError as e:
            sys.exit(f"ADO attachment upload failed for {name}: {e.code} {e.read().decode(errors='replace')[:300]}")

    def call(self, method, path, body=None, content_type="application/json", api=API):
        sep = "&" if "?" in path else "?"
        url = f"{self.base}/_apis/{path}{sep}api-version={api}"
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


# ── defects ───────────────────────────────────────────────────────────────

SEVERITY = {"Sev1": "1 - Critical", "Sev2": "2 - High", "Sev3": "3 - Medium", "Sev4": "4 - Low"}


def _env_text(d):
    return ", ".join(x for x in [d.get("environment"), d.get("build") and f"build {d['build']}"] if x)


def build_repro_html(d):
    parts = ["<ol>" + "".join(f"<li>{escape(s)}</li>" for s in d.get("stepsToReproduce", [])) + "</ol>"]
    parts.append(f"<p><b>Expected:</b> {escape(d.get('expected', ''))}</p>")
    parts.append(f"<p><b>Actual:</b> {escape(d.get('actual', ''))}</p>")
    if _env_text(d):
        parts.append(f"<p><b>Environment:</b> {escape(_env_text(d))}</p>")
    tr = d.get("traces", {}) or {}
    refs = []
    for k in ("testCases", "acceptanceCriteria", "rules", "runs", "features"):
        refs += tr.get(k) or []
    if tr.get("session"):
        refs.append(tr["session"])
    if refs:
        parts.append("<p><b>Traces:</b> " + escape(", ".join(refs)) + "</p>")
    if d.get("oracleBasis"):
        parts.append(f"<p><b>Oracle:</b> {escape(d['oracleBasis'])}</p>")
    if d.get("evidence"):
        parts.append("<p><b>Evidence:</b></p><ul>" + "".join(f"<li>{escape(e)}</li>" for e in d["evidence"]) + "</ul>")
    parts.append(f"<p><i>Logged by QA Trust Architect ({escape(d['id'])}), "
                 f"confirmed by {escape(d.get('confirmedBy') or '?')}.</i></p>")
    return "".join(parts)


def bug_fields(d, key, defect_type):
    tags = ["qa-trust", f"qa-def:{key}/{d['id']}"] + ((d.get("traces") or {}).get("features") or [])
    fields = {
        "System.Title": f"{d['id']} {d['title']}"[:255],
        "Microsoft.VSTS.Common.Priority": int(d.get("priority") or 2),
        "System.Tags": "; ".join(dict.fromkeys(tags)),
    }
    repro = build_repro_html(d)
    if defect_type.lower() == "bug":
        fields["Microsoft.VSTS.TCM.ReproSteps"] = repro
        fields["Microsoft.VSTS.Common.Severity"] = SEVERITY.get(d.get("severity"), "3 - Medium")
        if _env_text(d):
            fields["Microsoft.VSTS.TCM.SystemInfo"] = escape(_env_text(d))
    else:  # e.g. Basic process "Issue": no Repro Steps / Severity fields
        fields["System.Description"] = repro
        fields["System.Tags"] += f"; severity:{d.get('severity', 'Sev3')}"
    return fields


def check_confirmed(d):
    if d.get("status") != "confirmed" or not d.get("confirmedBy"):
        sys.exit(f"Refusing to create {d.get('id')}: defect must have status 'confirmed' and 'confirmedBy' set")


def create_bug(ado, args):
    with open(args.input, encoding="utf-8") as f:
        d = json.load(f)
    check_confirmed(d)
    existing = (d.get("externalIds") or {}).get("azure-devops")
    if existing:
        print(json.dumps({"id": existing, "action": "existing"}))
        return
    tag = f"qa-def:{args.key}/{d['id']}"
    wiql = {"query": "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = @project "
                     f"AND [System.Tags] CONTAINS '{tag}'"}
    found = ado.call("POST", "wit/wiql", wiql).get("workItems", [])
    if found:
        print(json.dumps({"id": found[0]["id"], "action": "existing"}))
        return
    for path in args.attach or []:
        if not os.path.isfile(path):
            sys.exit(f"Evidence file not found: {path}")
    fields = bug_fields(d, args.key, args.type)
    if args.requirement and args.copy_area_iteration:
        story = ado.call("GET", f"wit/workitems/{args.requirement}?fields=System.AreaPath,System.IterationPath")
        for name in ("System.AreaPath", "System.IterationPath"):
            if story.get("fields", {}).get(name):
                fields[name] = story["fields"][name]
    ops = [{"op": "add", "path": f"/fields/{k}", "value": v} for k, v in fields.items()]

    def wi(i):
        return f"{ado.base}/_apis/wit/workItems/{i}"

    if args.requirement:
        ops.append({"op": "add", "path": "/relations/-",
                    "value": {"rel": "System.LinkTypes.Related", "url": wi(args.requirement)}})
    for tc in [x.strip() for x in (args.test_cases or "").split(",") if x.strip()]:
        ops.append({"op": "add", "path": "/relations/-",
                    "value": {"rel": "Microsoft.VSTS.Common.TestedBy-Forward", "url": wi(tc)}})
    for path in args.attach or []:
        ops.append({"op": "add", "path": "/relations/-",
                    "value": {"rel": "AttachedFile", "url": ado.upload(path), "attributes": {"comment": d["id"]}}})
    res = ado.call("POST", "wit/workitems/$" + urllib.parse.quote(args.type), ops, "application/json-patch+json")
    print(json.dumps({"id": res.get("id"), "action": "created"}))


def get_states(ado, args):
    ids = ",".join(i.strip() for i in args.ids.split(",") if i.strip())
    res = ado.call("GET", f"wit/workitems?ids={ids}&fields=System.State,System.Reason")
    out = {str(w["id"]): {"state": w["fields"].get("System.State"), "reason": w["fields"].get("System.Reason")}
           for w in res.get("value", [])}
    print(json.dumps(out))


def comment(ado, args):
    with open(args.text_file, encoding="utf-8") as f:
        text = f.read()
    # The work item Comments API is still a preview API in 7.1
    ado.call("POST", f"wit/workItems/{args.id}/comments?format=markdown", {"text": text}, api="7.1-preview.4")
    if args.state:
        ado.call("PATCH", f"wit/workitems/{args.id}",
                 [{"op": "add", "path": "/fields/System.State", "value": args.state}], "application/json-patch+json")
    print(json.dumps({"id": int(args.id), "commented": True, "state": args.state}))


# ── test runs ─────────────────────────────────────────────────────────────

OUTCOME = {"passed": "Passed", "failed": "Failed", "blocked": "Blocked", "skipped": "NotExecuted", "not-run": "NotExecuted"}


def publish_run(ado, args):
    with open(args.input, encoding="utf-8") as f:
        run = json.load(f)
    points, skipped = {}, []
    for r in run.get("results", []):
        tc = str(r["testCaseId"])
        pts = ado.call("GET", f"testplan/Plans/{args.plan}/Suites/{args.suite}/TestPoint?testCaseId={tc}").get("value", [])
        if pts:
            points[tc] = pts[0]["id"]
        else:
            skipped.append(tc)
    if not points:
        print(json.dumps({"runId": None, "results": {}, "skipped": skipped}))
        return
    body = {"name": run.get("name", "QA Trust run")[:256], "plan": {"id": str(args.plan)},
            "pointIds": list(points.values()), "automated": False,
            "comment": f"Environment: {run.get('environment', '')}; build: {run.get('build', '')}"}
    run_id = ado.call("POST", "test/runs", body)["id"]
    results = ado.call("GET", f"test/Runs/{run_id}/results").get("value", [])
    by_point = {str((x.get("testPoint") or {}).get("id")): x["id"] for x in results}
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates, mapping = [], {}
    for r in run.get("results", []):
        tc = str(r["testCaseId"])
        rid = by_point.get(str(points.get(tc)))
        if rid is None:
            continue
        u = {"id": rid, "outcome": OUTCOME.get(r.get("outcome"), "NotExecuted"), "state": "Completed",
             "comment": (r.get("comment") or "")[:1000], "completedDate": now}
        if r.get("durationMs"):
            u["durationInMs"] = r["durationMs"]
        if r.get("bugIds"):
            u["associatedBugs"] = [{"id": str(b)} for b in r["bugIds"]]
        updates.append(u)
        mapping[tc] = rid
    if updates:
        ado.call("PATCH", f"test/Runs/{run_id}/results", updates)
    ado.call("PATCH", f"test/runs/{run_id}", {"state": "Completed"})
    print(json.dumps({"runId": run_id, "results": mapping, "skipped": skipped}))


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
    b = sub.add_parser("create-bug"); b.add_argument("--input", required=True); b.add_argument("--key", required=True)
    b.add_argument("--requirement"); b.add_argument("--test-cases"); b.add_argument("--attach", nargs="*")
    b.add_argument("--type", default="Bug"); b.add_argument("--copy-area-iteration", action="store_true")
    g = sub.add_parser("get-states"); g.add_argument("--ids", required=True)
    c = sub.add_parser("comment"); c.add_argument("--id", required=True); c.add_argument("--text-file", required=True); c.add_argument("--state")
    r = sub.add_parser("publish-run"); r.add_argument("--input", required=True); r.add_argument("--plan", required=True); r.add_argument("--suite", required=True)
    sub.add_parser("convert", help="Dry run: print ADO fields for --input without calling ADO").add_argument("--input", required=True)
    cb = sub.add_parser("convert-bug", help="Dry run: print ADO bug fields for a defect JSON")
    cb.add_argument("--input", required=True); cb.add_argument("--key", default="KEY"); cb.add_argument("--type", default="Bug")
    args = p.parse_args()

    if args.cmd == "convert-bug":
        with open(args.input, encoding="utf-8") as f:
            d = json.load(f)
        print(json.dumps({"confirmed": d.get("status") == "confirmed" and bool(d.get("confirmedBy")),
                          "fields": bug_fields(d, args.key, args.type)}, indent=2))
        return

    if args.cmd == "convert":
        with open(args.input, encoding="utf-8") as f:
            tc = json.load(f)
        steps = gherkin_to_steps(tc["gherkin"]) if tc.get("format") == "gherkin" else tc.get("steps", [])
        print(json.dumps({"steps": steps, "stepsXml": steps_xml(steps), "tags": build_tags(tc)}, indent=2))
        return

    ado = Ado(args.org_url, args.project)
    {"upsert-testcase": upsert_testcase, "ensure-suite": ensure_suite, "add-to-suite": add_to_suite,
     "create-bug": create_bug, "get-states": get_states, "comment": comment,
     "publish-run": publish_run}[args.cmd](ado, args)


if __name__ == "__main__":
    main()
