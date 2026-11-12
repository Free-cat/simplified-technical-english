#!/bin/sh
# Tests for the skill, its data, and its documents. Run from the repository root: sh tests/run.sh
set -eu
STE="python3 skills/ste100/scripts/ste.py"
CHECK="python3 skills/ste100/scripts/ste_check.py"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

fail() { echo "FAIL: $1"; exit 1; }

# Isolate the tests from the user's own local word list: an empty file is loaded as no entries.
: > "$TMP/empty-dictionary.txt"
export STE100_DICTIONARY="$TMP/empty-dictionary.txt"

# 1. Text that is not STE must give errors (exit code 1 with --strict).
for f in examples/check-runbook/source.md examples/edit-guide/source.md; do
  if $CHECK "$f" --strict >/dev/null; then fail "no errors found in $f"; fi
done

# 2. Text in STE must give no errors.
for f in examples/edit-guide/result.md examples/write-procedure/result.md; do
  $CHECK "$f" --strict >/dev/null || fail "errors found in $f"
done

# 3. JSON output must be valid JSON, from the wrapper and from ste.py.
$CHECK examples/check-runbook/source.md --json | python3 -c "import json,sys; json.load(sys.stdin)"
$STE check examples/check-runbook/source.md --json | python3 -c "import json,sys; json.load(sys.stdin)"

# 4. A file that does not exist must give a clear message, not a traceback.
if $CHECK no-such-file.md 2>/dev/null; then fail "missing file accepted"; fi

# 5. Wrapper equivalence: ste_check.py FILE and ste.py check FILE give the same output.
for f in examples/check-runbook/source.md examples/edit-guide/source.md; do
  $CHECK "$f" > "$TMP/a.txt"; $STE check "$f" > "$TMP/b.txt"
  cmp -s "$TMP/a.txt" "$TMP/b.txt" || fail "wrapper output differs for $f"
  $CHECK "$f" --json > "$TMP/a.json"; $STE check "$f" --json > "$TMP/b.json"
  cmp -s "$TMP/a.json" "$TMP/b.json" || fail "wrapper JSON differs for $f"
done

# 6. Compact output: grouped by rule, a count, the line numbers, and "use --all".
$STE check examples/check-runbook/source.md > "$TMP/compact.txt"
grep -q "^Rule " "$TMP/compact.txt" || fail "compact output has no rule table"
grep -q "^1.1 Unapproved word or phrase (" "$TMP/compact.txt" || fail "compact output has no 1.1 group"
grep -q "use --all" "$TMP/compact.txt" || fail "compact output does not say use --all"
$STE check examples/check-runbook/source.md --all > "$TMP/all.txt"
grep -q "^By rule:" "$TMP/all.txt" || fail "--all output changed"
$STE check examples/check-runbook/source.md --examples 1 | grep -q "+[0-9]* more, use --all" \
  || fail "--examples 1 does not limit the examples"

# 7. lookup: a known unapproved word, a pack term with --domain, an unknown word (exit 0),
#    an unknown domain (clear error).
$STE lookup verify | grep -q "not approved -> make sure" || fail "lookup of an unapproved word"
$STE lookup --domain software load | grep -q "technical" || fail "lookup of a pack term"
$STE lookup pump | grep -q "not in the word lists" || fail "lookup of an unknown word"
if $STE lookup --domain nope x 2>/dev/null; then fail "unknown domain accepted"; fi

# 8. lookup with a missing data file: clear message and non-zero exit.
cp -R skills/ste100 "$TMP/skill"
rm "$TMP/skill/assets/words/unapproved.txt"
if python3 "$TMP/skill/scripts/ste.py" lookup verify >/dev/null 2>"$TMP/err.txt"; then
  fail "missing data file accepted"
fi
grep -q "cannot read the data file" "$TMP/err.txt" || fail "missing data file: no clear message"

# 9. scan: lists unknown words with a summary line.
$STE scan --domain software examples/check-runbook/source.md > "$TMP/scan.txt"
grep -q "unknown words" "$TMP/scan.txt" || fail "scan has no summary"
grep -q "unapproved words found" "$TMP/scan.txt" || fail "scan has no unapproved count"

# 10. fix: a dry run changes nothing; --write changes only auto items, and leaves code,
#     quoted text, bold labels and headings alone; a word that depends on meaning stays.
cat > "$TMP/doc.md" <<'EOF'
# Don't panic

1. Don't touch the `prod` config. Utilize the console.
2. Check the colour of the light; in order to restart, prior to that, see "Utilize".
3. Press **Start**.
EOF
cp "$TMP/doc.md" "$TMP/doc.orig"
$STE fix "$TMP/doc.md" > "$TMP/fix-dry.txt"
cmp -s "$TMP/doc.md" "$TMP/doc.orig" || fail "fix without --write changed the file"
grep -q "^+1. Do not touch" "$TMP/fix-dry.txt" || fail "fix dry run shows no diff"
$STE fix "$TMP/doc.md" --write >/dev/null 2>&1
grep -q "^# Don't panic" "$TMP/doc.md" || fail "fix changed a heading"
grep -q '`prod`' "$TMP/doc.md" || fail "fix changed a code span"
grep -q 'see "Utilize"' "$TMP/doc.md" || fail "fix changed quoted text"
grep -q "\*\*Start\*\*" "$TMP/doc.md" || fail "fix changed a bold UI label"
grep -q "Do not touch" "$TMP/doc.md" || fail "fix did not replace a contraction"
grep -q "Use the console" "$TMP/doc.md" || fail "fix did not replace an auto word"
grep -q "color" "$TMP/doc.md" || fail "fix did not replace British spelling"
grep -q "Check the color" "$TMP/doc.md" || fail "fix changed a meaning-dependent word"

# 11. terms add: refuses to create the file without --create, adds entries with --create,
#     refuses duplicates.
cd "$TMP"
if python3 "$OLDPWD/skills/ste100/scripts/ste.py" terms add "release tag | TN | 19 | ext" >/dev/null 2>&1; then
  fail "terms add created a file without --create"
fi
python3 "$OLDPWD/skills/ste100/scripts/ste.py" terms add --create "release tag | TN | 19 | ext" >/dev/null
[ "$(grep -c '^release tag | TN' ste-terms.txt)" = "1" ] || fail "terms add did not write the entry"
if python3 "$OLDPWD/skills/ste100/scripts/ste.py" terms add "release tag | TN | 19 | ext" >/dev/null 2>&1; then
  fail "terms add accepted a duplicate"
fi
cd "$OLDPWD"

# 12. Project terms file: a term in it is known to scan and check (no unapproved finding).
printf 'release tag | TN | 19 | ext\n' > "$TMP/ste-terms.txt"
printf 'Push the release tag button.\n' > "$TMP/one.md"
$STE scan --terms "$TMP/ste-terms.txt" "$TMP/one.md" | grep -q "project terms file" || fail "project terms not used"

# 13. Documents: the existing examples and eval inputs keep their results; the file tree,
#     references, generated tables, README counts, and versions are consistent.
python3 tests/check_data.py

# 14. review: one call gives the unknown words, the safe fixes and the findings.
$STE review examples/check-runbook/source.md > "$TMP/review.txt"
grep -q "^Unknown words:" "$TMP/review.txt" || fail "review has no unknown words section"
grep -q "^Safe fixes proposed:" "$TMP/review.txt" || fail "review has no fixes section"
grep -q "^Check: " "$TMP/review.txt" || fail "review has no check section"

# 15. count: the STE word count of a phrase, with the same rules as the checker.
$STE count "Wear eye protection." | grep -q "^3 words" || fail "count of a short sentence"
$STE count "Check the pump (see Table 2) and record 70 °C." | grep -q "^7 words" \
  || fail "count does not treat parentheses and numbers as one word"

# 16. Candidates: scan writes a terms file; after deleting the non-terms, check accepts it.
printf 'The flarb valve is open. Check the flarb valve.\n' > "$TMP/cand.md"
$STE scan --candidates "$TMP/cand.txt" "$TMP/cand.md" >/dev/null
grep -q "^flarb | TN | - | ext" "$TMP/cand.txt" || fail "candidates file has no entry for flarb"
grep -q "^# Candidate" "$TMP/cand.txt" || fail "candidates file has no header"
if $STE scan --terms "$TMP/cand.txt" "$TMP/cand.md" | grep -q "flarb ("; then fail "candidates file not used"; fi
$STE check --terms "$TMP/cand.txt" "$TMP/cand.md" | grep -q "findings" || fail "check with candidates file"

# 17. terms add: many entries in one call, bare terms, --from FILE, duplicates refused.
cd "$TMP"
printf 'gasket\nseal | TV | 2c | ext\n' > "$TMP/terms-in.txt"
python3 "$OLDPWD/skills/ste100/scripts/ste.py" terms add --file "$TMP/many.txt" --create \
  "release tag" "widget | TV | 2c" "checkout | TN | 19 | ext" --from "$TMP/terms-in.txt" >/dev/null
[ "$(grep -v '^#' "$TMP/many.txt" | grep -c ' | ')" = "5" ] || fail "terms add did not add 5 entries"
grep -q "^release tag | TN | - | ext" "$TMP/many.txt" || fail "bare term not given defaults"
grep -q "^widget | TV | 2c | ext" "$TMP/many.txt" || fail "two-field entry not given defaults"
if python3 "$OLDPWD/skills/ste100/scripts/ste.py" terms add --file "$TMP/many.txt" "gasket" >/dev/null 2>&1; then
  fail "terms add accepted a duplicate bare term"
fi
cd "$OLDPWD"

# 18. Restricted meanings (rule 1.3): the checker warns, with a suggestion in normal case.
printf 'Wear eye protection.\nSee Table 2.\nThe valve turns green.\nRaise the pressure above 20 psi.\n' > "$TMP/restricted.md"
$STE check "$TMP/restricted.md" --all > "$TMP/restricted.txt"
[ "$(grep -c 'warning 1.3' "$TMP/restricted.txt")" = "4" ] || fail "restricted-meaning patterns did not fire"
grep -q "put on" "$TMP/restricted.txt" || fail "wear suggestion missing"
grep -q "refer to" "$TMP/restricted.txt" || fail "see suggestion missing"
grep -q "the color changes to" "$TMP/restricted.txt" || fail "turn suggestion missing"
grep -q "more than" "$TMP/restricted.txt" || fail "above suggestion missing"
for f in examples/edit-guide/result.md examples/write-procedure/result.md; do
  $STE check "$f" --all | grep -q "warning 1.3" && fail "1.3 pattern fires on correct text in $f"
done

# 19. Suggestions are in normal case, and "should" offers MUST first.
$STE lookup utilize | grep -q "not approved -> use$" || fail "lookup suggestion is not in normal case"
$STE lookup should | grep -q "not approved -> must (for an obligation" || fail "should does not suggest MUST first"
printf 'You should check the pump.\n' > "$TMP/should.md"
$STE check "$TMP/should.md" --all | grep -q '"should" is not approved -> must' || fail "check suggestion for should"

# 20. Rule numbers: no finding is reported under a code that is not an STE rule.
printf 'This is it. Ensure the pump is set.\n' > "$TMP/codes.md"
$STE check "$TMP/codes.md" --all > "$TMP/codes.txt"
printf 'WARNING: HOT PARTS CAN BURN.\n\n## Next steps\n' > "$TMP/convention.md"
$STE check "$TMP/convention.md" --all >> "$TMP/codes.txt"
python3 - "$TMP/codes.txt" <<'PYEOF' || fail "a finding row has a code that is not N.N, GR-N or CONV"
import re, sys
codes = [m.group(2) for m in (re.match(r"^ +(error|warning|info) +(\S+)", ln) for ln in open(sys.argv[1]))
         if m]
allowed = re.compile(r"^(\d\.\d+|GR-\d+|CONV)$")
bad = [c for c in codes if not allowed.match(c)]
sys.exit(1 if bad or not codes else 0)
PYEOF
grep -Eq "^ +info +GR-4 " "$TMP/codes.txt" || fail "the GR-4 finding is not coded GR-4"
grep -Eq "^ +info +CONV " "$TMP/codes.txt" || fail "the convention finding is not coded CONV"

# 21. Safe replacements: employ, properly, nearby, tiny, due to and owing to are not automatic.
printf 'Employ the tool properly, nearby, tiny. Due to heat, owing to wear.\n' > "$TMP/manual.md"
$STE fix "$TMP/manual.md" | grep -q "No automatic replacements" || fail "a word that is no longer auto was fixed"

# 22. Source accuracy: a value that matches in another format is not reported; a dropped
#     value and an added value are reported (info, rule 4.2).
printf 'Heat the seal to 70 °C for approx 4.5 L of oil. Part AB-1234 is needed.\n' > "$TMP/source.md"
printf 'Heat the seal to 70 C for 4.5 L of oil. Use part AB-1234. Wait 3 hours.\n' > "$TMP/doc.src.md"
$STE check "$TMP/doc.src.md" --source "$TMP/source.md" --all > "$TMP/src.txt"
grep -q '"3 hours" is not in the source' "$TMP/src.txt" || fail "a value added to the file was not reported"
if grep -q '70 C" is not in the source' "$TMP/src.txt"; then fail "70 C reported although the source has 70 °C"; fi
# Source items are a separate block, never rows of the rule table.
grep -q "^Source comparison (" "$TMP/src.txt" || fail "no source comparison block"
if grep -E "^ +(info|warning|error) +SRC" "$TMP/src.txt"; then fail "a source item is coded as a finding"; fi
if grep -q '4.5 L" is not in the source' "$TMP/src.txt"; then fail "4.5 L reported as different"; fi
$STE check "$TMP/source.md" --source "$TMP/doc.src.md" --all | grep -q 'source has "3 hours"' \
  || fail "a value dropped from the file was not reported"

# 23. Local word list: import-dictionary reads a synthetic fixture and writes outside the skill.
unset STE100_DICTIONARY
export XDG_CONFIG_HOME="$TMP/cfg"
$STE import-dictionary tests/fixtures/dictionary-sample.txt > "$TMP/import.txt" 2>"$TMP/import-err.txt"
grep -q "3 approved, 3 not approved" "$TMP/import.txt" || fail "import-dictionary summary"
grep -q "far from the official" "$TMP/import-err.txt" || fail "import-dictionary gives no count warning"
LOCAL="$TMP/cfg/ste100/dictionary.txt"
[ -f "$LOCAL" ] || fail "import-dictionary did not write to XDG_CONFIG_HOME"
grep -q "^shift | v | yes | -" "$LOCAL" || fail "approved entry not written"
grep -q "^flonk | v | no | shift" "$LOCAL" || fail "not-approved entry without its alternative"
grep -q "Do not copy" "$LOCAL" || fail "local file has no do-not-redistribute header"
if $STE import-dictionary tests/fixtures/dictionary-sample.txt --out skills/ste100/local-test.txt >/dev/null 2>&1; then
  fail "import-dictionary wrote inside the skill folder"
fi
[ ! -e skills/ste100/local-test.txt ] || fail "file created inside the skill folder"
: > "$TMP/no-entries.txt"
if $STE import-dictionary "$TMP/no-entries.txt" --out "$TMP/x.txt" >/dev/null 2>&1; then
  fail "import-dictionary accepted a source with no entries"
fi
printf '%%PDF-1.4 damaged\n' > "$TMP/damaged.pdf"
if $STE import-dictionary "$TMP/damaged.pdf" --out "$TMP/x.txt" >/dev/null 2>"$TMP/pdf-err.txt"; then
  fail "a damaged PDF was accepted"
fi
grep -q "Traceback" "$TMP/pdf-err.txt" && fail "damaged PDF gives a traceback"
# The local list is used by lookup, and is ignored with --no-local-dictionary.
STE100_DICTIONARY="$LOCAL" $STE lookup flonk | grep -q "not approved (v) in the local word list -> shift" \
  || fail "lookup does not use the local word list"
STE100_DICTIONARY="$LOCAL" $STE lookup --no-local-dictionary flonk | grep -q "not in the word lists" \
  || fail "--no-local-dictionary is not honoured"
printf 'Shifts shifts.\n' > "$TMP/local.md"
STE100_DICTIONARY="$LOCAL" $STE scan "$TMP/local.md" | grep -q "No unknown words" \
  || fail "scan does not know an inflected approved word from the local list"
# A word that the local list does not approve as the text's part of speech is listed by scan
# as unknown (with the note), and the checker does not report it (its part of speech is unknown).
printf 'Flonk the gauge.\n' > "$TMP/flonk.md"
STE100_DICTIONARY="$LOCAL" $STE scan "$TMP/flonk.md" | grep -q "flonk (1) -- not approved (v) in the local word list -> shift" \
  || fail "scan does not list a not-approved word from the local list as unknown"
if STE100_DICTIONARY="$LOCAL" $STE check "$TMP/flonk.md" --all | grep -q '"Flonk" is not approved'; then
  fail "check reports a word from the local list"
fi
# A bundled finding is dropped when the local list approves the word as the same part of speech.
printf 'Check the valve.\n' > "$TMP/check-verb.md"
STE100_DICTIONARY="$LOCAL" $STE check "$TMP/check-verb.md" --all | grep -q "1.1" \
  || fail "a bundled verb finding for check was dropped although the list approves check as a noun only"
unset XDG_CONFIG_HOME
export STE100_DICTIONARY="$TMP/empty-dictionary.txt"

# 24. Noun-only words as verbs (rule 1.2): an error anywhere in a sentence; noun uses stay silent.
printf 'Check the level.\nTest the pump.\nBefore you start, check the fluid.\nWhen the light comes on, test the pump.\nTo check the seal, open the cover.\nDo not test the pump.\nYou check the level.\nMust check the level first.\nCheck the valve, and then test the pump.\nCheck that the cover is closed.\n' > "$TMP/verbs.md"
[ "$($STE check "$TMP/verbs.md" --all | grep -c "error   1.2")" = "11" ] || fail "noun-only words used as verbs: expected 11 errors (rule 1.2)"
printf 'Do a check of the seal.\nUse a check valve.\nRun the CI checks.\nDo a leak test.\nInstall the test rig.\nThe test rig is ready.\nDo a functional test of the pump.\nDo work on the pump.\nSee the leak test results.\n' > "$TMP/nouns.md"
[ "$($STE check "$TMP/nouns.md" --all | grep -c "error   1.2")" = "0" ] || fail "noun uses of check, test or work reported as verbs"
# The examples with correct text stay silent for rule 1.2.
for f in examples/edit-guide/result.md examples/write-procedure/result.md; do
  $STE check "$f" --all | grep -q "error   1.2" && fail "rule 1.2 fires on correct text in $f"
done

# 25. count: many texts in one call, one line each; --from reads one text per line.
printf 'Check the pump.\nOpen the cover.\n' > "$TMP/texts.txt"
[ "$($STE count "Wear eye protection." "Open the cover." --from "$TMP/texts.txt" | wc -l | tr -d ' ')" = "4" ] \
  || fail "count does not print one line per text"
$STE count "Open the cover and remove the four bolts from the lower housing." | grep -q "^12 words" \
  || fail "count of a 12-word sentence"
if $STE count >/dev/null 2>&1; then fail "count without a text is accepted"; fi

# 26. check prints the word count of each over-length sentence, so count is rarely needed.
printf '1. Open the cover, remove the four bolts from the lower housing, lift the cover away from the pump carefully and then wait.\n' > "$TMP/long.md"
$STE check "$TMP/long.md" --all | grep -q "Sentence has 2[0-9] words" || fail "no word count in the over-length finding"

echo "All tests passed."
