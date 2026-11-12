#!/usr/bin/env python3
"""ste.py - one entry point for the ASD-STE100 skill (Python 3 standard library only).

Subcommands:
  review FILE           one call for the first pass: scan, proposed fixes (count and list),
                        check findings; --source SRC adds the accuracy check
  lookup WORD...        status of each word: local dictionary, term pack, project terms
  scan FILE             words in a document that no layer knows (--candidates OUT writes them)
  check FILE            checker: findings grouped by rule (--all, --json, --source SRC)
  fix FILE              safe automatic replacements; a diff by default, --write applies
  count TEXT...         STE word count of a phrase or sentence (rules 5.1, 6.3, 2.1)
  terms add ENTRY...    add entries (or --from FILE) to the project terms file
  import-dictionary SRC build a local word list from the user's own copy of the standard

Layers, highest precedence first: project terms file, domain term packs
(--domain), the local official word list (import-dictionary; not in the repository),
general word lists (assets/words/). The project terms file is
ste-terms.txt in the working directory or next to the checked document;
--terms FILE overrides the search. A "# domain: NAME" line in it sets the
default domain. Entries: "term | TN or TV | category | std or ext; note"
(a bare term per line is also accepted).

Data: assets/words/*.txt and assets/terms/<domain>.txt (see the file headers).
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS_DIR = os.path.join(SKILL_DIR, "assets", "words")
TERMS_DIR = os.path.join(SKILL_DIR, "assets", "terms")
PROJECT_FILE = "ste-terms.txt"
PROCEDURE_REF = "references/term-overview.md"
LOCAL_ENV = "STE100_DICTIONARY"
OFFICIAL_APPROVED, OFFICIAL_NOT_APPROVED = 875, 1274


class DataError(Exception):
    pass


def fail(msg, code=1):
    print(f"ste.py: {msg}", file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def data_rows(path):
    """Yield (line number, fields) for each data line of a ' | ' separated file."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise DataError(f"cannot read the data file {path}: {e.strerror}. "
                        "The skill folder is incomplete; reinstall or restore assets/words/.")
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if s and not s.startswith("#"):
            yield n, [p.strip() for p in s.split(" | ")]


def _rows(name, count):
    path = os.path.join(WORDS_DIR, name)
    out = []
    for n, f in data_rows(path):
        if len(f) != count:
            raise DataError(f"{path}, line {n}: expected {count} fields separated by ' | ', got {len(f)}")
        out.append(f)
    return out


def _flags(s):
    return set() if s in ("-", "") else {x.strip() for x in s.split(",")}


def _none(s):
    return None if s in ("-", "") else s


def load_general():
    g = {"unapproved": {}, "approved": set(), "pos": {}, "two": {}, "modals": {},
         "phrases": [], "phrasal": [], "patterns": [], "british": {},
         "contractions": {}, "jargon": [], "lists": {}, "function": set()}
    for f in _rows("unapproved.txt", 7):
        word, section, pos, alt, flags, note, example = f
        fl = _flags(flags)
        g["unapproved"][word.lower()] = {
            "word": word.lower(), "section": section, "pos": _none(pos), "alt": alt,
            "check": "check" in fl, "soft": "soft" in fl, "auto": "auto" in fl,
            "number": "number" in fl, "note": _none(note) or "", "example": _none(example) or ""}
    g["approved"] = {f[0].lower() for f in _rows("approved-verbs.txt", 1)}
    for f in _rows("part-of-speech.txt", 4):
        g["pos"][f[0].lower()] = {"approved": f[1], "not_approved": f[2], "write": f[3]}
    for f in _rows("two-statuses.txt", 3):
        g["two"][f[0].lower()] = {"general": f[1], "specific": f[2]}
    for f in _rows("modals.txt", 2):
        g["modals"][f[0].lower()] = f[1]
    for f in _rows("phrases.txt", 6):
        phrase, kind, rule, sev, alt, flags = f
        item = {"phrase": phrase.lower(), "rule": rule, "sev": sev, "alt": alt,
                "auto": "auto" in _flags(flags),
                "rx": re.compile(r"\b" + r"\s+".join(map(re.escape, phrase.lower().split())) + r"\b")}
        if kind == "phrasal":
            item["msg"] = f'Phrasal verb "{phrase.lower()}" -> {alt.lower()}'
            g["phrasal"].append(item)
        else:
            item["msg"] = f'"{phrase.lower()}" -> {alt.lower()}'
            g["phrases"].append(item)
    # noun-only words: approved as a noun, not approved as a verb (rule 1.2)
    noun_only = sorted(w for w, d in g["pos"].items()
                       if "noun" in re.split(r"[;,] ?", d["approved"]) and d["not_approved"] == "verb")
    g["noun_only"] = noun_only
    VERB = "(?<!do )(?<!does )(?<!did )(?:" + "|".join(map(re.escape, noun_only)) + ")"
    DET = "|".join(["the", "that", "a", "an", "this", "these", "those", "each", "every", "your", "all",
                    "it", "for", "if", "any", "its", "their", "them", "whether", "both"])
    for f in _rows("patterns.txt", 6):
        regex, rule, sev, msg, flags, repl = f
        fl = _flags(flags)
        if "verbuse" in fl:
            regex = regex.replace("{V}", VERB).replace("{DET}", DET)
        cs = "cs" in fl
        g["patterns"].append({
            "rule": rule, "sev": sev, "msg": after_arrow_lower(msg), "cs": cs, "auto": "auto" in fl,
            "verbuse": "verbuse" in fl,
            "repl": _none(repl),
            "rx": re.compile(regex, 0 if cs else re.IGNORECASE),
            "fix_rx": re.compile(regex, 0 if cs else re.IGNORECASE)})
    for f in _rows("british.txt", 2):
        g["british"][f[0].lower()] = f[1]
    for f in _rows("contractions.txt", 3):
        g["contractions"][f[0].lower()] = {"expansion": f[1], "auto": "auto" in _flags(f[2])}
    for f in _rows("jargon.txt", 4):
        g["jargon"].append({"jargon": f[0].lower(), "preferred": f[1], "domain": f[2],
                            "auto": "auto" in _flags(f[3])})
    lists = {}
    path = os.path.join(WORDS_DIR, "checker-lists.txt")
    for n, s in data_rows_raw(path):
        key, _, rest = s.partition(":")
        key = key.strip()
        if key.startswith("regex_"):
            lists[key] = rest.strip()
        elif key == "skip_before":
            lists[key] = dict(x.split(">") for x in rest.split())
        else:
            lists[key] = rest.split()
    g["lists"] = lists
    for n, f in data_rows(os.path.join(WORDS_DIR, "function-words.txt")):
        g["function"].add(f[0].lower())
    return g


def data_rows_raw(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise DataError(f"cannot read the data file {path}: {e.strerror}.")
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if s and not s.startswith("#"):
            yield n, s


def parse_term_line(f, layer, where):
    """f: fields of one term line. Returns an entry dict."""
    if len(f) == 1:
        term, typ, cat, note = f[0], "-", "-", ""
    elif len(f) == 2:
        term, typ, cat, note = f[0], f[1], "-", ""
    elif len(f) == 3:
        term, typ, cat, note = f[0], f[1], f[2], ""
    else:
        term, typ, cat, note = f[0], f[1], f[2], " | ".join(f[3:])
    if not term:
        raise DataError(f"{where}: empty term")
    syn = []
    m = re.search(r"also called (.+)$", note)
    if m:
        syn = [re.sub(r"\(.*?\)", "", x).strip() for x in m.group(1).split(",") if x.strip()]
    return {"term": term, "lower": term.lower(), "type": typ, "cat": cat, "note": note,
            "layer": layer, "synonyms": syn}


def load_pack(domain):
    path = os.path.join(TERMS_DIR, domain + ".txt")
    if not os.path.isfile(path):
        avail = sorted(x[:-4] for x in os.listdir(TERMS_DIR) if x.endswith(".txt"))
        raise DataError(f"no term pack named '{domain}' (available: {', '.join(avail)})")
    entries = []
    for n, f in data_rows(path):
        entries.append(parse_term_line(f, f"{domain} pack", f"{path}, line {n}"))
    return entries


def load_project(path):
    """Returns (entries, default domain or None)."""
    entries, domain = [], None
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise DataError(f"cannot read the terms file {path}: {e.strerror}.")
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            m = re.match(r"#\s*domain:\s*([\w-]+)", s)
            if m:
                domain = m.group(1)
            continue
        if s:
            entries.append(parse_term_line([p.strip() for p in s.split(" | ")],
                                           "project terms file", f"{path}, line {n}"))
    return entries, domain


def find_project(explicit, doc_path):
    if explicit:
        return explicit
    cands = [os.path.join(os.getcwd(), PROJECT_FILE)]
    if doc_path:
        cands.append(os.path.join(os.path.dirname(os.path.abspath(doc_path)), PROJECT_FILE))
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def default_local_path():
    """The local word list: $STE100_DICTIONARY, else ~/.config/ste100/dictionary.txt
    (XDG_CONFIG_HOME is respected). Returns (path, set_by_env)."""
    env = os.environ.get(LOCAL_ENV)
    if env:
        return os.path.expanduser(env), True
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "ste100", "dictionary.txt"), False


def load_local(path):
    """Read a file written by import-dictionary. Returns
    {"approved": {word: {pos}}, "unapproved": {word: {"pos": {pos}, "alts": [words]}}}."""
    approved, unapproved = {}, {}
    for n, f in data_rows(path):
        if len(f) not in (3, 4) or f[2] not in ("yes", "no"):
            raise DataError(f"{path}, line {n}: expected 'word | pos | yes or no | alternatives'. "
                            "Run import-dictionary again.")
        word, pos = f[0].lower(), f[1]
        if f[2] == "yes":
            approved.setdefault(word, set()).add(pos)
            continue
        e = unapproved.setdefault(word, {"pos": set(), "alts": []})
        e["pos"].add(pos)
        if len(f) == 4 and f[3] not in ("", "-"):
            for a in f[3].split(";"):
                a = a.strip().lower()
                if a and a not in e["alts"]:
                    e["alts"].append(a)
    return {"approved": approved, "unapproved": unapproved}


class Context:
    """All active layers for one run."""

    def __init__(self, domains=(), terms_file=None, doc_path=None, required=True, use_local=True):
        self.g = load_general()
        self.lists = self.g["lists"]
        self.project_path = None
        self.local = {"approved": {}, "unapproved": {}}
        self.local_path = None
        if use_local:
            path, explicit = default_local_path()
            if os.path.isfile(path):
                self.local = load_local(path)
                self.local_path = path
            elif explicit:
                raise DataError(f"the local word list {path} does not exist "
                                f"(set by ${LOCAL_ENV}). Run import-dictionary or unset it.")
        proj_entries, header_domain = [], None
        path = find_project(terms_file, doc_path)
        if terms_file and not os.path.isfile(terms_file):
            if required:
                raise DataError(f"the terms file {terms_file} does not exist")
            print(f"Cannot read the terms file {terms_file}. The check continues without it.",
                  file=sys.stderr)
            path = None
        if path:
            proj_entries, header_domain = load_project(path)
            self.project_path = path
        doms = list(domains)
        if not doms and header_domain:
            doms = [header_domain]
        self.domains = doms
        self.packs = {d: load_pack(d) for d in doms}
        self.terms = {}
        for e in proj_entries + [e for d in doms for e in self.packs[d]]:
            self.terms.setdefault(e["lower"], []).append(e)
        self.multi = [k for k in self.terms if " " in k]
        self.term_words = {k for k in self.terms if " " not in k}
        self.jargon = [j for j in self.g["jargon"] if j["domain"] == "general" or j["domain"] in doms]
        self.synonyms = [e for es in self.terms.values() for e in es if e["synonyms"]]

    def layers_text(self):
        parts = []
        if self.project_path:
            parts.append(f"project terms file {os.path.basename(self.project_path)}")
        parts += [f"{d} pack" for d in self.domains]
        if self.local_path:
            parts.append("local official word list")
        parts.append("bundled word lists")
        return ", ".join(parts)


# --------------------------------------------------------------------------
# lookup
# --------------------------------------------------------------------------

def term_status(ctx, w):
    ents = ctx.terms.get(w)
    if not ents:
        return None
    parts, seen = [], set()
    for e in ents:
        kind = {"TN": "technical noun", "TV": "technical verb"}.get(e["type"].upper(), "accepted term")
        if e["layer"] == "project terms file":
            label = "project terms file"
        else:
            label = f"{e['layer'].replace(' pack', '')} pack" + (f", category {e['cat']}" if e["cat"] != "-" else "")
        key = (kind, label)
        if key not in seen:
            seen.add(key)
            parts.append(f"{kind} ({label})")
    text = " and ".join(parts)
    note = next((e["note"] for e in ents if e["note"]), "")
    if note:
        text += "; " + note
    return text


def plain(s):
    """Suggestions are written in normal case (rule 9.2 notation: capitals are only in the data)."""
    return s.lower()


def trap_text(ctx, w):
    """The bundled part-of-speech or two-status note for a word, if any."""
    g = ctx.g
    if w in g["two"]:
        d = g["two"][w]
        return f"two statuses: general sense: {d['general']}; specific sense: {d['specific']}"
    if w in g["pos"]:
        d = g["pos"][w]
        text = f"approved as {d['approved']}"
        if d["not_approved"] and d["not_approved"] != "-":
            text += f"; not approved as {d['not_approved']} -> {plain(d['write'])}"
        return text
    return ""


def lookup_word(ctx, word):
    w = " ".join(word.lower().split())
    g = ctx.g
    t = term_status(ctx, w)
    if t:
        return {"word": word, "status": t, "kind": "term"}
    loc = ctx.local
    if w in loc["approved"]:
        pos = ", ".join(sorted(loc["approved"][w]))
        status = f"approved ({pos}) in the local word list"
        extra = trap_text(ctx, w)
        if extra:
            status += "; " + extra
        return {"word": word, "status": status, "kind": "approved"}
    if w in loc["unapproved"] and w not in g["unapproved"] and w not in g["modals"]:
        # the bundled list gives the firm status for these words (it is checked and suggested)
        e = loc["unapproved"][w]
        pos = " / ".join(sorted(e["pos"]))
        alt = " or ".join(e["alts"][:4]) if e["alts"] else None
        status = f"not approved ({pos}) in the local word list"
        status += f" -> {alt}" if alt else " (no alternative listed)"
        return {"word": word, "status": status, "kind": "unapproved", "alt": alt, "local": True}
    if w in g["two"]:
        d = g["two"][w]
        return {"word": word, "status": f"two statuses: general sense: {d['general']}; "
                                        f"specific sense: {d['specific']}", "kind": "two"}
    if w in g["pos"]:
        d = g["pos"][w]
        status = f"approved as {d['approved']}"
        if d["not_approved"] and d["not_approved"] != "-":
            status += f"; not approved as {d['not_approved']} -> {plain(d['write'])}"
        return {"word": word, "status": status, "kind": "pos"}
    if w in g["approved"]:
        return {"word": word, "status": "approved verb", "kind": "approved"}
    if w in g["unapproved"]:
        e = g["unapproved"][w]
        pos = f" as {e['pos']}" if e["pos"] else ""
        note = f" ({e['note']})" if e["note"] and not e["note"].startswith("sense") else ""
        return {"word": word, "status": f"not approved{pos} -> {plain(e['alt'])}{note}", "kind": "unapproved",
                "alt": plain(e["alt"])}
    if w in g["modals"]:
        return {"word": word, "status": f"not approved -> {plain(g['modals'][w])}", "kind": "unapproved",
                "alt": plain(g["modals"][w])}
    if w.replace("’", "'") in g["contractions"]:
        exp = g["contractions"][w.replace("’", "'")]["expansion"]
        return {"word": word, "status": f"contraction, not approved -> {exp}", "kind": "unapproved",
                "alt": exp}
    for ph in g["phrases"]:
        if ph["phrase"] == w:
            return {"word": word, "status": f"not approved -> {plain(ph['alt'])}", "kind": "unapproved",
                    "alt": plain(ph["alt"])}
    return {"word": word, "status": f"not in the word lists -> use the decision procedure in {PROCEDURE_REF}",
            "kind": "unknown"}


# --------------------------------------------------------------------------
# Text preparation (shared by scan and fix)
# --------------------------------------------------------------------------

PROTECT_RX = re.compile(r"`[^`\n]*`|\*\*[^*\n]+\*\*|\"[^\"\n]*\"|“[^”\n]*”|https?://\S+|\[[^\]\n]*\]\([^)\n]*\)")


def prose_lines(raw):
    """Yield (line number, line, masked line) for prose. Code blocks, front matter,
    indented code and protected spans (quotes, code spans, bold UI labels, links)
    are masked with \\x01 so no pattern matches inside them."""
    lines = raw.splitlines()
    in_code = in_front = False
    for i, line in enumerate(lines, 1):
        if i == 1 and line.strip() == "---":
            in_front = True
            yield i, line, None
            continue
        if in_front:
            if line.strip() == "---":
                in_front = False
            yield i, line, None
            continue
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
            yield i, line, None
            continue
        if in_code or re.match(r"^( {4,}|\t)", line):
            yield i, line, None
            continue
        masked = list(line)
        for m in PROTECT_RX.finditer(line):
            for k in range(m.start(), m.end()):
                masked[k] = "\x01"
        yield i, line, "".join(masked)


WORD_RX = re.compile(r"[A-Za-z][A-Za-z'’\-]*")


def scan_words(raw, ctx):
    """Word tokens in prose, skipping code, quotes, UI labels, links, numbers and
    all-capital acronyms. Yields (line, lowercase word)."""
    for i, line, masked in prose_lines(raw):
        if masked is None:
            continue
        text = masked.replace("\x01", " ")
        low = text.lower()
        for ph in ctx.multi:
            for m in re.finditer(r"\b" + r"\s+".join(map(re.escape, ph.split())) + r"\b", low):
                text = text[:m.start()] + " " * (m.end() - m.start()) + text[m.end():]
                low = low[:m.start()] + " " * (m.end() - m.start()) + low[m.end():]
        for m in WORD_RX.finditer(text):
            tok = m.group(0)
            if len(tok) > 1 and tok.isupper():
                continue
            yield i, tok.lower().strip("-'’")


def scan_result(raw, ctx):
    """Unapproved, known and unknown words of a document (shared by scan and review)."""
    unapproved, known, unknown = {}, Counter(), {}
    for line, w in scan_words(raw, ctx):
        if not w or len(w) < 2:
            continue
        st = lookup_word(ctx, w)
        if st["kind"] == "unknown":
            # an inflected form of a known term or approved verb ("deployed" -> "deploy")
            for base in lemma_candidates(w)[1:]:
                b = lookup_word(ctx, base)
                if b["kind"] in ("term", "approved", "two"):
                    st = b
                    break
        if st["kind"] in ("term", "two", "pos", "approved"):
            known[w] += 1
        elif st["kind"] == "unapproved" and st.get("local"):
            # not approved as one part of speech; the word may be a technical noun. Decide it.
            if w in ctx.g["function"]:
                continue
            unknown.setdefault(w, {"line": line, "note": st["status"]})
        elif st["kind"] == "unapproved":
            unapproved.setdefault(w, {"count": 0, "line": line, "alt": st.get("alt")})["count"] += 1
        elif w in ctx.g["function"]:
            continue
        else:
            unknown.setdefault(w, {"line": line})
    unknown_count = Counter(w for _, w in scan_words(raw, ctx) if w in unknown)
    unknown_list = sorted(unknown.items(), key=lambda kv: kv[1]["line"])
    summary = {"unapproved_found": sum(v["count"] for v in unapproved.values()),
               "unapproved_distinct": len(unapproved),
               "terms_recognised": sum(known.values()),
               "unknown_distinct": len(unknown),
               "unknown_occurrences": sum(unknown_count.values())}
    return {"unapproved": unapproved, "unknown": unknown_list, "unknown_count": unknown_count,
            "summary": summary}


def write_candidates(path, unknown):
    """Write the unknown words as a terms file. The author's agent deletes the lines that are
    not terms, then passes the file with --terms. One file for the whole list (no terms add)."""
    lines = ["# Candidate terms from scan, in the project terms format. Delete each line that is",
             "# not a subject-field term. Then pass this file with --terms FILE (one command).",
             "# Format: term | TN or TV | category | std or ext; note"]
    for w, v in unknown:
        lines.append(f"{w} | TN | - | ext; candidate from line {v['line']}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(unknown)


def print_scan(res, ctx, file_name, examples_note=True):
    s = res["summary"]
    print(f"STE scan: {file_name}")
    print(f"Layers: {ctx.layers_text()}")
    print(f"{s['unapproved_found']} unapproved words found ({s['unapproved_distinct']} distinct), "
          f"{s['terms_recognised']} domain or known terms recognised, "
          f"{s['unknown_distinct']} unknown words ({s['unknown_occurrences']} occurrences).")
    if res["unapproved"]:
        print("\nUnapproved words:")
        for w, v in sorted(res["unapproved"].items(), key=lambda kv: kv[1]["line"]):
            alt = f" -> {v['alt']}" if v["alt"] else " (no alternative listed; rewrite, rule 9.1)"
            print(f"  line {v['line']:<5} {w} ({v['count']}){alt}")
    if res["unknown"]:
        print("\nUnknown words (no layer knows them). Decide each one. Accepted terms: write the "
              "candidates file (--candidates), delete the lines that are not terms, and pass it with "
              "--terms. Do not run terms add once per word.")
        for w, v in res["unknown"]:
            note = f" -- {v['note']}" if v.get("note") else ""
            print(f"  line {v['line']:<5} {w} ({res['unknown_count'].get(w, 0)}){note}")
    else:
        print("\nNo unknown words.")


def cmd_scan(args):
    ctx = Context(args.domain, args.terms, args.file, required=True, use_local=not args.no_local_dictionary)
    raw = read_text(args.file)
    res = scan_result(raw, ctx)
    if args.json:
        json.dump({"file": args.file, "layers": ctx.layers_text(), "summary": res["summary"],
                   "unapproved": [{"word": w, **v} for w, v in sorted(res["unapproved"].items(),
                                                                      key=lambda kv: kv[1]["line"])],
                   "unknown": [{"word": w, "count": res["unknown_count"].get(w, 0), "line": v["line"]}
                               for w, v in res["unknown"]]}, sys.stdout, indent=2)
        print()
    else:
        print_scan(res, ctx, args.file)
    if args.candidates:
        n = write_candidates(args.candidates, res["unknown"])
        print(f"\n{n} candidate terms written to {args.candidates}.", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# check (first-pass checker; the rules are the same as in the original script)
# --------------------------------------------------------------------------

def lemma_candidates(w):
    c = [w]
    if w.endswith("ies") and len(w) > 4:
        c.append(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3:
        c.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        c.append(w[:-1])
    if w.endswith("ied") and len(w) > 4:
        c.append(w[:-3] + "y")
    if w.endswith("ed") and len(w) > 3:
        c += [w[:-2], w[:-1]]
        if len(w) > 5 and w[-3] == w[-4]:
            c.append(w[:-3])
    if w.endswith("ing") and len(w) > 5:
        c += [w[:-3], w[:-3] + "e"]
        if w[-4] == w[-5]:
            c.append(w[:-4])
    return c


CONTRACTION = re.compile(
    r"\b(?:[A-Za-z]+n[’']t|[A-Za-z]+[’'](?:ll|re|ve|d|m)|"
    r"(?:it|that|there|here|what|who|he|she|let|where|how)[’']s)\b",
    re.IGNORECASE,
)
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
SAFETY_RE = re.compile(r"^\s*(?:>\s*)?(?:\*\*|__)?\s*(WARNING|CAUTION|DANGER|NOTICE)\b\s*:?", re.I)
NOTE_RE = re.compile(r"^\s*(?:>\s*)?(?:\*\*|__)?\s*(NOTE|Note|TIP|Tip)\b\s*:?(?:\*\*|__)?\s*:?")


def is_participle(w, L):
    if w in set(L["not_participles"]):
        return False
    if w in set(L["irregular_participles"]):
        return True
    return len(w) > 3 and w.endswith("ed")


def mask(text):
    text = re.sub(r"`[^`\n]+`", "CODE", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "URL", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", lambda m: m.group(1), text)
    text = re.sub(r"(?<!\w)[*_]([^*_\n]+)[*_](?!\w)", r"\1", text)
    return text


def count_words(sentence):
    s = re.sub(r"\([^()]*\)", " PAREN ", sentence)
    s = re.sub(r'"[^"]*"|“[^”]*”', " QUOTE ", s)
    s = re.sub(r"\b\d+(?:[.,]\d+)*\s?(?:°\s?[CF]|%|[A-Za-zµ]{1,4}\b(?=\W|$))?",
               lambda m: " NUM " if re.fullmatch(
                   r"\d+(?:[.,]\d+)*\s?(?:°\s?[CF]|%|mm|cm|m|km|in|ft|kg|g|mg|lb|oz|psi|bar|kPa|MPa|Pa|Nm|N|V|mV|kV|A|mA|W|kW|Hz|kHz|MHz|GHz|rpm|s|ms|min|h|hr|L|l|ml|mL|GB|MB|KB|TB|kB)?",
                   m.group(0)) else " NUM " + " X ", s)
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-./_]*", s)
    return len(tokens)


def split_sentences(text):
    protected = re.sub(r"\b(e\.g|i\.e|vs|Fig|No|approx|max|min|Mr|Ms|Dr|St|Ref|para)\.",
                       lambda m: m.group(0).replace(".", "§"), text)
    protected = re.sub(r"(\d)\.(\d)", r"\1§\2", protected)
    parts = re.split(r"(?<=[.!?])\s+(?=[\"“(A-Z0-9])|(?<=:)\s*\n", protected)
    return [p.replace("§", ".").strip() for p in parts if p.strip()]


class Block:
    def __init__(self, kind, line, text):
        self.kind, self.line, self.text = kind, line, text


def parse_blocks(raw):
    lines = raw.splitlines()
    blocks, buf, buf_line, buf_kind = [], [], 0, None
    in_code = in_front = False

    def flush():
        nonlocal buf, buf_kind
        if buf:
            blocks.append(Block(buf_kind, buf_line, " ".join(buf)))
        buf, buf_kind = [], None

    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if i == 1 and s.strip() == "---":
            in_front = True
            continue
        if in_front:
            if s.strip() == "---":
                in_front = False
            continue
        if re.match(r"^\s*(```|~~~)", s):
            flush()
            in_code = not in_code
            continue
        if in_code or re.match(r"^( {4,}|\t)\S", line) and not buf:
            continue
        if not s.strip():
            flush()
            continue
        if re.match(r"^\s*\|", s) or re.match(r"^\s*[-=*_]{3,}\s*$", s) or re.match(r"^\s*<[^>]+>\s*$", s):
            flush()
            if re.match(r"^\s*\|", s) and not re.match(r"^\s*\|[\s:|-]+\|\s*$", s):
                for cell in s.strip().strip("|").split("|"):
                    if len(cell.split()) > 3:
                        blocks.append(Block("cell", i, cell.strip()))
            continue
        m = re.match(r"^\s*#{1,6}\s+(.*)$", s)
        if m:
            flush()
            blocks.append(Block("heading", i, m.group(1)))
            continue
        if SAFETY_RE.match(s):
            flush()
            buf, buf_line, buf_kind = [SAFETY_RE.sub("", s).strip(" *_:")], i, "safety"
            continue
        if NOTE_RE.match(s):
            flush()
            buf, buf_line, buf_kind = [NOTE_RE.sub("", s).strip(" *_:")], i, "note"
            continue
        m = re.match(r"^\s*(?:\d+[.)]|[a-z][.)]|\(\d+\)|\([a-z]\)|Step\s+\d+[.:])\s+(.*)$", s)
        if m:
            flush()
            buf, buf_line, buf_kind = [m.group(1)], i, "step"
            continue
        m = re.match(r"^\s*(?:[-*+•]|\[[ xX]\])\s+(.*)$", s)
        if m:
            flush()
            buf, buf_line, buf_kind = [m.group(1)], i, "bullet"
            continue
        s2 = re.sub(r"^\s*>\s?", "", s)
        if buf:
            buf.append(s2.strip())
        else:
            buf, buf_line, buf_kind = [s2.strip()], i, "para"
    flush()
    return blocks


def check_sentence(sent, line, kind, mode, ctx, out, seq=0):
    g, L = ctx.g, ctx.lists
    BE, HAVE = set(L["be_forms"]), set(L["have_forms"])
    STATE_ADJ, ING_OK = set(L["state_adjectives"]), set(L["approved_ing"])
    IMPERATIVE = set(L["imperative_hints"])
    NOUN_WORDS = set(L["noun_words"])
    SKIP_BEFORE = L["skip_before"]
    SKIP_INFL = set(L["skip_inflected"])
    checked = ctx.checked

    def add(rule, sev, msg, hit=""):
        out.append({"line": line, "seq": seq, "rule": rule, "severity": sev,
                    "message": msg, "match": hit, "sentence": sent})

    if kind == "note":
        procedure = False
    else:
        procedure = mode == "procedure" or (mode == "auto" and kind in ("step", "safety"))
    limit = 20 if procedure else 25
    n = count_words(sent)
    if kind != "heading" and n > limit:
        add("5.1" if procedure else "6.3", "error",
            f"Sentence has {n} words. The maximum is {limit} for "
            f"{'a procedure' if procedure else 'a description'}.")
    if ";" in sent:
        add("8.1", "error", "Do not use the semicolon. Make two sentences or a list.", ";")
    for m in CONTRACTION.finditer(sent):
        add("4.2", "error", "Do not use contractions.", m.group(0))

    low = sent.lower()
    verb_words, seen_pos = set(), set()
    for p in g["patterns"]:
        subject = sent if p["cs"] else low
        for m in p["rx"].finditer(subject):
            if p["verbuse"]:
                if m.start("w") in seen_pos:
                    continue
                seen_pos.add(m.start("w"))
                w = m.group("w")
                verb_words.add(w)
                add("1.2", "error", f'"{w}" is a noun in this use, not a verb (rule 1.2). '
                    f'Write: {plain(g["pos"][w]["write"])}.', w)
                continue
            add(p["rule"], p["sev"], p["msg"], m.group(0).strip())
    for ph in g["phrases"]:
        for m in ph["rx"].finditer(low):
            add(ph["rule"], ph["sev"], ph["msg"], m.group(0).strip())
    for ph in g["phrasal"]:
        a, *rest = ph["phrase"].split()
        rx = r"\b" + a + r"(?:s|ed|ing)?\s+(?:(?!to\b)\w+\s+){0,2}?" + r"\s+".join(rest) + r"\b" \
            if len(rest) == 1 else r"\b" + ph["phrase"].replace(" ", r"\s+") + r"\b"
        m = re.search(rx, low)
        if m and (len(m.group(0).split()) == len(ph["phrase"].split())
                  or a in ("turn", "switch", "shut", "plug", "hook", "pick")):
            add("9.3", "warning", ph["msg"], m.group(0))

    words = [(m.group(0), m.start()) for m in WORD.finditer(sent)]
    lows = [w.lower().replace("’", "'") for w, _ in words]
    covered = set()
    for mt in ctx.multi:
        for m in re.finditer(r"\b" + r"\s+".join(map(re.escape, mt.split())) + r"\b", low):
            for idx, (_, pos) in enumerate(words):
                if m.start() <= pos < m.end():
                    covered.add(idx)
    seen, term_notes = set(), set()
    for idx, w in enumerate(lows):
        raw = words[idx][0]
        if idx in covered or w in ctx.term_words:
            ents = ctx.terms.get(w, [])
            for e in ents:
                if re.search(r"general sense (not approved|:)", e["note"]) and (w, e["note"]) not in term_notes:
                    term_notes.add((w, e["note"]))
                    add("1.1", "info", e["note"], raw)
            if idx in covered or w in ctx.term_words:
                continue
        if raw in ("CODE", "URL") or (raw.isupper() and len(raw) > 1):
            continue
        if w in g["modals"]:
            add("3.4", "error", f'"{raw}" is not approved -> {plain(g["modals"][w])}', raw)
            continue
        if w in g["british"]:
            add("1.14", "warning", f'Use American spelling: "{g["british"][w]}"', raw)
        hit = next((c for c in lemma_candidates(w) if c in checked), None)
        if hit and hit not in seen and hit not in verb_words \
                and not any(c in ctx.term_words for c in lemma_candidates(w)):
            nxt = lows[idx + 1] if idx + 1 < len(lows) else ""
            if (hit in SKIP_BEFORE and SKIP_BEFORE[hit] == nxt) or (hit in SKIP_INFL and w != hit):
                continue
            entry = checked[hit]
            if hit in NOUN_WORDS:
                prev = lows[idx - 1] if idx > 0 else ""
                verb_use = (w.endswith(("ed", "ing")) or idx == 0 or prev in (
                    "to", "and", "then", "must", "can", "you", "not", "always",
                    "never", "also", "please", "should", "will", "or", "but"))
                if not verb_use:
                    continue
            if entry["number"] and not (nxt[:1].isdigit() or re.search(r"\b" + hit + r"\s+\d", low)):
                continue
            seen.add(hit)
            sev = "info" if entry["soft"] else "error"
            add("1.1", sev, f'"{raw}" is not approved -> {plain(entry["alt"])}', raw)

        if w in HAVE and idx + 1 < len(lows):
            j = idx + 1
            if lows[j] in ("not", "never", "already", "just", "also", "now") and j + 1 < len(lows):
                j += 1
            if is_participle(lows[j], L) and lows[j] not in ("need",):
                add("3.2", "error", "Perfect tense. Use the simple past or BE + adjective.",
                    f"{raw} {words[j][0]}")
        if w in BE and idx + 1 < len(lows):
            j = idx + 1
            while j < len(lows) and (lows[j] in ("not", "never", "also", "now", "then", "always",
                                                 "only", "still", "currently", "automatically")
                                     or lows[j].endswith("ly")) and j - idx < 3:
                j += 1
            if j < len(lows):
                t = lows[j]
                if t.endswith("ing") and len(t) > 4 and t not in ING_OK and t not in ctx.term_words:
                    add("3.4", "error", "Progressive tense. Use the simple present or past.",
                        f"{raw} {words[j][0]}")
                elif is_participle(t, L) and t not in STATE_ADJ and t not in ctx.term_words:
                    by = bool(re.search(r" by (?!means of)", low[words[j][1]:]))
                    add("3.6", "error" if (procedure or by) else "warning",
                        "Possible passive voice. Use the active voice"
                        + (" (the agent is given with 'by')." if by else
                           ". (Correct if the participle is an adjective of state, "
                           "or if the agent is unknown in a description.)"),
                        f"{raw} {words[j][0]}")
        if w.endswith("ing") and len(w) > 4 and w not in ING_OK and w not in ctx.term_words \
                and "-" not in w and not (idx > 0 and lows[idx - 1] in BE):
            add("3.5", "info" if idx > 0 and lows[idx - 1] in ("the", "a", "an") else "warning",
                'The "-ing" form is permitted only as a technical noun or in one. '
                'Rewrite (for example "before removing" -> "before you remove").', raw)

    if procedure and kind == "step" and words:
        first = lows[0]
        if first in ("you", "the", "user", "users", "operator", "it", "we", "please", "then", "next", "now", "once") \
                and not re.match(r"^(if|when|before|after|to|while|until)\b", low):
            if first in ("you", "we", "please") or re.search(r"\b(must|should|can|will|needs?)\b", low):
                add("5.3", "warning", "Write the instruction as a command (imperative).", words[0][0])
        cmds = re.findall(r"(?:,|\band\b|\bthen\b|\.)\s+(?:then\s+)?(\w+)\b", low)
        extra = [c for c in cmds if c in IMPERATIVE]
        if extra and lows[0] in IMPERATIVE | {"if", "when", "before", "after", "to"}:
            if re.search(r"\b(and|then)\s+(?:then\s+)?(" + "|".join(map(re.escape, extra)) + r")\b", low):
                add("5.2", "warning",
                    "Possibly more than one instruction in the sentence. Use one sentence for each "
                    "instruction, unless the actions occur at the same time.", ", ".join(extra))
        if re.match(r"^(if|when|before|after|while|until|to)\b[^,]{8,}$", low) and len(lows) > 6:
            add("5.4", "info", "If the sentence starts with a condition or purpose, put a comma before the command.")

    if kind == "note" and words and lows[0] in IMPERATIVE | {"do", "never", "always", "make"}:
        add("5.5", "warning", "A note gives information only. Make this instruction a step.", words[0][0])
    if kind == "safety" and words:
        if re.match(L["regex_bad_safety_starts"], low):
            add("7.2", "warning", "Start the safety instruction with a clear command or condition.", words[0][0])
    if re.match(r"^this\s+(is|are|can|will|must|does|has|removes|shows|makes|lets|causes|prevents|occurs|means)\b", low):
        add("GR-4", "info", 'Make sure that the reader knows what "this" refers to. If not, add the noun.', "This")
    if re.search(L["regex_inclusive_terms"], low):
        add("GR-7", "info", "Use gender-neutral language.")


def check_text(raw, mode, ctx):
    out, seq = [], 0
    blocks = parse_blocks(raw)
    for i, b in enumerate(blocks):
        text = mask(b.text)
        sents = split_sentences(text)
        if b.kind == "para" and len(sents) > 6:
            out.append({"line": b.line, "seq": 0, "rule": "6.6", "severity": "error",
                        "message": f"Paragraph has {len(sents)} sentences. The maximum is 6.",
                        "match": "", "sentence": sents[0]})
        if b.kind == "safety":
            nxt = blocks[i + 1].kind if i + 1 < len(blocks) else None
            if nxt not in ("step", "safety", "note", "bullet", "para"):
                out.append({"line": b.line, "seq": 0, "rule": "CONV", "severity": "info",
                            "message": "Convention, not an STE rule: put this safety instruction before the step it applies to.",
                            "match": "", "sentence": sents[0] if sents else ""})
        for s in sents:
            seq += 1
            check_sentence(s, b.line, b.kind, mode, ctx, out, seq)
    out.extend(synonym_findings(blocks, ctx))
    out.sort(key=lambda f: (f["line"], f.get("seq", 0)))
    return out


def synonym_findings(blocks, ctx):
    """Rule 1.11: a term and one of its synonyms ("also called") in the same document."""
    out = []
    if not ctx.synonyms:
        return out
    texts = [(b.line, mask(b.text).lower()) for b in blocks]
    for e in ctx.synonyms:
        term_rx = re.compile(r"\b" + re.escape(e["lower"]) + r"\b")
        t_line = next((ln for ln, t in texts if term_rx.search(t)), None)
        if t_line is None:
            continue
        for syn in e["synonyms"]:
            s_rx = re.compile(r"\b" + re.escape(syn.lower()) + r"\b")
            for ln, t in texts:
                if s_rx.search(t):
                    out.append({"line": ln, "seq": 0, "rule": "1.11", "severity": "warning",
                                "message": f'"{syn}" and "{e["term"]}" both occur. Use one name for one thing: "{e["term"]}" (rule 1.11).',
                                "match": syn, "sentence": syn})
                    break
    return out


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError as e:
        fail(f"Cannot read {path}: {e.strerror}. Give the path of a text or Markdown file. "
             "Convert .docx or .pdf to text first.")
    if "\x00" in raw[:2000]:
        fail(f"{path} is not a text file. Convert it to text or Markdown first.")
    return raw


def after_arrow_lower(msg):
    """Pattern messages suggest in capitals in the data; the output is in normal case."""
    if "->" in msg:
        head, tail = msg.split("->", 1)
        return head + "-> " + tail.strip().lower()
    return msg


RULE_TOPIC = {
    "1.1": "Unapproved word or phrase",
    "1.11": "Two names for one thing (synonyms)",
    "1.3": "Restricted meaning (wear, see, above, turn)",
    "1.14": "Spelling (American English)",
    "3.2": "Verb tense (perfect)", "3.4": "Complex verb construction / modal verb",
    "3.5": "-ing form", "3.6": "Passive voice", "4.1": "Vague wording",
    "4.2": "Contraction",
    "5.1": "Procedure sentence longer than 20 words",
    "5.2": "More than one instruction in a sentence", "5.3": "Instruction not a command",
    "5.4": "Comma after condition", "5.5": "Instruction in a note",
    "6.3": "Descriptive sentence longer than 25 words", "6.6": "Paragraph longer than 6 sentences",
    "7.1": "Signal word (WARNING or CAUTION)", "7.2": "Start of safety instruction",
    "GR-1": 'Missing "that"', "GR-4": '"This" without a noun', "GR-6": "Latin abbreviation",
    "GR-7": "Inclusive language", "CONV": "Position of safety instruction (convention, not a rule)",
    "8.1": "Semicolon", "9.3": "Phrasal verb",
}
NOT_CHECKED = ("Not checked by this script: multi-word nouns (2.1), wrong meaning or part of "
               "speech (1.2, 1.3), missing articles (4.5), term consistency (1.11, partly), "
               "one topic per paragraph (6.5). Read the text for these.")


def build_checked(ctx):
    """Words the checker reports as not approved: the bundled entries with the check flag.
    The local word list never adds a finding (most of its entries are for one part of speech,
    and the text does not show the part of speech). It removes a bundled finding only when
    the list approves the word as the same part of speech (local precedence, rule 1.2)."""
    POS = {"verb": "v", "adjective": "adj"}
    checked = {}
    for w, e in ctx.g["unapproved"].items():
        if not e["check"]:
            continue
        local_pos = ctx.local["approved"].get(w)
        if local_pos and (e["pos"] is None or POS.get(e["pos"]) in local_pos):
            continue
        checked[w] = e
    return checked


def ln(line):
    return "source" if line == 0 else str(line)


UNIT_WORDS = {"minute": "min", "minutes": "min", "hour": "h", "hours": "h", "second": "s",
              "seconds": "s", "litre": "l", "litres": "l", "liter": "l", "liters": "l",
              "meter": "m", "meters": "m", "metre": "m", "metres": "m", "volt": "v", "volts": "v",
              "bar": "bar", "bars": "bar", "psi": "psi"}
UNIT_ABBR = {"mm", "cm", "m", "km", "ft", "kg", "g", "mg", "lb", "lbs", "oz", "psi", "bar", "kpa",
             "mpa", "pa", "nm", "v", "mv", "kv", "ma", "kw", "w", "hz", "khz", "mhz", "ghz", "rpm",
             "ms", "min", "h", "hr", "l", "ml", "gb", "mb", "kb", "tb", "%", "sec", "deg", "c", "f"}
SPELLED = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
           "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
NUM_RX = re.compile(r"(?<![\w.,/-])(\d+(?:[.,]\d+)?|one|two|three|four|five|six|seven|eight|nine|ten)"
                    r"\s?(°\s?[CFK]|%|[A-Za-zµ]{1,9}(?:/[A-Za-z]{1,4})?)(?![\w/])", re.IGNORECASE)
PART_RX = re.compile(r"\b(?=[A-Z0-9/-]*\d)(?=[A-Z0-9/-]*[A-Z])[A-Z0-9][A-Z0-9/-]{3,}\b"
                     r"|\b\d{3,}-(?=[A-Z0-9-]*[A-Z])[A-Z0-9-]+\b")


def norm_unit(u):
    key = u.replace("°", "").replace(" ", "").lower()
    if key in UNIT_WORDS:
        return UNIT_WORDS[key]
    if key in UNIT_ABBR:
        return key.replace("°", "")
    return None


def value_keys(text):
    """(key, display, line) for each number with a unit and each part number in the text.
    Formatting differences are tolerated: 70 °C = 70 C; 4.50 L = 4.5 L; two hours = 2 h."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in NUM_RX.finditer(line):
            unit = norm_unit(m.group(2))
            if unit is None:
                continue
            num = m.group(1).lower()
            num = SPELLED.get(num, num)
            if re.fullmatch(r"\d{1,3}(,\d{3})+", num):
                num = num.replace(",", "")
            else:
                num = num.replace(",", ".")
            key = f"{float(num):g} {unit}"
            out.append((key, m.group(0).strip(), n))
        for m in PART_RX.finditer(line):
            part = m.group(0)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", part):
                continue
            out.append(("part " + part.replace("-", "").replace("/", ""), part, n))
    return out


def source_findings(raw, src_raw):
    """Source comparison items (code SRC, not an STE rule): values or part numbers in the file
    that the source does not give, and values in the source that the file does not give.
    They are printed in their own block and are not findings of the rule table."""
    mine, theirs = value_keys(raw), value_keys(src_raw)
    mine_keys = {k for k, _, _ in mine}
    their_keys = {k for k, _, _ in theirs}
    out = []
    for key, disp, line in mine:
        if key not in their_keys:
            out.append({"line": line, "seq": 0, "rule": "SRC", "severity": "info",
                        "message": f'"{disp}" is not in the source file. Check the value, or put it in the open questions.',
                        "match": disp, "sentence": disp})
    seen = set()
    for key, disp, line in theirs:
        if key not in mine_keys and key not in seen:
            seen.add(key)
            out.append({"line": 0, "seq": 0, "rule": "SRC", "severity": "info",
                        "message": f'The source has "{disp}" (source line {line}). The file does not. Keep it or ask.',
                        "match": disp, "sentence": f"source line {line}: {disp}"})
    return out


def cmd_check(args):
    ctx = Context(args.domain, args.terms, args.file, required=False, use_local=not args.no_local_dictionary)
    ctx.checked = build_checked(ctx)
    raw = read_text(args.file)
    findings = check_text(raw, args.type, ctx)
    if args.source:
        findings += source_findings(raw, read_text(args.source))
        findings.sort(key=lambda f: (f["line"], f.get("seq", 0)))
    if args.json:
        by_sev = Counter(f["severity"] for f in findings)
        json.dump({"file": args.file, "summary": {"total": len(findings), **by_sev},
                   "by_rule": dict(Counter(f["rule"] for f in findings)), "domains": ctx.domains,
                   "project_terms": ctx.project_path, "findings": findings}, sys.stdout, indent=2)
        print()
    else:
        print(f"STE check: {args.file}")
        if ctx.domains or ctx.project_path:
            print(f"Terms: {ctx.layers_text()}")
        print_check(findings, args.file, ctx, args.examples, args.all)
        print("\n" + NOT_CHECKED)
    if args.strict and any(f["severity"] == "error" for f in findings):
        sys.exit(1)
    return 0


# --------------------------------------------------------------------------
# fix (safe automatic replacements only)
# --------------------------------------------------------------------------

def apply_case(orig, repl):
    if len(orig) > 1 and orig.isupper():
        return repl.upper()
    if orig[:1].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


def fix_rules(ctx):
    """Yield (regex, replacement function, label). Only entries flagged auto."""
    g = ctx.g
    for ph in g["phrases"] + g["phrasal"]:
        if ph["auto"]:
            repl = ph["alt"].lower()
            yield (re.compile(ph["rx"].pattern, re.IGNORECASE), repl, "phrase")
    for p in g["patterns"]:
        if p["auto"] and p["repl"]:
            yield (p["fix_rx"], p["repl"], "pattern")
    for word, c in g["contractions"].items():
        if c["auto"]:
            yield (re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE), c["expansion"], "contraction")
    for word, e in g["unapproved"].items():
        if e["auto"]:
            alt = e["alt"].split(";")[0].split(" (")[0].strip().lower()
            yield (re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE), alt, "word")
    for en, am in g["british"].items():
        yield (re.compile(r"\b" + re.escape(en) + r"\b", re.IGNORECASE), am, "spelling")
    for j in ctx.jargon:
        if j["auto"]:
            yield (re.compile(r"\b" + re.escape(j["jargon"]) + r"\b", re.IGNORECASE), j["preferred"], "jargon")
    # synonyms: only from the project terms file (a pack's synonyms are reported, not replaced)
    for e in ctx.synonyms:
        if e["layer"] != "project terms file":
            continue
        for syn in e["synonyms"]:
            yield (re.compile(r"\b" + re.escape(syn) + r"\b", re.IGNORECASE), e["term"], "synonym")


def fix_result(raw, ctx):
    """Returns (new text, changes); changes are (line, old, new, label). Nothing is written."""
    rules = list(fix_rules(ctx))
    out_lines, changes = [], []
    for i, line, masked in prose_lines(raw):
        if masked is None or line.lstrip().startswith("#"):
            out_lines.append(line)
            continue
        cands = []
        low = masked.lower()
        term_spans = []
        for mt in ctx.multi:
            for m in re.finditer(r"\b" + r"\s+".join(map(re.escape, mt.split())) + r"\b", low):
                term_spans.append((m.start(), m.end()))
        for rx, repl, label in rules:
            for m in rx.finditer(masked):
                s, e = m.span()
                txt = line[s:e]
                if txt.lower() in ctx.terms or any(a < e and s < b for a, b in term_spans):
                    continue
                cands.append((s, e, apply_case(txt, repl), label))
        cands.sort(key=lambda c: (c[0], -(c[1] - c[0])))
        res, pos = [], 0
        for s, e, new, label in cands:
            if s < pos:
                continue
            res.append(line[pos:s])
            res.append(new)
            changes.append((i, line[s:e], new, label))
            pos = e
        res.append(line[pos:])
        out_lines.append("".join(res))
    new_raw = "\n".join(out_lines) + ("\n" if raw.endswith("\n") else "")
    return new_raw, changes


def cmd_fix(args):
    ctx = Context(args.domain, args.terms, args.file, required=True, use_local=False)
    raw = read_text(args.file)
    new_raw, changes = fix_result(raw, ctx)
    if not changes:
        print(f"No automatic replacements in {args.file}.")
        return 0
    if args.write:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(new_raw)
        print(f"{len(changes)} replacements written to {args.file}. Review the result with a diff and run check.")
    else:
        diff = difflib.unified_diff(raw.splitlines(keepends=True), new_raw.splitlines(keepends=True),
                                    fromfile=args.file, tofile=args.file + " (proposed)")
        sys.stdout.writelines(diff)
        print(f"\n{len(changes)} replacements proposed. Nothing was changed; run again with --write to apply.")
    for i, old, new, label in changes:
        print(f"  line {i}: {old} -> {new} ({label})", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# count (rules 5.1, 6.3, 2.1): the same counting rules as the checker
# --------------------------------------------------------------------------

def cmd_count(args):
    """One line per text: count, the limits, a preview. Every argument is one text;
    --from FILE reads one text per line. Pass all the texts in one call."""
    texts = list(args.text)
    for path in args.from_file or []:
        texts += [ln.strip() for ln in read_text(path).splitlines() if ln.strip()]
    if not texts:
        fail("give one or more texts, or --from FILE")
    for t in texts:
        n = count_words(mask(t))
        preview = t if len(t) <= 60 else t[:57] + "..."
        print(f"{n} words (procedure max 20, description max 25): {preview}")
    return 0


# --------------------------------------------------------------------------
# terms add
# --------------------------------------------------------------------------

def parse_entry(entry):
    """'term | TN or TV | category | std or ext; note', or a shorter form. Defaults: TN, -, ext."""
    f = [p.strip() for p in entry.split(" | ")]
    if not f[0]:
        raise DataError("empty term")
    typ = f[1].upper() if len(f) > 1 and f[1] else "TN"
    cat = f[2] if len(f) > 2 and f[2] else "-"
    note = " | ".join(f[3:]) if len(f) > 3 and f[3] else "ext"
    if typ not in ("TN", "TV"):
        raise DataError("the second field must be TN or TV")
    return f[0], typ, cat, note


def entries_from_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise DataError(f"cannot read {path}: {e.strerror}")
    return [s.strip() for s in lines if s.strip() and not s.strip().startswith("#")]


def cmd_terms_add(args):
    path = args.file or os.path.join(os.getcwd(), PROJECT_FILE)
    exists = os.path.isfile(path)
    if not exists and not args.create:
        fail(f"{path} does not exist. Ask the author before creating it. "
             "Then run again with --create.")
    entries = list(args.entries)
    for src in args.from_file or []:
        entries += entries_from_file(src)
    if not entries:
        fail("no entries: give terms, or --from FILE (one entry per line; a bare term is enough)")
    existing = set()
    if exists:
        loaded, _ = load_project(path)
        existing = {(e["lower"], e["type"].upper()) for e in loaded}
    new, refused = [], []
    for entry in entries:
        try:
            term, typ, cat, note = parse_entry(entry)
        except DataError as e:
            refused.append(f"{entry!r}: {e}")
            continue
        key = (term.lower(), typ)
        if key in existing:
            refused.append(f"{entry!r}: already in {path}")
            continue
        existing.add(key)
        new.append(f"{term} | {typ} | {cat} | {note}")
    if new:
        with open(path, "a" if exists else "w", encoding="utf-8") as fh:
            if not exists:
                fh.write("# Project terms: subject-field words for this document set.\n"
                         "# Format: term | TN or TV | category | std or ext; note\n")
            elif open(path, encoding="utf-8").read()[-1:] not in ("\n", ""):
                fh.write("\n")
            fh.write("\n".join(new) + "\n")
    print(f"{len(new)} entries added to {path}.")
    for r in refused:
        print(f"refused: {r}", file=sys.stderr)
    return 1 if refused else 0


# --------------------------------------------------------------------------
# import-dictionary: a local word list from the user's own copy of the standard
# --------------------------------------------------------------------------

DICT_START = re.compile(r"Dictionary Page 2-1-A1")
DICT_HEADER = re.compile(r"^(ASD-STE100 Simplified|Word Approved meaning|\(part of speech\)|"
                         r"Issue \d+ Part \d|\d{4}-\d{2}-\d{2}\s*$|=+\s*PAGE)")
DICT_POS = ("art", "adj", "adv", "conj", "n", "pron", "prep", "v", "TN", "TV")
DICT_TAG = re.compile(r"\((\w+)\)[,.;:]?")
SENTENCE_END = ".,:;?!"
LOCAL_HEADER = ("# Word list generated locally by 'ste.py import-dictionary' from the user's own copy of\n"
                "# ASD-STE100. This file is NOT part of the skill or the repository. Do not copy it into a\n"
                "# repository, and do not redistribute it.\n"
                "# Columns: word | part of speech | approved (yes or no) | alternatives (not approved only)\n")
PDF_HELP = ("Cannot read this PDF. Install pypdf (pip install pypdf), or run\n"
            "  pdftotext -layout FILE.pdf FILE.txt\n"
            "and pass FILE.txt. The -layout option keeps the columns the parser needs.")


def read_source(path):
    if not os.path.isfile(path):
        fail(f"{path} does not exist.")
    with open(path, "rb") as fh:
        head = fh.read(5)
    if not (path.lower().endswith(".pdf") or head == b"%PDF-"):
        return read_text(path)
    try:
        import pypdf  # optional
    except ImportError:
        pypdf = None
    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(path)
            pages = []
            for page in reader.pages:
                try:
                    pages.append(page.extract_text(extraction_mode="layout") or "")
                except TypeError:
                    pages.append(page.extract_text() or "")
            return "\n".join(pages)
        except Exception as e:  # pypdf raises many types on damaged files
            fail(f"pypdf could not read {path} ({e.__class__.__name__}). {PDF_HELP}")
    exe = shutil.which("pdftotext")
    if exe:
        r = subprocess.run([exe, "-layout", path, "-"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
        fail(f"pdftotext could not read {path}. {PDF_HELP}")
    fail(PDF_HELP)


def dict_tag(tok):
    m = DICT_TAG.fullmatch(tok)
    return m.group(1) if m and m.group(1) in DICT_POS else None


def dict_case(tok):
    letters = re.sub(r"[^A-Za-z]", "", tok)
    if not letters:
        return None
    if letters.isupper():
        return "U"
    if letters.islower():
        return "L"
    return "M"


def parse_dictionary(text):
    """Headwords with part of speech from the dictionary pages. Returns
    {(word, pos): {"approved": bool, "alts": [words]}}. Definitions and examples are not kept.
    Approved headwords are capitals at the start of a line; not-approved headwords are lower case;
    alternatives are capitals after a headword, with their part of speech in brackets."""
    text = text.replace("\f", "\n")
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if DICT_START.search(ln)), None)
    if start is None:
        print("import-dictionary: the dictionary start (Dictionary Page 2-1-A1) was not found; "
              "the whole text was read, so check the counts.", file=sys.stderr)
        start = 0
    toks = []
    for ln in lines[start:]:
        s = ln.strip()
        if not s or DICT_HEADER.match(s):
            continue
        col0 = not ln[:1].isspace()
        for k, t in enumerate(ln.split()):
            toks.append((t, col0 and k == 0))
    entries, cur = {}, None
    for k, (t, col0) in enumerate(toks):
        pos = dict_tag(t)
        if not pos:
            continue
        run, j, want = [], k - 1, None
        while j >= 0:
            tj = toks[j][0]
            if dict_tag(tj) or (("(" in tj or ")" in tj)) or tj.rstrip("”’\"') ")[-1:] in SENTENCE_END:
                break
            c = dict_case(tj)
            if c is None or c == "M":
                break
            if want is None:
                want = c
            if c != want:
                break
            run.insert(0, toks[j])
            j -= 1
        if not run:
            continue
        word = " ".join(x[0] for x in run).lower().strip(",")
        if want == "L":
            cur = (word, pos)
            entries.setdefault(cur, {"approved": False, "alts": []})
        elif want == "U":
            if run[0][1]:
                cur = (word, pos)
                entries.setdefault(cur, {"approved": True, "alts": []})
            elif cur is not None and not entries[cur]["approved"]:
                if word not in entries[cur]["alts"] and word != cur[0]:
                    entries[cur]["alts"].append(word)
    return entries


def write_local(path, entries):
    rows = []
    for (word, pos) in sorted(entries):
        e = entries[(word, pos)]
        if e["approved"]:
            rows.append(f"{word} | {pos} | yes | -")
        else:
            rows.append(f"{word} | {pos} | no | {'; '.join(e['alts']) if e['alts'] else '-'}")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(LOCAL_HEADER + "\n".join(rows) + "\n")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def repo_root():
    d = SKILL_DIR
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def inside(path, folder):
    p, f = os.path.realpath(path), os.path.realpath(folder)
    return p == f or p.startswith(f + os.sep)


def cmd_import_dictionary(args):
    out = args.out or default_local_path()[0]
    out = os.path.expanduser(out)
    if inside(out, SKILL_DIR):
        fail("refusing to write inside the skill folder. Use --out with a path outside it.")
    root = repo_root()
    if root and inside(out, root):
        fail("refusing to write inside the repository. Use the default location (~/.config/ste100) "
             "or --out with a path outside it.")
    entries = parse_dictionary(read_source(args.source))
    if not entries:
        fail(f"no dictionary entries found in {args.source}. Give the dictionary pages (they contain "
             "'Dictionary Page 2-1-A1' or the entries that follow it), or a plain-text extraction of them.")
    approved = sum(1 for e in entries.values() if e["approved"])
    not_approved = len(entries) - approved
    write_local(out, entries)
    print(f"{approved} approved, {not_approved} not approved. Written to {out}.")
    print("The file is your copy of the standard, in words only: keep it on this machine.")
    for label, got, want in (("approved", approved, OFFICIAL_APPROVED),
                             ("not approved", not_approved, OFFICIAL_NOT_APPROVED)):
        if abs(got - want) > 0.15 * want:
            print(f"Warning: {label} count {got} is far from the official {want}. The extraction may be "
                  "incomplete or the layout may differ; check the output file before you rely on it.",
                  file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# review: one call for the first pass
# --------------------------------------------------------------------------

def print_source(findings):
    """The source comparison block: after the rule findings, never in the rule table."""
    src = [f for f in findings if f["rule"] == "SRC"]
    if not src:
        return
    print(f"\nSource comparison ({len(src)} items; not rule findings, see SKILL.md):")
    for f in src:
        where = f"line {f['line']}" if f["line"] else "source"
        print(f"  {where}: {f['message']}")


def print_check(findings, file_name, ctx, examples, show_all):
    """Rule findings in the rule table, then the source comparison block (code SRC)."""
    print_rule_findings([f for f in findings if f["rule"] != "SRC"], file_name, ctx, examples, show_all)
    print_source(findings)


def print_rule_findings(findings, file_name, ctx, examples, show_all):
    by_sev = Counter(f["severity"] for f in findings)
    by_rule = Counter(f["rule"] for f in findings)
    print(f"{len(findings)} findings: {by_sev.get('error', 0)} error, "
          f"{by_sev.get('warning', 0)} warning, {by_sev.get('info', 0)} info")
    if not findings:
        return
    if show_all:
        print("\nBy rule:")
        for r, c in sorted(by_rule.items(), key=lambda x: -x[1]):
            print(f"  {r:<5} {RULE_TOPIC.get(r, ''):<45} {c}")
        last = None
        for f in findings:
            if (f["line"], f["sentence"]) != last:
                where = f"line {f['line']}" if f["line"] else "source"
                print(f"\n{where}: {f['sentence'][:160]}")
                last = (f["line"], f["sentence"])
            hit = f" [{f['match']}]" if f["match"] else ""
            print(f"    {f['severity']:<7} {f['rule']:<5}{hit} {f['message']}")
        return
    groups = {}
    for f in findings:
        groups.setdefault(f["rule"], []).append(f)
    print()
    print(f"{'Rule':<6}{'Findings':<10}{'Topic':<46}Lines")
    for r, fs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines = sorted({f["line"] for f in fs})
        print(f"{r:<6}{len(fs):<10}{RULE_TOPIC.get(r, ''):<46}{', '.join(ln(x) for x in lines)}")
    for r, fs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print(f"\n{r} {RULE_TOPIC.get(r, '')} ({len(fs)})")
        for f in fs[:examples]:
            sent = f["sentence"] if len(f["sentence"]) <= 90 else f["sentence"][:87] + "..."
            where = "" if f["line"] == 0 else f"line {f['line']} "
            print(f"  {where}[{f['severity']}] \"{sent}\" -- {f['message']}")
        if len(fs) > examples:
            print(f"  +{len(fs) - examples} more, use --all")


def cmd_review(args):
    ctx = Context(args.domain, args.terms, args.file, required=False, use_local=not args.no_local_dictionary)
    ctx.checked = build_checked(ctx)
    raw = read_text(args.file)
    res = scan_result(raw, ctx)
    new_raw, changes = fix_result(raw, ctx)
    findings = check_text(raw, args.type, ctx)
    if args.source:
        findings += source_findings(raw, read_text(args.source))
        findings.sort(key=lambda f: (f["line"], f.get("seq", 0)))
    s = res["summary"]
    print(f"STE review: {args.file}")
    print(f"Layers: {ctx.layers_text()}")
    print(f"\nUnknown words: {s['unknown_distinct']} ({s['unknown_occurrences']} occurrences). "
          "Decide each one. Accepted terms: the candidates file (--candidates) holds them; delete the lines "
          "that are not terms, then pass the file with --terms.")
    for w, v in res["unknown"][:40]:
        print(f"  line {v['line']:<5} {w} ({res['unknown_count'].get(w, 0)})")
    if len(res["unknown"]) > 40:
        print(f"  +{len(res['unknown']) - 40} more; see the candidates file")
    if args.candidates:
        n = write_candidates(args.candidates, res["unknown"])
        print(f"  {n} candidates written to {args.candidates}.")
    print(f"\nSafe fixes proposed: {len(changes)}. fix FILE shows the diff; fix FILE --write applies them.")
    for i, old, new, label in changes[:30]:
        print(f"  line {i}: {old} -> {new}")
    if len(changes) > 30:
        print(f"  +{len(changes) - 30} more")
    print(f"\nCheck: {args.file}")
    print_check(findings, args.file, ctx, args.examples, args.all)
    print("\n" + NOT_CHECKED)
    return 0


# --------------------------------------------------------------------------
# lookup
# --------------------------------------------------------------------------

def cmd_lookup(args):
    ctx = Context(args.domain, args.terms, None, required=True, use_local=not args.no_local_dictionary)
    results = [lookup_word(ctx, w) for w in args.words]
    if args.json:
        json.dump({"layers": ctx.layers_text(), "results": results}, sys.stdout, indent=2)
        print()
    else:
        for r in results:
            print(f"{r['word']}: {r['status']}")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(prog="ste.py", description="ASD-STE100 helper (stdlib only).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, doc=True, local=True):
        p.add_argument("--domain", action="append", default=[],
                       help="term pack to load (repeatable): software, mechanical")
        p.add_argument("--terms", metavar="FILE", help="project terms file (default: ste-terms.txt)")
        if local:
            p.add_argument("--no-local-dictionary", action="store_true",
                           help="ignore the local word list made by import-dictionary")
        if doc:
            p.add_argument("file")

    def check_opts(p):
        p.add_argument("--type", choices=["auto", "procedure", "description"], default="auto")
        p.add_argument("--examples", type=int, default=3, help="examples per rule (default 3)")
        p.add_argument("--source", metavar="SRC",
                       help="the source text (notes): report values and part numbers that differ")

    p = sub.add_parser("review", help="first pass in one call: scan, safe fixes, check")
    common(p)
    check_opts(p)
    p.add_argument("--all", action="store_true", help="print every finding")
    p.add_argument("--candidates", metavar="OUT", help="write the unknown words as a terms file")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("lookup", help="status of words")
    common(p, doc=False)
    p.add_argument("--json", action="store_true")
    p.add_argument("words", nargs="+")
    p.set_defaults(func=cmd_lookup)

    p = sub.add_parser("scan", help="words no layer knows")
    common(p)
    p.add_argument("--json", action="store_true")
    p.add_argument("--candidates", metavar="OUT", help="write the unknown words as a terms file")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("check", help="checker")
    common(p)
    check_opts(p)
    p.add_argument("--all", action="store_true", help="print every finding")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="exit 1 if there is an error finding")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("fix", help="safe automatic replacements (diff; --write applies)")
    common(p, local=False)
    p.add_argument("--write", action="store_true")
    p.set_defaults(func=cmd_fix)

    p = sub.add_parser("count", help="STE word count of phrases or sentences (one line each)")
    p.add_argument("--from", dest="from_file", action="append", metavar="FILE",
                   help="one text per line (repeatable)")
    p.add_argument("text", nargs="*", help="each argument is one text")
    p.set_defaults(func=cmd_count)

    p = sub.add_parser("terms", help="project terms file")
    tsub = p.add_subparsers(dest="action", required=True)
    ta = tsub.add_parser("add", help="add entries (many in one call, or --from FILE)")
    ta.add_argument("--file", help="default: ste-terms.txt in the working directory")
    ta.add_argument("--create", action="store_true", help="create the file if it does not exist")
    ta.add_argument("--from", dest="from_file", action="append", metavar="FILE",
                    help="a file with one entry per line (repeatable)")
    ta.add_argument("entries", nargs="*",
                    help="'term | TN or TV | category | std or ext; note', or a bare term")
    ta.set_defaults(func=cmd_terms_add)

    p = sub.add_parser("import-dictionary", help="local word list from your own copy of the standard")
    p.add_argument("source", help="your PDF, or a .txt made with: pdftotext -layout FILE.pdf FILE.txt")
    p.add_argument("--out", metavar="PATH",
                   help="output file (default: ~/.config/ste100/dictionary.txt, or $XDG_CONFIG_HOME)")
    p.set_defaults(func=cmd_import_dictionary)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        rc = args.func(args)
    except DataError as e:
        fail(str(e), 1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
