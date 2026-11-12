#!/usr/bin/env python3
"""Format and consistency checks for the skill's data and documents. Called by tests/run.sh.

Checks: every data file has the right number of fields; term packs have 4 fields, TN/TV,
at most three words, and no duplicate (term, TN/TV); the counts stated in README match the
files; every file that SKILL.md names exists; reference files are one level deep and long
ones have a contents list; generated references are up to date; SKILL.md version matches.
Standard library only. Exits 1 on the first failure group, printing each problem.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "ste100")
WORDS = os.path.join(SKILL, "assets", "words")
TERMS = os.path.join(SKILL, "assets", "terms")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

problems = []


def bad(msg):
    problems.append(msg)


def rows(path, count=None):
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f.read().splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [p.strip() for p in s.split(" | ")]
            if count and len(parts) != count:
                bad(f"{os.path.relpath(path, ROOT)} line {n}: {len(parts)} fields, expected {count}")
            out.append((n, parts))
    return out


def check_words_files():
    spec = {"unapproved.txt": 7, "approved-verbs.txt": 1, "part-of-speech.txt": 4,
            "two-statuses.txt": 3, "modals.txt": 2, "phrases.txt": 6, "patterns.txt": 6,
            "british.txt": 2, "contractions.txt": 3, "jargon.txt": 4, "function-words.txt": 1}
    for name, n in spec.items():
        rows(os.path.join(WORDS, name), n)
    for n, parts in rows(os.path.join(WORDS, "unapproved.txt")):
        if parts[1] not in ("verbs", "connecting", "adjectives"):
            bad(f"unapproved.txt line {n}: unknown section {parts[1]}")
    for n, parts in rows(os.path.join(WORDS, "phrases.txt"), 6):
        if parts[1] not in ("fixed", "phrasal"):
            bad(f"phrases.txt line {n}: kind must be fixed or phrasal")
        if parts[3] not in ("error", "warning", "info"):
            bad(f"phrases.txt line {n}: severity must be error, warning or info")
    for n, parts in rows(os.path.join(WORDS, "patterns.txt"), 6):
        try:
            re.compile(parts[0])
        except re.error as e:
            bad(f"patterns.txt line {n}: bad regular expression: {e}")
    # no word in both the core approved list and the unapproved list
    approved = {p[0].lower() for _, p in rows(os.path.join(WORDS, "approved-verbs.txt"))}
    unapproved = {p[0].lower() for _, p in rows(os.path.join(WORDS, "unapproved.txt"))
                  if p[2] != "adjective"}  # close (adjective) is a different sense
    for w in sorted(approved & unapproved):
        bad(f"'{w}' is both an approved verb and an unapproved word")
    # checker-lists keys
    keys = {line.split(":")[0].strip() for line in open(os.path.join(WORDS, "checker-lists.txt"), encoding="utf-8")
            if line.strip() and not line.startswith("#")}
    for k in ["noun_words", "skip_before", "be_forms", "have_forms", "irregular_participles",
              "state_adjectives", "not_participles", "approved_ing", "imperative_hints",
              "regex_bad_safety_starts", "regex_inclusive_terms"]:
        if k not in keys:
            bad(f"checker-lists.txt: missing key {k}")


def check_packs():
    counts = {}
    for name in sorted(os.listdir(TERMS)):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(TERMS, name)
        seen = set()
        tn = tv = 0
        for n, parts in rows(path):
            if len(parts) != 4:
                bad(f"{name} line {n}: expected 4 fields (term | TN or TV | category | std or ext; note)")
                continue
            term, typ, cat, note = parts
            if typ not in ("TN", "TV"):
                bad(f"{name} line {n}: second field must be TN or TV, got {typ}")
            if len(term.split()) > 3:
                bad(f"{name} line {n}: '{term}' has more than three words (rule 2.1)")
            if not re.match(r"(std|ext)\b", note):
                bad(f"{name} line {n}: note must start with std or ext")
            key = (term.lower(), typ)
            if key in seen:
                bad(f"{name} line {n}: duplicate {typ} entry '{term}'")
            seen.add(key)
            tn += typ == "TN"
            tv += typ == "TV"
        counts[name[:-4]] = (len(seen), tn, tv)
    return counts


def check_readme(pack_counts):
    text = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    import ste  # noqa: E402  (scripts/ste.py, same folder as the data)
    general = len(ste.load_general()["unapproved"])
    approved = len(ste.load_general()["approved"])
    expected = [
        f"{general} not-approved entries",
        f"{approved} core approved verbs",
    ]
    for name, (total, tn, tv) in sorted(pack_counts.items()):
        expected.append(f"{total} entries ({tn} TN, {tv} TV)")
    for s in expected:
        if s not in text:
            bad(f"README.md does not state the current count: '{s}'")


def check_skill_refs():
    s = open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", s, re.S)
    if not m:
        bad("SKILL.md: no frontmatter")
        return
    fm = m.group(1)
    ver = re.search(r'^  version: "(.+)"$', fm, re.M).group(1)
    for ref in sorted(set(re.findall(r"\b((?:references|scripts|assets)/[\w./-]+)", s))):
        if not os.path.exists(os.path.join(SKILL, ref.rstrip("."))):
            bad(f"SKILL.md names a missing file: {ref}")
    if len(s.splitlines()) > 250:
        bad(f"SKILL.md has {len(s.splitlines())} lines; the target is 250")
    rd = os.path.join(SKILL, "references")
    for f in sorted(os.listdir(rd)):
        t = open(os.path.join(rd, f), encoding="utf-8").read()
        if re.search(r"\]\((?!https?://)[^)]+\.md[)#]", t):
            bad(f"references/{f} links to another .md file (references must stay one level deep)")
        if len(t.splitlines()) > 100 and "## Contents" not in "\n".join(t.splitlines()[:15]):
            bad(f"references/{f} has more than 100 lines and no contents list at the top")
    mk = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    if mk["metadata"]["version"] != ver:
        bad("marketplace.json version differs from SKILL.md")
    if f"## {ver}" not in open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read():
        bad("CHANGELOG.md has no entry for this version")


def check_generated():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "build_references.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        bad("generated references are out of date: " + r.stdout.strip())


CODE_RX = r"\d\.\d+|GR-\d+|CONV"


def check_rule_numbers():
    """Every finding code in the data is an STE rule (N.N), a general recommendation (GR-N),
    or CONV (a convention of this skill, not a rule)."""
    for n, parts in rows(os.path.join(WORDS, "patterns.txt"), 6):
        if not re.fullmatch(CODE_RX, parts[1]):
            bad(f"patterns.txt line {n}: code '{parts[1]}' is not N.N, GR-N or CONV")
    for n, parts in rows(os.path.join(WORDS, "phrases.txt"), 6):
        if not re.fullmatch(CODE_RX, parts[2]):
            bad(f"phrases.txt line {n}: code '{parts[2]}' is not N.N, GR-N or CONV")
    # the safe-replacement list: these words change meaning or part of speech, so no auto flag
    for n, parts in rows(os.path.join(WORDS, "unapproved.txt"), 7):
        if parts[0] in ("employ", "properly", "nearby", "tiny") and "auto" in parts[4]:
            bad(f"unapproved.txt line {n}: '{parts[0]}' must not have the auto flag")
    for n, parts in rows(os.path.join(WORDS, "phrases.txt"), 6):
        if parts[0] in ("due to", "owing to") and "auto" in parts[5]:
            bad(f"phrases.txt line {n}: '{parts[0]}' must not have the auto flag")
    # guidance: every bullet in software-text.md cites a rule; every GR item in the summary too
    sw = open(os.path.join(SKILL, "references", "software-text.md"), encoding="utf-8").read()
    for line in sw.splitlines():
        if line.startswith("- **") and not re.search(r"(?:Rules?|related rule) [0-9]\.[0-9]", line):
            bad(f"software-text.md has a bullet with no rule number: {line[:60]}")
    summ = open(os.path.join(SKILL, "references", "rules-summary.md"), encoding="utf-8").read()
    for line in summ.splitlines():
        if re.match(r"^- \*\*GR-\d\*\*", line) and not re.search(r"related rule [0-9]\.[0-9]", line):
            bad(f"rules-summary.md: GR item without a rule number: {line[:50]}")


def main():
    check_words_files()
    check_rule_numbers()
    pack_counts = check_packs()
    check_readme(pack_counts)
    check_skill_refs()
    check_generated()
    if problems:
        print("data and document checks FAILED:")
        for p in problems:
            print("  " + p)
        return 1
    print("data and document checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
