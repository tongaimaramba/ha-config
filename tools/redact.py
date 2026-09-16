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
  4. Token-shape pass: JWTs (eyJ...), and long bearer-ish strings after
     "Bearer ".

Prints a per-file report of replacements to stdout.
"""
import json
import os
import re
import sys
from collections import Counter

SENSITIVE_KEYS = (
    "password|passwd|pwd|token|access_token|refresh_token|id_token|secret|client_secret|"
    "api_key|apikey|api_token|auth_key|access_key|secret_key|private_key|encryption_key|"
    "credential|credentials|credentialsecret|credentialSecret|webhook_id|cloudhook_url|"
    "devicekey|device_key|psk|ota_password|bearer|cookie|app_secret|"
    "totp|otp|pin_code|passcode|license_key|serial_secret"
)
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

TEXT_EXT = {".yaml", ".yml", ".json", ".js", ".txt", ".conf", ".cfg", ".ini", ".py", ".md", ".csv", ".tsv", ""}
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
    n = 0
    if esphome:
        text, k = RE_ESPHOME_KEY.subn(r"\1<redacted>", text); n += k
    if ext in (".yaml", ".yml", ".conf", ".cfg", ".ini", ".txt", ""):
        text, k = RE_YAML.subn(r"\1 <redacted>", text); n += k
    if ext in (".json", ".txt", ""):
        text, k = RE_JSON.subn(r'\1"<redacted>"', text); n += k
    if ext in (".js", ".py"):
        text, k = RE_JS.subn(r'\1"<redacted>"', text); n += k
    text, k = RE_JWT.subn("<redacted-jwt>", text); n += k
    text, k = RE_BEARER.subn(r"\1<redacted>", text); n += k
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
            if ext not in TEXT_EXT:
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
