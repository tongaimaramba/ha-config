#!/usr/bin/env python3
"""redact.py — scrub secrets from an export staging directory, in place.

Usage:  python3 redact.py <export-dir>      (the <host>/ dir export.sh builds)

Standard library only, so it runs inside the HA SSH add-on with a bare python3.

Passes, in order:
  1. secrets-style YAML (secrets.yaml, *secrets*.yaml): every value -> <redacted>,
     keys kept so it stays obvious what each secret is wired to.
  2. .storage/core.config_entries: each entry keeps identity fields
     (entry_id, domain, title, state, source, version, unique_id, disabled_by,
     pref_*, created_at, modified_at, subentries' identity); `data` and
     `options` are replaced by {"_redacted_keys": [...]}.
  3. Generic key/value pass over every text file: values of keys that look
     like credentials are replaced, in YAML (`key: value`), JSON
     (`"key": "value"`) and JS (`key: 'value'`) forms. `!secret name`
     references are left alone (they are the point of secrets.yaml).
  4. Python assignment pass: `identifier = "value"` / `self.identifier = "value"`
     for names that look like credentials (the generic pass above only catches
     `key: value` / `"key": value` shapes, which Python code doesn't use).
  5. Shape-based pass, name- and extension-independent: known credential formats
     (Stripe/Octopus-style sk_live_/sk_test_, GitHub tokens, Slack tokens, AWS
     access key IDs, Google API keys, Twilio SIDs, PEM private key blocks) are
     redacted wherever they appear, because a real Octopus Energy API key was
     found sitting in a variable named `un` in a hand-written AppDaemon app —
     no key-name pattern would ever have caught that; only the key's own shape
     did (GitHub's push protection is what actually caught it, after the fact).
  6. Token-shape pass: JWTs (eyJ...), and long bearer-ish strings after
     "Bearer ".

Prints a per-file report of replacements to stdout. Passes 4-6 (Python
assignments, credential shapes, JWT/Bearer) run on every text file regardless
of its extension or the sensitivity of any key name nearby — this is
belt-and-braces for exactly the "safe-looking variable name" failure mode
above.
"""
import json
import os
import re
import sys
from collections import Counter

SENSITIVE_KEYS = (
    "password|passwd|pwd|pw|token|access_token|refresh_token|id_token|secret|client_secret|"
    "api_key|apikey|api_token|auth_key|access_key|secret_key|private_key|encryption_key|"
    "credential|credentials|credentialsecret|credentialSecret|webhook_id|cloudhook_url|"
    "devicekey|device_key|psk|ota_password|bearer|cookie|app_secret|broker_un|broker_pw|"
    "totp|otp|pin_code|passcode|license_key|serial_secret"
)
# Note: "pw" is intentionally broad (matches as a substring, e.g. mqtt_broker_pw — that's
# a real credential this codebase used) — a rare false hit on an unrelated "...pw..."
# identifier just means over-redaction, which is the safe direction to err in here.
# YAML:   key: value        (value not starting with !secret, not a nested block)
RE_YAML = re.compile(
    rf"^(\s*-?\s*['\"]?[A-Za-z0-9_.\-]*?(?:{SENSITIVE_KEYS})['\"]?[ \t]*:)(?![ \t]*!secret\b)(?![ \t]*$)(?![ \t]*[|>])[ \t]*(.+?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
# JSON:   "key": "value"   or "key": 12345
RE_JSON = re.compile(
    rf'("[A-Za-z0-9_.\-]*?(?:{SENSITIVE_KEYS})"\s*:\s*)("(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?)',
    re.IGNORECASE,
)
# JS:     key: 'value'  /  key: "value"
RE_JS = re.compile(
    rf"(\b(?:{SENSITIVE_KEYS})\s*:\s*)('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")",
    re.IGNORECASE,
)
RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
RE_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9._~+/=-]{20,}")

# Python assignment: identifier = "value"  /  self.identifier = "value"  (the generic
# YAML/JSON/JS passes above miss this — bit us once already: an Octopus Energy API
# key was sitting in a variable named `un`/`self.un`, so this ALSO doesn't help catch
# that one; kept for the next credential that at least has a sensible name).
RE_PY_ASSIGN = re.compile(
    rf"^(\s*(?:self\.)?[A-Za-z_][A-Za-z0-9_]*(?:{SENSITIVE_KEYS})[A-Za-z0-9_]*\s*=\s*)(['\"]).*?\2\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# The specific `un`/`pw` idiom used throughout this codebase (found the hard way: an
# Octopus Energy key lived in `self.un`, a Monit dashboard password in `self.pw` — the
# word-boundary version below is deliberately loose, matching the bare identifiers "un"
# and "pw" with or without a `self.` prefix, unlike RE_PY_ASSIGN's substring match).
RE_PY_UN_PW = re.compile(
    r"^(\s*(?:self\.)?(?:un|pw)\s*=\s*)(['\"]).*?\2\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# auth = ('user', 'pass')  /  .auth = ("user","pass")  — HTTPBasicAuth-style literal
# tuples. Redacts both elements whenever they're string literals (not variables).
RE_AUTH_TUPLE = re.compile(
    r"(\bauth\s*=\s*\(\s*)(['\"])(?:[^'\"\\]|\\.)*\2(\s*,\s*)(['\"])(?:[^'\"\\]|\\.)*\4(\s*\))",
    re.IGNORECASE,
)

# Shape-based, name-independent: catches a credential regardless of what variable it's
# assigned to (this is what actually would have caught the Octopus Energy key stored in
# a variable called `un` — GitHub's push protection flagged it as a Stripe-shaped key
# since Octopus Energy deliberately mints keys in Stripe's sk_live_/sk_test_ format).
# Extend this list whenever a new provider's key shape turns up in an export.
SECRET_SHAPES = [
    ("stripe/octopus-style secret key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("stripe-style publishable key", re.compile(r"\bpk_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github fine-grained pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("aws access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("twilio api key sid", re.compile(r"\bSK[0-9a-fA-F]{32}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

# Blocklist, not allowlist: export.sh's own copytree filters already keep most binaries
# out, but this repo has real text files sitting under odd/renamed extensions
# (.yaml_txt, .old, .v233, .lot, _txt_pause from paused/backed-up AppDaemon apps) that a
# TEXT_EXT allowlist would silently skip — and skip means unredacted. Try to decode
# everything as UTF-8 text except known-binary types; a real binary just fails to decode
# and is skipped in main() regardless.
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pyc", ".pyo", ".so", ".db", ".db-shm", ".db-wal", ".sqlite", ".sqlite3",
    ".pem", ".der", ".p12", ".pfx", ".key", ".crt",
    ".zip", ".gz", ".tar", ".7z", ".bz2", ".xz",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".mp3", ".wav", ".mp4", ".mov", ".pickle", ".pkl",
}
SECRETS_FILE = re.compile(r"secrets.*\.ya?ml$", re.IGNORECASE)

report = Counter()


def redact_secrets_yaml(text):
    out, n = [], 0
    for line in text.splitlines():
        m = re.match(r"^(\s*[A-Za-z0-9_.\-]+\s*:\s*)(.*\S)\s*$", line)
        if m and not line.lstrip().startswith("#"):
            out.append(m.group(1) + "<redacted>")
            n += 1
        else:
            out.append(line)
    return "\n".join(out) + "\n", n


def redact_config_entries(path):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    entries = doc.get("data", {}).get("entries", [])
    keep = {
        "entry_id", "domain", "title", "state", "source", "version", "minor_version",
        "unique_id", "disabled_by", "pref_disable_new_entities", "pref_disable_polling",
        "created_at", "modified_at", "discovery_keys", "subentries", "data", "options",
    }
    n = 0
    for e in entries:
        for field in ("data", "options"):
            if field in e:
                val = e[field]
                e[field] = {"_redacted_keys": sorted(val.keys()) if isinstance(val, dict) else ["<non-dict>"]}
                n += 1
        for sub in e.get("subentries", []) or []:
            if "data" in sub:
                sub["data"] = {"_redacted_keys": sorted(sub["data"].keys()) if isinstance(sub["data"], dict) else ["<non-dict>"]}
                n += 1
        for k in list(e.keys()):
            if k not in keep:
                del e[k]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return n


RE_ESPHOME_KEY = re.compile(r"^(\s*key\s*:\s*)(?!!secret\b)(\S.*)$", re.MULTILINE)


def redact_generic(text, ext, esphome=False):
    # Deliberately NOT gated tightly on `ext` any more: this repo has real files with
    # renamed/odd extensions (.yaml_txt, .old, .v233, .lot, _txt_pause — paused or
    # backed-up AppDaemon apps) that used to fall outside the extension allow-list and
    # get ZERO redaction. Every syntax-shaped pass below is cheap and low-false-positive
    # enough to just always attempt; only the ESPHome `key:` pass stays conditional,
    # since it's deliberately aggressive (redacts ANY `key: ...` line) and would be too
    # broad outside ESPHome device YAML specifically.
    n = 0
    if esphome:
        text, k = RE_ESPHOME_KEY.subn(r"\1<redacted>", text); n += k
    text, k = RE_YAML.subn(r"\1 <redacted>", text); n += k
    text, k = RE_JSON.subn(r'\1"<redacted>"', text); n += k
    text, k = RE_JS.subn(r'\1"<redacted>"', text); n += k
    text, k = RE_PY_ASSIGN.subn(r"\1\2<redacted>\2", text); n += k
    text, k = RE_PY_UN_PW.subn(r"\1\2<redacted>\2", text); n += k
    text, k = RE_AUTH_TUPLE.subn(r"\1\2<redacted>\2\3\4<redacted>\4\5", text); n += k
    text, k = RE_JWT.subn("<redacted-jwt>", text); n += k
    text, k = RE_BEARER.subn(r"\1<redacted>", text); n += k
    # shape-based, applied regardless of extension or variable/key name
    for _label, rx in SECRET_SHAPES:
        text, k = rx.subn("<redacted>", text); n += k
    return text, n


def main(root):
    for dirpath, _, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            ext = os.path.splitext(name)[1].lower()
            if rel.startswith("meta/"):
                continue
            if rel == os.path.join("storage", "core.config_entries"):
                try:
                    report[rel] += redact_config_entries(path)
                except Exception as exc:  # never leave a half-redacted file behind
                    os.remove(path)
                    report[rel + "  !! REMOVED (parse error: %s)" % exc] += 0
                continue
            if ext in BINARY_EXT:
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            if SECRETS_FILE.search(name):
                text, n = redact_secrets_yaml(text)
                report[rel] += n
            text, n = redact_generic(text, ext, esphome=rel.startswith(os.path.join("config", "esphome")))
            report[rel] += n
            if report[rel]:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)

    print("redaction report (replacements per file):")
    total = 0
    for rel, n in sorted(report.items()):
        if n or "REMOVED" in rel:
            print(f"  {n:5d}  {rel}")
            total += n
    print(f"  total: {total}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit("usage: redact.py <export-dir>")
    main(sys.argv[1])
