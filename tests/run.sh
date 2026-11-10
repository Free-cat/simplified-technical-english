#!/bin/sh
# Smoke tests for the checker and the skill metadata. Run from the repository root.
set -eu
CHECK="python3 skills/ste100/scripts/ste_check.py"

# 1. Text that is not STE must give errors (exit code 1 with --strict).
for f in examples/check-runbook/source.md examples/edit-guide/source.md; do
  if $CHECK "$f" --strict >/dev/null; then
    echo "FAIL: no errors found in $f"; exit 1
  fi
done

# 2. Text in STE must give no errors.
for f in examples/edit-guide/result.md examples/write-procedure/result.md; do
  $CHECK "$f" --strict >/dev/null || { echo "FAIL: errors found in $f"; exit 1; }
done

# 3. JSON output must be valid JSON.
$CHECK examples/check-runbook/source.md --json | python3 -c "import json,sys; json.load(sys.stdin)"

# 4. A file that does not exist must give a clear message, not a traceback.
if $CHECK no-such-file.md 2>/dev/null; then echo "FAIL: missing file accepted"; exit 1; fi

# 5. Agent Skills specification (agentskills.io/specification) and version sync.
python3 - <<'PY'
import json, os, re
d = "skills/ste100"
s = open(d + "/SKILL.md", encoding="utf-8").read()
m = re.match(r"---\n(.*?)\n---\n", s, re.S)
assert m, "no frontmatter"
fm = m.group(1)
get = lambda k: re.search(rf"^{k}: (.+)$", fm, re.M).group(1).strip()
name, desc, compat = get("name"), get("description"), get("compatibility")
assert name == os.path.basename(d), "name must be the same as the folder name"
assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64, name
assert 0 < len(desc) <= 1024, f"description has {len(desc)} characters"
assert "<" not in desc and ">" not in desc, "no XML tags in the description"
assert 0 < len(compat) <= 500, f"compatibility has {len(compat)} characters"
assert len(s.splitlines()) < 500, "SKILL.md must have fewer than 500 lines"
# Each file that SKILL.md refers to must exist.
for ref in set(re.findall(r"\b((?:references|scripts)/[\w.-]+)", s)):
    assert os.path.exists(os.path.join(d, ref)), f"missing file: {ref}"
# References are one level deep: a reference file must not point to another one.
for f in os.listdir(d + "/references"):
    t = open(f"{d}/references/{f}", encoding="utf-8").read()
    assert not re.search(r"\]\((?!https?://)[^)]+\.md\)", t), f"nested reference in {f}"
# The version is the same in all places.
ver = re.search(r'^  version: "(.+)"$', fm, re.M).group(1)
mk = json.load(open(".claude-plugin/marketplace.json"))
assert mk["metadata"]["version"] == ver, "marketplace.json version differs"
assert f"## {ver}" in open("CHANGELOG.md").read(), "CHANGELOG.md has no entry for this version"
PY
echo "All tests passed."
