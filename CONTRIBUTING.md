# Contributing

Thank you for your help. Three types of change are most useful.

## 1. Corrections to the rules or the word list

Files: `skills/ste100/references/rules.md` and `skills/ste100/references/dictionary.md`.

- **Do not copy text from the ASD-STE100 specification or its dictionary.** The
  specification is copyrighted. Write the rule or the entry in your own words,
  and write your own example.
- Say how you know: the rule number, or a public source (the ASD website, a
  published article, a vendor guide).
- Keep entries short. The word list is a working subset of frequent cases, not a
  copy of the dictionary.

## 2. Checker fixes

File: `skills/ste100/scripts/ste_check.py` (Python 3 standard library only; do
not add dependencies).

- For a false finding or a missed violation, give the sentence, what the script
  reported, and what you expected.
- Run `sh tests/run.sh` before you open a pull request.

## 3. Changes to the skill instructions

File: `skills/ste100/SKILL.md`.

- Keep it short (under 500 lines). Put detail in `references/`.
- Explain why, not only what. The file is read by a language model.
- If the change affects the output, run the test cases in `evals/` with and
  without the change, and put the result in the pull request.

## Test cases

`evals/` has three cases in the layout that `claude plugin eval` reads. To run
them with that tool, copy `evals/` into `skills/ste100/` first. They are kept
outside the skill folder so that an install does not copy them.

## Format and validation

The skill follows the [Agent Skills specification](https://agentskills.io/specification):
the `name` in `SKILL.md` is the same as the folder name, the description has
1024 characters or fewer, `SKILL.md` has fewer than 500 lines, and reference
files are one level below `SKILL.md`. `tests/run.sh` checks these points. You can
also use the reference validator: `skills-ref validate skills/ste100`.

## Versions and commits

- The version is in three places: `metadata.version` in `SKILL.md`,
  `.claude-plugin/marketplace.json`, and `CHANGELOG.md`. Change all three together.
- Use [semantic versioning](https://semver.org): a change that can alter the
  output for the same input is at least a minor version.
- Use [Conventional Commits](https://www.conventionalcommits.org) for commit
  messages: `feat(skill): ...`, `fix(checker): ...`, `docs: ...`.

## Style

Write documentation in plain English. STE is welcome but not required here.
