#!/usr/bin/env python3
"""QA Trust Architect guard hooks (standard library only).

Hook modes (JSON on stdin, called from hooks/hooks.json through hooks/run-guard.sh):
  pre    PreToolUse  - secret scan on writes, secret-file access, domain write guard,
                       browser (Playwright MCP) environment and action guard
  post   PostToolUse - gate-stale detector

Helper modes (run from the project root):
  hash <ITEM_DIR> <GATE> [extra paths...]
        print the `artifacts:` list for a gate record (canonical sha256 per covered file)
  dcp-window open <DCP-ids> [--minutes N] | close
        open/close the window in which accepted DCPs may be applied to domain files
  status
        print which guards are active for this project

Guards do nothing unless qa-trust.config.yaml exists in the project root. On an internal
error a guard lets the tool call through and prints a warning (fail open); it never prints
secret values - matches are reported by pattern or variable name only.
"""
import datetime
import hashlib
import json
import os
import re
import sys

WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
READ_TOOLS = ("Read", "Grep")
SHELL_TOOLS = ("Bash", "PowerShell")
BROWSER_TOOL = re.compile(r"^mcp__.*playwright.*__browser_", re.I)

DEFAULT_MODES = {
    "secretScan": "block",     # block | warn | off
    "secretFiles": "block",    # block | warn | off
    "domainWrites": "ask",     # ask | warn | block | off
    "gateStale": "mark",       # mark | warn | off
    "browser": "enforce",      # enforce | warn | off
}

# Artifacts each gate covers, relative to ITEM_DIR (a trailing "/" covers a folder).
DEFAULT_COVER = {
    "G1": ["1-inception/requirement.md", "1-inception/requirement-analysis.md",
           "1-inception/acceptance-criteria.md"],
    "G2": ["1-inception/risk-assessment.md", "1-inception/gap-analysis.md",
           "1-inception/test-plan.md"],
    "G3": ["2-design/"],
    "G4": ["3-execution/test-summary-report.md", "3-execution/runs/"],
}
STALE_FROM = ("approved", "approved-with-risks")
# Keys written back by sync / publishing; ignored by the canonical hash.
BOOKKEEPING_KEYS = ("externalIds", "contentHash", "published")

SECRET_NAME = re.compile(r"(PAT|TOKEN|PASS|PASSWD|PASSWORD|PWD|SECRET|KEY|CREDENTIAL|CERT)", re.I)
KNOWN_SECRET_VARS = ("ADO_PAT", "AZURE_DEVOPS_EXT_PAT", "JIRA_API_TOKEN", "XRAY_CLIENT_ID",
                     "XRAY_CLIENT_SECRET", "GITHUB_TOKEN", "GH_TOKEN")

HIGH_CONFIDENCE = [
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("Atlassian API token", re.compile(r"\bATATT3[A-Za-z0-9_=\-]{50,}")),
    ("JSON Web Token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("Azure storage key", re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}")),
    ("Azure DevOps PAT", re.compile(r"\b[A-Za-z0-9]{52}JQQJ99[A-Za-z0-9]{3}AZDO[A-Za-z0-9]{4}\b")),
    ("authorization header", re.compile(r"Authorization\s*:\s*(?:Basic|Bearer)\s+[A-Za-z0-9._~+/=-]{20,}", re.I)),
    ("credentials in URL", re.compile(r"\bhttps?://[^\s:/@]+:[^\s:/@]{6,}@")),
]
# Used only inside the QA root and QA config files (more false positives elsewhere).
LEGACY_ADO_PAT = re.compile(r"(?<![A-Za-z0-9])[a-z2-7]{52}(?![A-Za-z0-9])")
ASSIGNMENT = re.compile(
    r"""["']?[\w.-]*?(?<![A-Za-z])(password|passwd|pwd|passcode|secret|client[_-]?secret|token|"""
    r"""access[_-]?token|api[_-]?key|apikey|pat)["']?\s*[:=]\s*["']?([^\s"',}|#\]]+)["']?"""
    r"""(?=\s*(?:$|[|,;#}\]]))""", re.I | re.M)
REFERENCE_VALUE = re.compile(
    r"^(?:(?i:env:|\$|%|<|\{\{|vault:|keyvault:|secret:|ref:|op://|\*{3}|redacted$|null$|none$|~$|true$|"
    r"false$)|[A-Z][A-Z0-9_]{2,}$|\d+$)")

OUTPUT_START = re.compile(
    r"^\s*(echo|printf|print|write-output|write-host|write-information|out-file|set-content|add-content|"
    r"tee|curl|wget|invoke-restmethod|invoke-webrequest|irm|iwr|python\d?\s+-c|py\s+-c|node\s+-e)\b", re.I)
READ_VERBS = re.compile(
    r"(?<![\w-])(cat|type|more|less|head|tail|grep|egrep|fgrep|rg|findstr|sed|awk|gc|get-content|"
    r"select-string|bat|strings|xxd|od|hexdump|base64|cp|copy|copy-item|mv|move|move-item|scp|rsync|"
    r"curl|wget|source|nano|vi|vim|code|notepad|jq|sort|uniq|diff|fc|comm|tee|dd|zip|tar|"
    r"import-csv|python\d?\s+-c|py\s+-c|node\s+-e|git\s+add|git\s+show|git\s+diff)(?![\w-])", re.I)
ENV_LISTING = re.compile(
    r"(^|[;&|]\s*)(printenv|env|set|export\s+-p|get-childitem\s+env:|gci\s+env:|dir\s+env:|ls\s+env:)\s*($|[;&|])",
    re.I | re.M)
PASSWORD_FIELD = re.compile(r"pass(word|code|phrase)?\b|\bpin\b|\botp\b|one[- ]time|secret", re.I)


# ─── Minimal YAML (PyYAML when installed) ───────────────────────────────────

def load_yaml_text(text):
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        pass
    return MiniYaml(text).parse()


class MiniYaml:
    """Subset of YAML used by QA Trust files: block maps/lists, flow [..]/{..}, scalars."""

    def __init__(self, text):
        self.lines = []
        buf, ind = None, 0
        for raw in text.replace("\r\n", "\n").split("\n"):
            if raw.strip() in ("---", "..."):
                continue
            line = self._strip_comment(raw)
            if not line.strip():
                continue
            if buf is not None:
                buf += " " + line.strip()
                if self._balanced(buf):
                    self.lines.append((ind, buf))
                    buf = None
                continue
            ind = len(line) - len(line.lstrip(" "))
            text_ = line.strip()
            if self._balanced(text_):
                self.lines.append((ind, text_))
            else:
                buf = text_
        if buf is not None:
            self.lines.append((ind, buf))

    @staticmethod
    def _strip_comment(line):
        out, q = [], None
        for i, ch in enumerate(line):
            if q:
                if ch == q:
                    q = None
            elif ch in "\"'":
                q = ch
            elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
                break
            out.append(ch)
        return "".join(out).rstrip()

    @staticmethod
    def _balanced(s):
        depth, q = 0, None
        for ch in s:
            if q:
                if ch == q:
                    q = None
            elif ch in "\"'":
                q = ch
            elif ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
        return depth <= 0

    def parse(self):
        if not self.lines:
            return None
        node, _ = self._block(0, self.lines[0][0])
        return node

    @staticmethod
    def _is_item(t):
        return t == "-" or t.startswith("- ")

    def _block(self, i, ind):
        if self._is_item(self.lines[i][1]):
            return self._list(i, ind)
        return self._map(i, ind)

    def _list(self, i, ind):
        out = []
        while i < len(self.lines) and self.lines[i][0] == ind and self._is_item(self.lines[i][1]):
            t = self.lines[i][1]
            content = t[1:].strip()
            if not content:
                i += 1
                if i < len(self.lines) and self.lines[i][0] > ind:
                    v, i = self._block(i, self.lines[i][0])
                else:
                    v = None
                out.append(v)
            elif content[0] in "[{\"'" or self._split_key(content) is None:
                out.append(self._value(content))
                i += 1
            else:
                col = ind + (len(t) - len(t[1:].lstrip()))
                self.lines[i] = (col, content)
                v, i = self._map(i, col)
                out.append(v)
        return out, i

    @staticmethod
    def _split_key(t):
        q, depth = None, 0
        for j, ch in enumerate(t):
            if q:
                if ch == q:
                    q = None
            elif ch in "\"'":
                q = ch
            elif ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif ch == ":" and depth == 0 and (j + 1 == len(t) or t[j + 1] in " \t"):
                return t[:j].strip(), t[j + 1:].strip()
        return None

    def _map(self, i, ind):
        out = {}
        while i < len(self.lines) and self.lines[i][0] == ind and not self._is_item(self.lines[i][1]):
            kv = self._split_key(self.lines[i][1])
            if kv is None:
                i += 1
                continue
            k, rest = kv
            k = self._scalar(k)
            i += 1
            if rest in ("|", ">", "|-", ">-", "|+", ">+"):
                parts = []
                while i < len(self.lines) and self.lines[i][0] > ind:
                    parts.append(self.lines[i][1])
                    i += 1
                out[k] = ("\n" if rest[0] == "|" else " ").join(parts)
            elif rest:
                out[k] = self._value(rest)
            elif i < len(self.lines) and (self.lines[i][0] > ind or
                                          (self.lines[i][0] == ind and self._is_item(self.lines[i][1]))):
                out[k], i = self._block(i, self.lines[i][0])
            else:
                out[k] = None
        return out, i

    def _value(self, s):
        s = s.strip()
        if s[:1] in "[{":
            try:
                v, _ = self._flow(s, 0)
                return v
            except (IndexError, ValueError):
                return s
        return self._scalar(s)

    @staticmethod
    def _scalar(s):
        s = s.strip()
        if not s:
            return None
        if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
            return s[1:-1]
        low = s.lower()
        if low in ("null", "~"):
            return None
        if low == "true":
            return True
        if low == "false":
            return False
        for cast in (int, float):
            try:
                return cast(s)
            except ValueError:
                pass
        return s

    def _flow(self, s, p):
        while s[p] in " \t":
            p += 1
        c = s[p]
        if c in "[{":
            close = "]" if c == "[" else "}"
            p += 1
            items = [] if c == "[" else {}
            while True:
                while s[p] in " \t,":
                    p += 1
                if s[p] == close:
                    return items, p + 1
                if c == "[":
                    v, p = self._flow(s, p)
                    items.append(v)
                else:
                    k, p = self._atom(s, p, key=True)
                    while s[p] in " \t":
                        p += 1
                    if s[p] == ":":
                        p += 1
                        v, p = self._flow(s, p)
                    else:
                        v = None
                    items[k] = v
        return self._atom(s, p)

    def _atom(self, s, p, key=False):
        while s[p] in " \t":
            p += 1
        if s[p] in "\"'":
            q = s[p]
            e = s.index(q, p + 1)
            return s[p + 1:e], e + 1
        e = p
        while e < len(s) and s[e] not in ",]}" and not (key and s[e] == ":" and
                                                      (e + 1 == len(s) or s[e + 1] in " \t")):
            e += 1
        return self._scalar(s[p:e]), e


def load_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return load_yaml_text(f.read()) or {}
    except (OSError, ValueError):
        return {}


def front_matter(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text.replace("\r\n", "\n"), re.S)
    return (load_yaml_text(m.group(1)) or {}) if m else {}


def dig(d, keys, default=None):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return default if d is None else d


# ─── Project context ────────────────────────────────────────────────────────

def _norm(p):
    p = str(p or "").replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


def _fold(p):
    return p.lower() if os.name == "nt" else p


def under(r, prefix):
    if r is None or not prefix:
        return False
    r, prefix = _fold(r), _fold(prefix)
    return r == prefix or r.startswith(prefix + "/")


class Ctx:
    def __init__(self, cwd=None):
        self.root = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd())
        cfg_path = os.path.join(self.root, "qa-trust.config.yaml")
        self.active = os.path.isfile(cfg_path)
        self.cfg = load_yaml(cfg_path) if self.active else {}
        if not isinstance(self.cfg, dict):
            self.cfg = {}
        self.qa_root = _norm(dig(self.cfg, ("storage", "repo", "path"), "docs/qa"))
        self.project_dir = self.qa_root + "/_project"
        self.domain_dir = _norm(dig(self.cfg, ("domain", "path"), self.project_dir + "/domain"))
        self.env_file = _norm(dig(self.cfg, ("secrets", "envFile"), ".env"))
        ssp = _norm(dig(self.cfg, ("exploratory", "auth", "storageStatePath"), ".auth/x.json"))
        self.auth_dir = ssp.split("/")[0] if "/" in ssp else ".auth"
        self.guards = dig(self.cfg, ("guards",), {}) or {}
        if not isinstance(self.guards, dict):
            self.guards = {}

    def mode(self, name):
        if self.guards.get("enabled") is False:
            return "off"
        g = self.guards.get(name)
        if isinstance(g, dict) and g.get("mode"):
            return str(g["mode"])
        if isinstance(g, str):
            return g
        return DEFAULT_MODES[name]

    def opt(self, name, key, default=None):
        g = self.guards.get(name)
        return g.get(key, default) if isinstance(g, dict) and g.get(key) is not None else default

    def rel(self, path):
        if not path:
            return None
        p = path if os.path.isabs(path) else os.path.join(self.root, path)
        try:
            r = os.path.relpath(os.path.abspath(p), self.root)
        except ValueError:
            return None
        r = r.replace("\\", "/")
        return None if r == ".." or r.startswith("../") else r

    def abspath(self, r):
        return os.path.join(self.root, *r.split("/"))

    def is_secret_file(self, r):
        if r is None:
            return False
        base = r.split("/")[-1]
        if _fold(r) == _fold(self.env_file):
            return True
        if base == ".env" or (base.startswith(".env.") and
                              base.split(".", 2)[-1] not in ("example", "sample", "template", "dist")):
            return True
        return any(seg == self.auth_dir for seg in r.split("/")[:-1])

    def secret_values(self):
        """name -> value for secret-looking variables (env file + process env). Never printed."""
        names, values = set(KNOWN_SECRET_VARS), {}
        try:
            with open(self.abspath(self.env_file), encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
                    if m:
                        v = m.group(2)
                        if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                            v = v[1:-1]
                        names.add(m.group(1))
                        values[m.group(1)] = v
        except OSError:
            pass
        envs = load_yaml(self.abspath(self.domain_dir + "/environments.yaml"))
        for ref in re.findall(r"env:([A-Za-z_][A-Za-z0-9_]*)", json.dumps(envs)):
            names.add(ref)
        for n in names:
            if os.environ.get(n):
                values[n] = os.environ[n]
        return {n: v for n, v in values.items() if SECRET_NAME.search(n) and len(v) >= 8}


# ─── Guards ─────────────────────────────────────────────────────────────────

def _mask(v):
    return (v[:2] + "***") if len(v) > 4 else "***"


def _decision(mode, strong):
    """Map a guard mode to deny / ask / warn."""
    if mode in ("block", "enforce"):
        return strong
    if mode == "ask":
        return "ask"
    return "warn"


def written_text(tool, ti):
    if tool == "Write":
        return ti.get("content") or ""
    if tool == "Edit":
        return ti.get("new_string") or ""
    if tool == "MultiEdit":
        return "\n".join((e or {}).get("new_string", "") for e in ti.get("edits") or [])
    if tool == "NotebookEdit":
        return ti.get("new_source") or ""
    return ""


def guard_secret_file_write(ctx, tool, r):
    mode = ctx.mode("secretFiles")
    if mode == "off" or not ctx.is_secret_file(r):
        return []
    if tool == "Write" and not os.path.exists(ctx.abspath(r)) and not under(r, ctx.auth_dir):
        return []  # creating the env file from the template (empty values) is allowed
    return [(_decision(mode, "deny"),
             f"{r} holds secrets or recorded logins. Only the user edits it; the AI never reads or "
             f"writes its values (docs/03-credentials-and-test-accounts.md).")]


def guard_secret_scan(ctx, r, text):
    mode = ctx.mode("secretScan")
    if mode == "off" or not text or ctx.is_secret_file(r):
        return []
    text = text[:2_000_000]
    allow = [a for a in (ctx.opt("secretScan", "allow", []) or []) if isinstance(a, str)]

    def allowed(s):
        return any(a in s or re.search(a, s) for a in allow if a)

    found = []
    for name, rx in HIGH_CONFIDENCE:
        m = rx.search(text)
        if m and not allowed(m.group(0)):
            found.append(name)
    if ctx.opt("secretScan", "envValues", True) is not False:
        for n, v in ctx.secret_values().items():
            if v in text and not allowed(v):
                found.append(f"the value of {n}")
    qa_scope = (under(r, ctx.qa_root) or under(r, ctx.domain_dir) or
                _fold(r) in (_fold("qa-trust.config.yaml"), ".mcp.json") or
                (under(r, ".claude") and r.endswith(".json")))
    if qa_scope:
        if LEGACY_ADO_PAT.search(text) and not allowed(LEGACY_ADO_PAT.search(text).group(0)):
            found.append("an Azure DevOps PAT (52-character)")
        for m in ASSIGNMENT.finditer(text):
            val = m.group(2)
            if len(val) < 4 or REFERENCE_VALUE.match(val) or allowed(m.group(0)):
                continue
            found.append(f"a literal {m.group(1)} value ({_mask(val)})")
    if not found:
        return []
    uniq = list(dict.fromkeys(found))
    return [(_decision(mode, "deny"),
             f"Possible secret in {r}: {', '.join(uniq[:5])}. Secrets live only in "
             f"{ctx.env_file} (or the shell); artifacts hold references such as `env:TEST_EMPLOYEE_PASS`. "
             f"Rewrite with a reference. A false positive can be allowed via guards.secretScan.allow "
             f"in qa-trust.config.yaml.")]


def guard_domain_write(ctx, r):
    mode = ctx.mode("domainWrites")
    if mode == "off" or not under(r, ctx.domain_dir) or under(r, ctx.domain_dir + "/_proposals"):
        return []
    g0 = front_matter(ctx.abspath(ctx.project_dir + "/gates/G0.md"))
    if not g0 or str(g0.get("decision", "")).lower() not in ("approved", "approved-with-risks", "overridden"):
        return []  # baseline not set yet: domain discovery writes freely
    win = _read_json(ctx.abspath(ctx.domain_dir + "/_proposals/.apply-window.json"))
    if win and _future(win.get("until")):
        return []
    return [(_decision(mode, "deny"),
             f"{r} is part of the baselined domain context (G0 decided). After G0, domain facts change "
             f"only through Domain Change Proposals: raise a DCP (/qa-domain), or accept one with "
             f"/qa-domain accept (which opens an apply window). Approve only an intentional direct edit "
             f"and record it in {ctx.project_dir}/audit.md as DOMAIN-DIRECT-EDIT.")]


def guard_secret_read(ctx, tool, ti):
    mode = ctx.mode("secretFiles")
    if mode == "off":
        return []
    r = ctx.rel(ti.get("file_path") or ti.get("path") or "")
    if r and ctx.is_secret_file(r):
        return [(_decision(mode, "deny"),
                 f"{r} holds secrets or recorded logins; the AI never opens it. To check setup, test "
                 f"whether keys are set (e.g. the helper's --check) or use `git check-ignore {r}`.")]
    return []


def _env_ref_regex(ctx):
    names = {ctx.env_file.split("/")[-1], ".env"}
    alts = "|".join(re.escape(n) for n in names) + "|" + re.escape(ctx.auth_dir) + r"[/\\]"
    return re.compile(r"(?:^|[\s'\"=/\\(<])(?:" + alts + r")(?=$|[\s'\")>;|&]|(?<=[/\\]))")


def guard_shell(ctx, cmd):
    mode = ctx.mode("secretFiles")
    if mode == "off" or not cmd:
        return []
    out = []
    if _env_ref_regex(ctx).search(cmd) and (READ_VERBS.search(cmd) or re.search(r"(^|[;&|]\s*)\.\s", cmd) or
                                            re.search(r"<\s*\S*\.env\b", cmd)):
        out.append("reads or copies the secrets file / recorded logins (use `git check-ignore` to "
                   "verify it is ignored; the helper scripts load it themselves)")
    if ENV_LISTING.search(cmd):
        out.append("lists all environment variables (they include secrets)")
    var = r"(?:\$\{?|\$env:|%|getenv\(\s*['\"]|environ\[\s*['\"]|environ\.get\(\s*['\"]|process\.env\.|GetEnvironmentVariable\(\s*['\"])"
    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        for m in re.finditer(var + r"([A-Za-z_][A-Za-z0-9_]*)", seg, re.I):
            if SECRET_NAME.search(m.group(1)) and (OUTPUT_START.search(seg) or re.search(r">{1,2}", seg)):
                out.append(f"prints or writes the secret variable {m.group(1)}")
                break
    if not out:
        return []
    return [(_decision(mode, "deny"), "This command " + "; ".join(dict.fromkeys(out)) + ".")]


def _origin(url):
    m = re.match(r"^\s*([a-z][a-z0-9+.-]*)://([^/?#]+)", str(url or ""), re.I)
    if not m:
        return None
    host = m.group(2).split("@")[-1].lower()
    return f"{m.group(1).lower()}://{host}"


def guard_browser(ctx, tool, ti):
    mode = ctx.mode("browser")
    if mode == "off":
        return []
    out = []
    envs = dig(load_yaml(ctx.abspath(ctx.domain_dir + "/environments.yaml")), ("environments",), []) or []
    allowed_names = [str(n).lower() for n in (dig(ctx.cfg, ("exploratory", "environments", "allowed"),
                                                  ["dev", "test", "staging"]) or [])]
    allowed, blocked = set(), {}
    for e in envs if isinstance(envs, list) else []:
        if not isinstance(e, dict) or "{{" in str(e.get("url", "")):
            continue
        o, name = _origin(e.get("url")), str(e.get("name", "")).lower()
        if not o:
            continue
        if re.search(r"prod|production|live", name) or e.get("agentsAllowed") is not True:
            blocked[o] = name
        elif name in allowed_names:
            allowed.add(o)
    for extra in dig(ctx.cfg, ("exploratory", "allowedOrigins"), []) or []:
        o = _origin(extra)
        if o:
            allowed.add(o)
    for key in ("url",):
        url = ti.get(key)
        if not url or re.match(r"^\s*(about:|data:)", str(url), re.I):
            continue
        o = _origin(url)
        if o in blocked and o not in allowed:
            out.append((_decision(mode, "deny"),
                        f"{o} is the '{blocked[o]}' environment, which agents may not use "
                        f"(environments.yaml agentsAllowed / production is always refused)."))
        elif o not in allowed:
            out.append((_decision(mode, "ask"),
                        f"{o or url} is not an allowed test origin (exploratory.environments.allowed + "
                        f"environments.yaml, exploratory.allowedOrigins). Allow only if it is a test system."))
    labels = [ti.get("element"), ti.get("startElement"), ti.get("endElement")]
    labels += [(f or {}).get("name") for f in ti.get("fields") or [] if isinstance(f, dict)]
    labels = [str(x) for x in labels if x]
    if re.search(r"(type|fill_form|fill)$", tool) and any(PASSWORD_FIELD.search(x) for x in labels):
        out.append((_decision(mode, "deny"),
                    "The AI never types credentials. The tester logs in in the browser window "
                    "(or a recorded storage-state login is used)."))
    if re.search(r"(click|type|select_option|fill_form|drag|press_key)$", tool):
        phrases = dig(ctx.cfg, ("exploratory", "guards", "blockActions"), []) or []
        for label in labels:
            for ph in phrases:
                rx = r"(?<![A-Za-z])" + re.escape(str(ph)).replace(r"\ ", r"\s+") + r"(?![A-Za-z])"
                if re.search(rx, label, re.I):
                    out.append((_decision(mode, "ask"),
                                f"'{label}' matches the blocked action '{ph}' (exploratory.guards.blockActions). "
                                f"Destructive or outward-facing actions need the tester's go-ahead."))
                    break
    if tool.endswith("file_upload"):
        for p in ti.get("paths") or []:
            if ctx.is_secret_file(ctx.rel(p)):
                out.append(("deny", f"Uploading {p} would expose secrets."))
    return out


def handle_pre(ctx, data):
    tool, ti = data.get("tool_name") or "", data.get("tool_input") or {}
    res = []
    if tool in WRITE_TOOLS:
        r = ctx.rel(ti.get("file_path") or ti.get("notebook_path") or "")
        if r is None:
            return None
        res += guard_secret_file_write(ctx, tool, r)
        res += guard_secret_scan(ctx, r, written_text(tool, ti))
        res += guard_domain_write(ctx, r)
    elif tool in READ_TOOLS:
        res += guard_secret_read(ctx, tool, ti)
    elif tool in SHELL_TOOLS:
        res += guard_shell(ctx, ti.get("command") or "")
    elif BROWSER_TOOL.match(tool):
        res += guard_browser(ctx, tool, ti)
    return combine(res)


def combine(res):
    if not res:
        return None
    for level in ("deny", "ask"):
        reasons = [m for lv, m in res if lv == level]
        if reasons:
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": level,
                                           "permissionDecisionReason": "qa-guard: " + " | ".join(reasons)}}
    return {"systemMessage": "qa-guard (warning): " + " | ".join(m for _, m in res)}


# ─── Gate staleness ─────────────────────────────────────────────────────────

def canonical_hash(path):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    if path.lower().endswith((".yaml", ".yml")):
        lines, out, skip_ind = text.split("\n"), [], None
        keys = "|".join(BOOKKEEPING_KEYS)
        for ln in lines:
            ind = len(ln) - len(ln.lstrip(" "))
            if skip_ind is not None:
                if ln.strip() and ind <= skip_ind:
                    skip_ind = None
                else:
                    continue
            m = re.match(r"^(\s*)(" + keys + r")\s*:\s*(#.*)?$", ln)
            if m:
                skip_ind = len(m.group(1))
                continue
            if re.match(r"^\s*(" + keys + r")\s*:", ln):
                continue
            out.append(ln.rstrip())
        text = "\n".join(out)
    else:
        text = "\n".join(ln.rstrip() for ln in text.split("\n"))
    return "sha256:" + hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def find_item_dir(ctx, r):
    parts = r.split("/")[:-1]
    while len(parts) > len(ctx.qa_root.split("/")):
        cand = "/".join(parts)
        if os.path.isfile(ctx.abspath(cand + "/qa-state.md")):
            return cand
        parts.pop()
    return None


def cover_map(ctx):
    cm = dict(DEFAULT_COVER)
    extra = ctx.opt("gateStale", "cover", {}) or {}
    if isinstance(extra, dict):
        for g, paths in extra.items():
            if isinstance(paths, list):
                cm[str(g)] = [str(p) for p in paths]
    return cm


def covers(pattern, ip):
    pattern = _norm(pattern) + ("/" if str(pattern).endswith("/") else "")
    return (_fold(ip).startswith(_fold(pattern)) if pattern.endswith("/") else _fold(ip) == _fold(pattern))


def handle_post(ctx, data):
    tool, ti = data.get("tool_name") or "", data.get("tool_input") or {}
    if tool not in WRITE_TOOLS:
        return None
    mode = ctx.mode("gateStale")
    r = ctx.rel(ti.get("file_path") or ti.get("notebook_path") or "")
    if mode == "off" or r is None or not under(r, ctx.qa_root) or under(r, ctx.project_dir):
        return None
    item = find_item_dir(ctx, r)
    if not item:
        return None
    ip = r[len(item) + 1:]
    base = ip.split("/")[-1]
    if ip in ("qa-state.md", "audit.md", "questions.md") or ip.startswith("gates/") or base.startswith("."):
        return None
    state_path = ctx.abspath(item + "/qa-state.md")
    with open(state_path, encoding="utf-8") as f:
        state = f.read()
    row_rx = re.compile(r"^(\|\s*)(G[0-5])(\s*\|\s*)([a-z-]+)(\s*\|)", re.M)
    hits = []
    cm = cover_map(ctx)
    for m in row_rx.finditer(state):
        gate, status = m.group(2), m.group(4)
        if status not in STALE_FROM:
            continue
        rec = front_matter(ctx.abspath(f"{item}/gates/{gate}.md")) or {}
        covered, unchanged = False, False
        for a in rec.get("artifacts") or []:
            if not isinstance(a, dict) or not a.get("path"):
                continue
            if covers(a["path"], ip):
                covered = True
                if not str(a["path"]).endswith("/") and a.get("hash"):
                    want = str(a["hash"])
                    want = want if want.startswith("sha256:") else "sha256:" + want
                    try:
                        unchanged = canonical_hash(ctx.abspath(r)) == want
                    except OSError:
                        unchanged = False
        if not covered:
            covered = any(covers(p, ip) for p in cm.get(gate, []))
        if covered and not unchanged:
            hits.append((gate, status))
    if not hits:
        return None
    names = ", ".join(f"{g} (was {s})" for g, s in hits)
    if mode == "mark":
        stale = {g for g, _ in hits}
        state = row_rx.sub(lambda m: m.group(1) + m.group(2) + m.group(3) +
                           ("stale" if m.group(2) in stale else m.group(4)) + m.group(5), state)
        with open(state_path, "w", encoding="utf-8", newline="") as f:
            f.write(state)
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        audit = ctx.abspath(item + "/audit.md")
        try:
            with open(audit, "a+", encoding="utf-8") as f:
                f.seek(0)
                body = f.read()
                sep = "" if body.endswith("\n") or not body else "\n"
                for g, s in hits:
                    f.write(f"{sep}| {ts} | GATE | qa-guard | {g} stale (was {s}) — {ip} changed after the decision |\n")
                    sep = ""
        except OSError:
            pass
        what = f"Marked {names} as stale in {item}/qa-state.md"
    else:
        what = f"{names} may now be stale"
    msg = (f"qa-guard: {ip} is covered by {names}. {what}. Tell the user. If the change is not "
           f"material (typo, formatting), the approver can re-affirm with /qa-gate <Gx> --reaffirm; "
           f"otherwise re-run the gate before relying on it (core/gate-protocol.md §4).")
    return {"systemMessage": msg,
            "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}


# ─── Helpers ────────────────────────────────────────────────────────────────

def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _future(iso):
    try:
        t = datetime.datetime.strptime(str(iso), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return False
    return t > datetime.datetime.now(datetime.timezone.utc)


def cmd_hash(ctx, args):
    if len(args) < 2:
        print("usage: qa_guard.py hash <ITEM_DIR> <GATE> [extra paths relative to ITEM_DIR...]", file=sys.stderr)
        return 2
    item, gate = _norm(args[0]), args[1].upper()
    item_abs = ctx.abspath(ctx.rel(item) or item)
    pats = cover_map(ctx).get(gate, []) + list(args[2:])
    files = []
    for p in pats:
        full = os.path.join(item_abs, *_norm(p).split("/"))
        if os.path.isdir(full):
            for dp, _, fns in os.walk(full):
                for fn in fns:
                    if not fn.startswith("."):
                        files.append(os.path.relpath(os.path.join(dp, fn), item_abs).replace("\\", "/"))
        elif os.path.isfile(full):
            files.append(_norm(p))
    print("artifacts:")
    for rp in sorted(dict.fromkeys(files)):
        h = canonical_hash(os.path.join(item_abs, *rp.split("/")))
        print(f'  - {{ path: "{rp}", hash: "{h}" }}')
    return 0


def cmd_dcp_window(ctx, args):
    path = ctx.abspath(ctx.domain_dir + "/_proposals/.apply-window.json")
    if args and args[0] == "close":
        try:
            os.remove(path)
        except OSError:
            pass
        print("closed")
        return 0
    if len(args) < 2 or args[0] != "open":
        print("usage: qa_guard.py dcp-window open <DCP-0001,DCP-0002> [--minutes 30] | close", file=sys.stderr)
        return 2
    minutes = 30
    if "--minutes" in args:
        minutes = max(1, min(240, int(args[args.index("--minutes") + 1])))
    until = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"dcps": [d for d in args[1].split(",") if d],
                   "until": until.strftime("%Y-%m-%dT%H:%M:%SZ")}, f)
    print(f"open until {until.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return 0


def cmd_status(ctx):
    if not ctx.active:
        print("inactive: no qa-trust.config.yaml in " + ctx.root)
        return 0
    for name in DEFAULT_MODES:
        print(f"{name}: {ctx.mode(name)}")
    print(f"qaRoot: {ctx.qa_root}  domain: {ctx.domain_dir}  envFile: {ctx.env_file}  authDir: {ctx.auth_dir}")
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode in ("pre", "post"):
        try:
            data = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        except ValueError:
            return 0
        try:
            ctx = Ctx(data.get("cwd"))
            if not ctx.active:
                return 0
            out = handle_pre(ctx, data) if mode == "pre" else handle_post(ctx, data)
        except Exception as e:  # fail open, but say so
            sys.stderr.write(f"qa-guard: internal error, guard skipped: {type(e).__name__}: {e}\n")
            return 0
        if out:
            sys.stdout.write(json.dumps(out, ensure_ascii=True))
        return 0
    ctx = Ctx()
    if mode == "hash":
        return cmd_hash(ctx, argv[2:])
    if mode == "dcp-window":
        return cmd_dcp_window(ctx, argv[2:])
    if mode == "status":
        return cmd_status(ctx)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
