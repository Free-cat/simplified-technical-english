# Changelog

## 0.2.0

The reference files were compared with the official ASD-STE100 Issue 9 text and
corrected. The rule summaries and examples are still our own words. The word
list is still a partial, working subset.

- Smaller context for the agent: `SKILL.md` has a trigger table that says which
  reference to open for each condition. Check and Edit read `rules-summary.md` (one
  line per rule); the other files are read on demand. The always-read text keeps the
  critical numbers (20 and 25 words, one word, passive only when the agent is unknown,
  three words for a multi-word noun, approved verb first for technical verbs).
- `references/` is split: `rules-summary.md`, `rules-details.md`, `term-overview.md`,
  `term-details.md`, `software-text.md`, and `dictionary.md`. `rules.md` and
  `technical-names.md` are removed.
- Word data is in text files in `assets/words/` (one entry per line). `dictionary.md`
  and the two-status table are generated from them (`tests/build_references.py`).
- One entry point, `scripts/ste.py`, with `lookup`, `scan`, `check`, `fix`, and
  `terms add`. `scripts/ste_check.py` is a wrapper with the same output.
- Term packs for software and IT operations (`assets/terms/software.txt`, 392 entries)
  and mechanical equipment and maintenance (`assets/terms/mechanical.txt`, 398 entries).
  `--domain` loads a pack; a term in a pack is not reported as unapproved. A pack note
  that says the general sense is not approved gives an info finding.
- Project terms file `ste-terms.txt` (created only with the author's agreement). It
  overrides the packs and the general lists.
- Checker output is compact by default: findings grouped by rule, with all line
  numbers and up to three examples per rule (`--examples N`). `--all` prints everything.
- New rule 1.11 check: a term and its synonym ("also called") in one document.
- `fix` makes only the safe replacements flagged `auto`, as a diff by default.
- Tests for each subcommand, the wrapper, the fix rules, the data formats, and the
  README counts.

- Technical nouns and verbs: 22 technical noun categories and 4 technical verb
  categories (was 20 and 3). `technical-names.md` has a scope, examples, and the
  usual error for each category, a decision procedure, a table of general words
  that look technical, a table of words with two statuses, and a format for the
  term list. The examples are our own, not the standard's lists.
- Rule 2.1 limits a multi-word noun to three words (nouns and adjectives count),
  not three nouns.
- Passive voice is permitted in a description only when the agent is unknown.
- Notes have the 25-word limit. Safety instructions have the 20-word limit.
- Notes must not give instructions or requirements, or set limits. A note may
  state a result.
- Gerund (*-ing*) headings are allowed as technical nouns, for example
  "Troubleshooting".
- GR items are recommendations, not rules. GR-6 lists the Latin abbreviations
  only. *Via* and *vs.* are unapproved words, listed in the dictionary.
- The position of a warning before its step is a convention of technical
  publication standards, not an STE rule. The skill and the checker label it so.
- WARNING is for a risk of injury or death, CAUTION for a risk of damage to
  objects. The skill reads loss of data as damage. That is its own reading.
- Word list: removed wrong "not approved" entries (*wait, try, receive,
  activate, deactivate, flush, although, adjacent, defective, mandatory*, and
  *torque* as a verb). Corrected wrong alternatives: *swap* → INTERCHANGE,
  *nearly* → ALMOST, *vital* → MANDATORY, *inoperative* → OFF. Words that are not
  approved in the dictionary are not approved only by being missing from the list.
- Checker: suggests no NOW for *currently* and *at this point*; no longer warns
  about approved PUT ON; reports the safety-instruction position as a convention
  (code CONV), not as rule 7.1.
- Examples: corrected the few clear violations in the result files (for example
  WEAR for eye protection, FAIL, and TRIGGER).
- Fewer script calls per job: `review FILE` gives the scan, the safe fixes (count and
  list) and the check findings in one call. A typical job takes 3 to 5 script calls
  (SKILL.md says so).
- Terms in one step: `terms add` takes many entries in one call, bare terms (defaults
  TN, category -, ext), and `--from FILE`. `scan --candidates OUT` (and `review
  --candidates OUT`) writes the unknown words as a terms file; delete the lines that are
  not terms and pass it with `--terms OUT`.
- Author view: SKILL.md says that a term in a domain pack is settled and is never shown
  to the author; Check reports never describe how they were made; open questions are
  about meaning only.
- Every finding has a code: an STE rule number, a GR number (general recommendations, not
  rules), or CONV (a convention). GR items in `rules-summary.md` and `software-text.md` name
  the nearest rule as a "related rule", and say "interpretation" where the bullet is this
  skill's own reading. Each report row cites a rule or a GR number (SKILL.md).
- Suggestions are in normal case (`utilize -> use`). Capitals remain in the data files
  and in `dictionary.md`.
- Restricted meanings (rules 1.3 and 9.2): warnings for *wear* with clothing or
  protection (put on), *see* with Table, Figure, Section, step, or page (refer to),
  *above*, *over*, *below*, and *under* with a number (more than, less than), and *turn*
  with a color (the color changes to). They are in `patterns.txt`. They do not fire on
  the correct result files.
- `should` suggests MUST first (then the imperative, then IF for "should" = "if").
- `check --source SRC` (and `review --source SRC`): information findings for a value with
  a unit or a part number that the file and the source do not share. Formatting
  differences are tolerated (70 °C and 70 C; 4.50 L and 4.5 L; two hours and 2 hours).
  The items are printed in a separate "Source comparison" block with the code SRC;
  they are not rule findings.
- `count TEXT` prints the STE word count of a phrase or sentence, with the rules that
  the checker uses. A noun-cluster heuristic (rule 2.1) was tried and not added: it
  fired on the correct example texts and on verbs, so it is too noisy.
- Safe replacements: `employ`, `properly`, `nearby`, `tiny`, `due to`, and `owing to`
  are no longer flagged `auto`. They remain normal findings.
- `import-dictionary SOURCE` builds a local word list from the user's own copy of the
  standard (their PDF, read with pypdf or `pdftotext -layout`, or a `.txt` made from it).
  It writes `~/.config/ste100/dictionary.txt` (or `$XDG_CONFIG_HOME`, or `--out`, which
  may not be inside the skill folder or the repository). The file stores only the word,
  its part of speech, approved yes or no, and the alternative words. It has no
  definitions or examples. `lookup`, `scan`, `check`, and `review` use it when it exists
  (`--no-local-dictionary` ignores it; `STE100_DICTIONARY` points elsewhere). `lookup`
  and `scan` use it: a word that the list does not approve as the text's part of speech
  is listed as unknown, with the note, so that the author decides (most of these are
  nouns the list does not cover). `check` never reports from the list; it drops a bundled
  finding only when the list approves the word as the same part of speech. Reporting
  every not-approved entry as an error gave false positives such as "housing" for
  "contain". The repository does not contain the official dictionary, and the command
  only reads the user's copy on the user's machine. The tests use a synthetic fixture.
- Rule 1.2: `check`, `test`, `work`, `damage`, `leak`, `aid`, and `function` used as verbs
  anywhere in a sentence are errors (after a comma, "to", a modal, "and/then/or", a pronoun
  subject, or at the start). The patterns are in `patterns.txt` (`verbuse`); the word list
  comes from `part-of-speech.txt`. Noun uses ("do a check", "check valve", "leak test") stay silent.
- `count` takes many texts in one call (one line each) and `--from FILE`.


## 0.1.0

- First public version.
- Skill `ste100`: write, check, and edit workflows for ASD-STE100 Issue 9.
- Rule summary (53 rules), working word list, software documentation section.
- `ste_check.py` checker.
- Three test cases and three worked examples.
