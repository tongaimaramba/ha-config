#!/usr/bin/env python3
"""digest.py — build compact, knowledge-base-sized summaries for one host snapshot.

Usage:  python3 digest.py hosts/<host>

Reads the redacted snapshot under hosts/<host>/{config,storage,integrations,addons,meta}
and writes hosts/<host>/digest/*.md|*.tsv.  These digests are what the
project-knowledge GitHub sync should point at: the raw registries are several MB
each, the digests are a few hundred KB per host.

Needs PyYAML (pip install pyyaml) for the automations/scripts/config summaries;
degrades to a regex-only summary if it is missing.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

try:
    import yaml

    class Tolerant(yaml.SafeLoader):
        pass

    def _tag(loader, tag_suffix, node):
        if isinstance(node, yaml.ScalarNode):
            return f"{node.tag} {loader.construct_scalar(node)}"
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_mapping(node)

    Tolerant.add_multi_constructor("!", _tag)
    HAVE_YAML = True
except ImportError:  # pragma: no cover
    HAVE_YAML = False


def jload(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def yload(path):
    if not HAVE_YAML or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.load(fh, Loader=Tolerant)
    except Exception as exc:
        return {"_parse_error": str(exc)}


def tsv(rows, header):
    out = ["\t".join(header)]
    for r in rows:
        out.append("\t".join("" if v is None else str(v).replace("\t", " ").replace("\n", " ") for v in r))
    return "\n".join(out) + "\n"


def md_table(rows, header):
    if not rows:
        return "_none_\n"
    esc = lambda v: "" if v is None else str(v).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(esc(v) for v in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


ENTITY_RE = re.compile(r"\b((?:[a-z_]+)\.[a-z0-9_]+)\b")
DOMAINS = {"sensor", "binary_sensor", "switch", "light", "input_boolean", "input_datetime", "input_number",
           "input_select", "input_text", "input_button", "script", "automation", "lawn_mower", "climate",
           "cover", "lock", "camera", "media_player", "person", "device_tracker", "zone", "number", "select",
           "button", "fan", "vacuum", "alarm_control_panel", "scene", "group", "timer", "counter", "weather",
           "sun", "calendar", "event", "image", "siren", "valve", "water_heater", "humidifier", "remote",
           "notify", "text", "date", "time", "datetime", "update", "tts", "stt", "todo", "conversation"}


def actions_in(obj):
    """All service/action calls anywhere inside a sequence (recurses into if/then/choose/repeat)."""
    found = set()
    if isinstance(obj, dict):
        a = obj.get("action") if isinstance(obj.get("action"), str) else obj.get("service")
        if isinstance(a, str) and "." in a:
            found.add(a)
        for v in obj.values():
            found |= actions_in(v)
    elif isinstance(obj, list):
        for v in obj:
            found |= actions_in(v)
    return found


def entity_refs(obj):
    """All entity_id-looking strings inside any JSON/YAML structure."""
    found = set()
    for m in ENTITY_RE.findall(json.dumps(obj, default=str)):
        if m.split(".")[0] in DOMAINS:
            found.add(m)
    return sorted(found)


def main(host_dir):
    host = os.path.basename(os.path.normpath(host_dir))
    C = os.path.join(host_dir, "config")
    S = os.path.join(host_dir, "storage")
    I = os.path.join(host_dir, "integrations")
    M = os.path.join(host_dir, "meta")
    D = os.path.join(host_dir, "digest")
    os.makedirs(D, exist_ok=True)
    written = []

    def write(name, text):
        with open(os.path.join(D, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(name)

    # ---- registries ----------------------------------------------------------
    areas = {a["id"]: a["name"] for a in (jload(os.path.join(S, "core.area_registry")) or {}).get("data", {}).get("areas", [])}
    devices = {d["id"]: d for d in (jload(os.path.join(S, "core.device_registry")) or {}).get("data", {}).get("devices", [])}
    entities = (jload(os.path.join(S, "core.entity_registry")) or {}).get("data", {}).get("entities", [])
    entries = (jload(os.path.join(S, "core.config_entries")) or {}).get("data", {}).get("entries", [])
    entry_by_id = {e["entry_id"]: e for e in entries}

    # ---- integrations.md -----------------------------------------------------
    custom = {}
    if os.path.isdir(I):
        for n in sorted(os.listdir(I)):
            mf = jload(os.path.join(I, n, "manifest.json"))
            if mf:
                custom[n] = mf
    ent_count_by_entry = Counter(e.get("config_entry_id") for e in entities)
    dev_count_by_entry = Counter()
    for d in devices.values():
        for ce in d.get("config_entries", []) or []:
            dev_count_by_entry[ce] += 1
    rows = []
    for e in sorted(entries, key=lambda x: (x["domain"], str(x.get("title")))):
        rows.append([e["domain"], e.get("title"), e.get("source"),
                     "custom" if e["domain"] in custom else "core",
                     dev_count_by_entry.get(e["entry_id"], 0), ent_count_by_entry.get(e["entry_id"], 0),
                     e.get("disabled_by") or "", e["entry_id"]])
    text = f"# {host} — integrations (config entries)\n\n"
    text += md_table(rows, ["domain", "title", "source", "kind", "devices", "entities", "disabled", "entry_id"])
    text += "\n## custom_components present on disk\n\n"
    crow = []
    has_entry = {e["domain"] for e in entries}
    for n, mf in custom.items():
        crow.append([n, mf.get("version", ""), mf.get("name", ""), "yes" if n in has_entry else "NO — installed but not configured",
                     mf.get("documentation", "") or mf.get("codeowners", "")])
    text += md_table(crow, ["component", "version", "name", "has config entry", "docs"])
    # YAML-configured integrations (top-level keys of configuration.yaml)
    conf = yload(os.path.join(C, "configuration.yaml"))
    if isinstance(conf, dict):
        text += "\n## configuration.yaml top-level keys\n\n"
        text += ", ".join(f"`{k}`" for k in conf.keys()) + "\n"
    write("integrations.md", text)

    # ---- entities.tsv, devices.tsv, areas -------------------------------------
    erows = []
    for e in sorted(entities, key=lambda x: x["entity_id"]):
        dev = devices.get(e.get("device_id") or "", {})
        area = e.get("area_id") or dev.get("area_id")
        ce = entry_by_id.get(e.get("config_entry_id") or "", {})
        erows.append([e["entity_id"], e.get("platform"), ce.get("title", ""), dev.get("name_by_user") or dev.get("name", ""),
                      areas.get(area, ""), e.get("name") or e.get("original_name") or "",
                      e.get("disabled_by") or "", e.get("hidden_by") or "", e.get("unique_id", "")])
    write("entities.tsv", tsv(erows, ["entity_id", "platform", "config_entry", "device", "area", "name", "disabled_by", "hidden_by", "unique_id"]))

    drows = []
    for d in sorted(devices.values(), key=lambda x: (x.get("name_by_user") or x.get("name") or "")):
        doms = sorted({entry_by_id.get(ce, {}).get("domain", "?") for ce in d.get("config_entries", []) or []})
        drows.append([d.get("name_by_user") or d.get("name"), d.get("manufacturer"), d.get("model"), areas.get(d.get("area_id"), ""),
                      ",".join(doms), d.get("disabled_by") or "", d.get("sw_version") or "", d["id"]])
    write("devices.tsv", tsv(drows, ["name", "manufacturer", "model", "area", "integrations", "disabled_by", "sw_version", "device_id"]))
    write("areas.md", f"# {host} — areas\n\n" + "\n".join(f"- {n}" for n in sorted(areas.values())) + "\n")

    # ---- helpers.md ----------------------------------------------------------
    text = f"# {host} — UI-created helpers (.storage/input_*, counter, timer, zone)\n\n"
    for kind in ["input_boolean", "input_datetime", "input_number", "input_select", "input_text", "input_button", "counter", "timer", "zone", "person"]:
        doc = jload(os.path.join(S, kind))
        items = (doc or {}).get("data", {}).get("items", []) if doc else []
        text += f"## {kind} ({len(items)})\n\n"
        rows = [[f"{kind}.{i.get('id')}", i.get("name"), json.dumps({k: v for k, v in i.items() if k not in ('id', 'name')}, default=str)[:160]] for i in items]
        text += md_table(rows, ["entity_id", "name", "settings"]) + "\n"
    write("helpers.md", text)

    # ---- automations.md / scripts.md ------------------------------------------
    def summarize_automations():
        data = yload(os.path.join(C, "automations.yaml"))
        rows = []
        if isinstance(data, list):
            for a in data:
                if not isinstance(a, dict):
                    continue
                trig = a.get("triggers", a.get("trigger", []))
                trig = trig if isinstance(trig, list) else [trig]
                tsum = ", ".join(str(t.get("trigger") or t.get("platform") or "?") + (":" + str(t.get("at") or t.get("entity_id") or t.get("event_type") or "") if t.get("at") or t.get("entity_id") or t.get("event_type") else "") for t in trig if isinstance(t, dict))
                rows.append([a.get("id"), a.get("alias"), a.get("mode", "single"), tsum[:120], ", ".join(entity_refs(a))[:300]])
        return rows, data

    rows, data = summarize_automations()
    text = f"# {host} — automations.yaml ({len(rows)} automations)\n\n" + md_table(rows, ["id", "alias", "mode", "triggers", "entities referenced"])
    if isinstance(data, dict) and "_parse_error" in data:
        text += f"\n_parse error: {data['_parse_error']}_\n"
    write("automations.md", text)

    sdata = yload(os.path.join(C, "scripts.yaml"))
    rows = []
    if isinstance(sdata, dict):
        for sid, s in sdata.items():
            if isinstance(s, dict):
                svc = sorted(actions_in(s.get("sequence", [])))
                rows.append([f"script.{sid}", s.get("alias"), s.get("mode", "single"), ", ".join(svc)[:200], ", ".join(entity_refs(s))[:300]])
    write("scripts.md", f"# {host} — scripts.yaml ({len(rows)} scripts)\n\n" + md_table(rows, ["entity_id", "alias", "mode", "actions", "entities referenced"]))

    # ---- packages / other yaml -------------------------------------------------
    text = f"# {host} — YAML files in config root\n\n"
    rows = []
    for dirpath, _, files in os.walk(C):
        for f in sorted(files):
            if f.endswith((".yaml", ".yml")):
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, C)
                doc = yload(p)
                keys = ", ".join(list(doc.keys())[:15]) if isinstance(doc, dict) else (f"list[{len(doc)}]" if isinstance(doc, list) else type(doc).__name__)
                rows.append([rel, os.path.getsize(p), keys[:200]])
    write("yaml-files.md", text + md_table(rows, ["file", "bytes", "top-level keys"]))

    # ---- dashboards.md ---------------------------------------------------------
    dash = jload(os.path.join(S, "lovelace_dashboards")) or {}
    dash_items = {d["id"]: d for d in dash.get("data", {}).get("items", [])}
    text = f"# {host} — Lovelace dashboards\n\n"
    files = sorted(f for f in os.listdir(S) if f == "lovelace" or f.startswith("lovelace.")) if os.path.isdir(S) else []
    for f in files:
        doc = jload(os.path.join(S, f)) or {}
        cfg = doc.get("data", {}).get("config", {}) or {}
        key = f.split(".", 1)[1] if "." in f else "(default)"
        meta = dash_items.get(key, {})
        text += f"## {f}  — url `{meta.get('url_path', 'lovelace' if key == '(default)' else key)}`  title `{meta.get('title') or cfg.get('title') or ''}`  ({os.path.getsize(os.path.join(S, f))} bytes)\n\n"
        views = cfg.get("views", []) or []
        if not views:
            text += "_no views / strategy dashboard_\n\n"
        for v in views:
            cards = v.get("cards", []) or []
            for sec in v.get("sections", []) or []:
                cards += sec.get("cards", []) or []
            types = Counter(c.get("type", "?") for c in cards)
            text += f"- view **{v.get('title') or v.get('path') or '?'}** — {len(cards)} cards ({', '.join(f'{t}×{n}' for t, n in types.most_common())})\n"
            refs = entity_refs(v)
            if refs:
                text += f"  - entities: {', '.join(refs)[:1500]}\n"
        text += "\n"
    res = jload(os.path.join(S, "lovelace_resources")) or {}
    text += "## resources (custom cards JS)\n\n" + "\n".join(f"- `{r.get('url')}` ({r.get('res_type')})" for r in res.get("data", {}).get("items", [])) + "\n"
    write("dashboards.md", text)

    # ---- voice / exposure ------------------------------------------------------
    text = f"# {host} — entity exposure (emulated_hue, assistants)\n\n"
    eh = jload(os.path.join(S, "emulated_hue.ids")) or {}
    text += "## emulated_hue.ids (Alexa via Hue emulation)\n\n" + "\n".join(f"- {n}: {e}" for n, e in sorted((eh.get("data") or {}).items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0)) + "\n\n"
    ehy = yload(os.path.join(C, "emulated_hue.yaml"))
    if ehy is not None:
        text += "## emulated_hue.yaml\n\n```yaml\n" + open(os.path.join(C, "emulated_hue.yaml"), encoding="utf-8").read() + "```\n\n"
    ex = jload(os.path.join(S, "homeassistant.exposed_entities")) or {}
    exp = (ex.get("data") or {}).get("exposed_entities", {}) or {}
    rows = [[eid, ", ".join(k for k, v in (a.get("assistants", {}) or {}).items() if v.get("should_expose"))] for eid, a in sorted(exp.items())]
    rows = [r for r in rows if r[1]]
    text += f"## exposed to assistants ({len(rows)})\n\n" + md_table(rows, ["entity_id", "assistants"])
    write("exposure.md", text)

    # ---- addons.md / hacs.md -----------------------------------------------------
    text = f"# {host} — add-ons & supervisor\n\n"
    sup = jload(os.path.join(M, "ha-supervisor.json")) or {}
    core = jload(os.path.join(M, "ha-core.json")) or {}
    osj = jload(os.path.join(M, "ha-os.json")) or {}
    d = lambda j: (j.get("data") or j) if isinstance(j, dict) else {}
    text += f"- Core: `{d(core).get('version')}` (latest `{d(core).get('version_latest')}`)  arch `{d(core).get('arch')}`\n"
    text += f"- Supervisor: `{d(sup).get('version')}`  channel `{d(sup).get('channel')}`  healthy `{d(sup).get('healthy')}`  supported `{d(sup).get('supported')}`\n"
    text += f"- OS: `{d(osj).get('version')}`  board `{d(osj).get('board')}`\n\n"
    ad = jload(os.path.join(M, "ha-addons.json")) or {}
    rows = [[a.get("name"), a.get("slug"), a.get("version"), a.get("version_latest"), a.get("state"), "yes" if a.get("update_available") else ""]
            for a in sorted((d(ad).get("addons") or []), key=lambda a: a.get("name", ""))]
    text += "## add-ons\n\n" + md_table(rows, ["name", "slug", "version", "latest", "state", "update?"])
    A = os.path.join(host_dir, "addons")
    if os.path.isdir(A):
        text += "\n## add-on config files captured\n\n"
        for dirpath, _, files in os.walk(A):
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                text += f"- `{os.path.relpath(p, host_dir)}` ({os.path.getsize(p)} bytes)\n"
    write("addons.md", text)

    text = f"# {host} — HACS\n\n"
    hacs_dir = os.path.join(S, "hacs")
    rows = []
    if os.path.isdir(hacs_dir):
        for f in sorted(os.listdir(hacs_dir)):
            doc = jload(os.path.join(hacs_dir, f)) or {}
            dd = doc.get("data", {}) or {}
            rows.append([dd.get("full_name") or dd.get("repository_manifest", {}).get("name") or f, dd.get("category", ""), dd.get("version_installed") or dd.get("installed_version", ""), dd.get("last_version") or dd.get("last_release", ""), "yes" if dd.get("installed") else ""])
    text += "## per-repository state (.storage/hacs/*)\n\n" + md_table(rows, ["repository", "category", "installed", "latest", "installed?"])
    rep = jload(os.path.join(S, "hacs.repositories")) or {}
    inst = []
    for rid, r in ((rep.get("data") or {}).items()):
        if r.get("installed"):
            inst.append([r.get("full_name"), r.get("category"), r.get("installed_version") or r.get("version_installed"), r.get("last_version"), rid])
    text += "\n## installed repositories (from hacs.repositories)\n\n" + md_table(sorted(inst, key=lambda r: str(r[0])), ["repository", "category", "installed", "latest", "id"])
    write("hacs.md", text)

    # ---- summary.md ------------------------------------------------------------
    info = open(os.path.join(M, "export-info.yaml"), encoding="utf-8").read() if os.path.exists(os.path.join(M, "export-info.yaml")) else ""
    skipped = open(os.path.join(M, "skipped.txt"), encoding="utf-8").read() if os.path.exists(os.path.join(M, "skipped.txt")) else ""
    plat = Counter(e.get("platform") for e in entities)
    text = f"# {host} — snapshot summary\n\n```\n{info}```\n\n"
    text += f"- config entries: {len(entries)}  (custom components on disk: {len(custom)})\n- devices: {len(devices)}\n- entities: {len(entities)} across {len(plat)} platforms\n- areas: {len(areas)}\n\n"
    text += "## entities per platform\n\n" + md_table(plat.most_common(), ["platform", "entities"])
    text += "\n## files deliberately not exported\n\n```\n" + skipped + "```\n"
    text += "\n## digests written\n\n" + "\n".join(f"- {w}" for w in written + ["summary.md"]) + "\n"
    write("summary.md", text)
    print(f"{host}: wrote {len(written)} digest files to {D}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit("usage: digest.py hosts/<host>")
    main(sys.argv[1])
