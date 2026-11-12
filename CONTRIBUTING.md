# Contributing

Thank you for your help. Four types of change are most useful.

## 1. Corrections to the rules or the word lists

Files: `skills/ste100/references/rules-summary.md` and `rules-details.md` (rules),
`skills/ste100/assets/words/` (general words). `dictionary.md` and the two-status table
in `term-details.md` are generated: change the files in `assets/words/`, then run
`python3 tests/build_references.py`.

- **Do not copy text from the ASD-STE100 specification or its dictionary.** The
  specification is copyrighted. Write the rule or the entry in your own words, and
  write your own example.
- Check each claim against your own copy of the specification (the rule number, the
  dictionary entry, or the category). Do not paste the text of the specification into
  an issue, a pull request, or a commit message.
- Say how you know: the rule number, or a public source (the ASD website, a published
  article, a vendor guide).
- Keep entries short. The word list is a working subset of frequent cases.

### Word file formats

Each file has a header that lists its columns. Lines starting with `#` are comments.
Fields are separated by ` | ` (space, bar, space).

| File | Columns |
|---|---|
| `unapproved.txt` | word \| section \| pos \| alternative \| flags \| note \| example |
| `approved-verbs.txt` | one verb per line, lower case |
| `part-of-speech.txt` | word \| approved as \| not approved as \| write instead |
| `two-statuses.txt` | word \| general sense \| specific sense |
| `modals.txt` | word \| alternative |
| `phrases.txt` | phrase \| fixed or phrasal \| rule \| severity \| alternative \| flags |
| `patterns.txt` | regular expression \| rule \| severity \| message \| flags \| replacement |
| `british.txt` | British spelling \| American spelling |
| `contractions.txt` | contraction \| expansion \| flags |
| `jargon.txt` | jargon \| preferred term \| domain \| flags |
| `function-words.txt` | one word per line (common English words that `scan` does not list) |

`patterns.txt` and `phrases.txt` give each finding a code: an STE rule number (N.N), a general
recommendation (GR-N, for example GR-4; these are recommendations, not rules), or CONV (a
convention of this skill, not a rule). `tests/check_data.py` allows only these forms.

Flags: `check` (the checker reports the word), `soft` (report as info only), `auto`
(safe for `ste.py fix --write`: the alternative keeps the meaning and the part of speech
in the usual sentence), `number` (only when a number follows), `cs` (case-sensitive
pattern). Be conservative with `auto`: when in doubt, leave it out. Every `auto` entry
is listed in the pull request. A word that changes meaning or part of speech when it is
replaced (for example *employ*, *properly*, *due to*) is never `auto`.

## 2. New term pack (a subject field)

File: `skills/ste100/assets/terms/<domain>.txt`. Use the format of the existing packs:

```
term | TN or TV | category | std or ext; note
```

- `TN` or `TV`; the category is a rule 1.5 number (1–22) for nouns, or a verb
  category (1a–1f, 2a–2c, 3a–3f, 4) for verbs.
- `std` = the word is an example in the standard's own list for that category. `ext` =
  the word is added by the same principle. Be honest: most entries are `ext`.
- A note that starts with "general sense not approved" tells the checker to report an
  info finding with that note. Use it when the everyday sense of the word is not approved.
- "also called X" names a synonym (rule 1.11). The checker then reports a document that
  uses both names.
- One line per term. No duplicate (term, TN or TV) pairs. At most three words per term.
- Each entry is checked against your own copy of the standard. Describe in the pull
  request which rule and category you used, but do not paste the specification text.
- Add the term in the file, or in a list passed to `terms add --from`; do not add one
  command per term when you prepare a list.

The validation in `tests/check_data.py` checks the format, the duplicates, the word
count, and that the README counts match the files. The README "Coverage"
table has a row for each domain: add your row and its counts when you add a pack.

## 2a. The local word list (`import-dictionary`)

The command reads the user's own copy of the standard and writes a word list outside the
repository. Its parser is tested only with `tests/fixtures/dictionary-sample.txt`, which
contains invented words in the same layout. Do not add extracts of the official text, the
official word list, or the output of the command to the repository, to a fixture, or to an
issue. Changes to the parser must keep the fixture test passing and must not depend on a
real extraction.

## 3. Checker and lookup fixes

File: `skills/ste100/scripts/ste.py` (Python 3 standard library only; do not add
dependencies). `ste_check.py` is a wrapper; do not put logic in it.

- For a false finding or a missed violation, give the sentence, what the script
  reported, and what you expected.
- A change to the output format needs a note in the CHANGELOG and an update to the tests.
- Run `sh tests/run.sh` before you open a pull request.

## 4. Changes to the skill instructions

Files: `skills/ste100/SKILL.md` and the files in `references/`.

- Keep `SKILL.md` at about 250 lines. Put detail in `references/` (one level below
  `SKILL.md`; a reference file must not link to another `.md` file).
- Explain why, not only what. The file is read by a language model.
- If the change affects the output, run the test cases in `evals/` with and without the
  change, and put the result in the pull request.

## Test cases

`evals/` has three cases in the layout that `claude plugin eval` reads. To run them
with that tool, copy `evals/` into `skills/ste100/` first. They are kept outside the
skill folder so that an install does not copy them.

## Format and validation

The skill follows the [Agent Skills specification](https://agentskills.io/specification):
the `name` in `SKILL.md` is the same as the folder name, the description has 1024
characters or fewer, `SKILL.md` has fewer than 500 lines, and reference files are one
level below `SKILL.md`. `tests/run.sh` checks these points. You can also use the
reference validator: `skills-ref validate skills/ste100`.

## Versions and commits

- The version is in three places: `metadata.version` in `SKILL.md`,
  `.claude-plugin/marketplace.json`, and `CHANGELOG.md`. Change all three together.
- Use [semantic versioning](https://semver.org): a change that can alter the output for
  the same input is at least a minor version.
- Use [Conventional Commits](https://www.conventionalcommits.org) for commit messages:
  `feat(skill): ...`, `fix(checker): ...`, `docs: ...`.

## Style

Write documentation in plain English. STE is welcome but not required here.
