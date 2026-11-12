# Simplified Technical English skill (`ste100`)

[![test](https://github.com/Free-cat/simplified-technical-english/actions/workflows/test.yml/badge.svg)](https://github.com/Free-cat/simplified-technical-english/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-black.svg)](https://agentskills.io)

An agent skill that writes, checks, and edits technical documents by the rules of
ASD-STE100 Simplified Technical English (Issue 9).

Simplified Technical English (STE) is a controlled language. It has a small
vocabulary and strict sentence rules, so that a reader with limited English, or
a translator, can understand each sentence in only one way. It started in
aerospace maintenance. It also works for software runbooks, user guides, and
work instructions.

| Before | After |
|---|---|
| Prior to commencing the deployment, verify that all CI checks have passed and ensure the release tag is correct. | 1. Before you deploy, make sure that all CI checks have no errors.<br>2. Make sure that the release tag is correct. |
| The maintenance banner should be enabled by the operator via the admin console. | Set the maintenance banner to on in the admin console. |
| Having confirmed that the pressure selector is at minimum, press the green START button. | 1. Make sure that the pressure selector is at minimum.<br>2. Push the green START button. |

> **Unofficial project.** This skill is not affiliated with, endorsed by, or
> certified by ASD. It does not contain the text of the ASD-STE100 specification
> or its dictionary. See [Limits and disclaimer](#limits-and-disclaimer).

## Install

```bash
npx skills add Free-cat/simplified-technical-english
```

This uses the open [`skills`](https://github.com/vercel-labs/skills) CLI. It
finds the agents on your machine (Claude Code, Cursor, Codex, and others) and
copies the skill to the correct folder.

| To do this | Run |
|---|---|
| Install for all your projects | `npx skills add Free-cat/simplified-technical-english -g` |
| Install for one agent only | `npx skills add Free-cat/simplified-technical-english -a claude-code` |
| See what the repository contains | `npx skills add Free-cat/simplified-technical-english --list` |
| Get a newer version | `npx skills update ste100` |
| Remove the skill | `npx skills remove ste100` |

**Claude Code plugin marketplace:**

```
/plugin marketplace add Free-cat/simplified-technical-english
/plugin install ste100@simplified-technical-english
```

**Manual install:** copy the `skills/ste100` folder into the skills folder of
your agent (for Claude Code: `~/.claude/skills/` or `.claude/skills/` in a project).

The skill follows the open [Agent Skills](https://agentskills.io) format.

## What it does

| Job | You give | You get |
|---|---|---|
| **Write** | Notes, facts, or an outline | A new document in STE |
| **Check** | An existing document | A findings report: rule or GR number, original text, problem, corrected text |
| **Edit** | An existing document | The document in STE, and a summary of the changes |

Example requests:

- "Turn these shop-floor notes into a work instruction in Simplified Technical English."
- "Check `deploy-runbook.md` against the STE rules. Do not rewrite it, only give me a report."
- "Our customer requires ASD-STE100. Rewrite section 4 of this guide and tell me what you changed."

The [`examples/`](examples/) folder has one full input and output for each job.

## What is in the skill

```
skills/ste100/
├── SKILL.md                      # job selection, workflows, key rules, trigger table (always read)
├── references/
│   ├── rules-summary.md          # all 53 rules and 8 GR, one line each (read for Check and Edit)
│   ├── rules-details.md          # examples and reasons, by section (open for a rule in doubt)
│   ├── term-overview.md          # term decision procedure, category lines, term list format
│   ├── term-details.md           # category scope and examples, two-status table (open for a word in doubt)
│   ├── software-text.md          # software and IT guidance and typical conversions
│   └── dictionary.md             # generated word tables: alternatives, part-of-speech traps, core verbs
├── assets/
│   ├── words/                    # general word data as text: unapproved.txt, approved-verbs.txt,
│   │                             #   part-of-speech.txt, two-statuses.txt, modals.txt, phrases.txt,
│   │                             #   patterns.txt, british.txt, contractions.txt, jargon.txt,
│   │                             #   checker-lists.txt, function-words.txt
│   └── terms/                    # term packs: software.txt, mechanical.txt
└── scripts/
    ├── ste.py                    # one entry point: review, lookup, scan, check, fix, count, terms add, import-dictionary
    └── ste_check.py              # wrapper: the same as "ste.py check FILE"
tests/
├── run.sh                        # all tests (sh tests/run.sh)
├── check_data.py                 # data format, rule numbers, README counts, references, versions
├── build_references.py           # regenerates dictionary.md and the two-status table
└── fixtures/dictionary-sample.txt  # invented entries in the layout of the standard, for import-dictionary tests
```

## The scripts

The agent runs one script, `scripts/ste.py`, for the mechanical part of the work.
It has no dependencies (Python 3 standard library) and does not use the network.

| Command | What it does |
|---|---|
| `review` | First pass in one call: unknown words, safe fixes, and check findings |
| `check` | Findings by rule number, with line numbers |
| `fix` | Safe replacements only (contractions, fixed phrases, spelling). Shows a diff; `--write` applies it |
| `lookup`, `scan` | The status of a word; the words in a document that no word list knows |
| `count` | The STE word count of a sentence or a noun group |
| `terms add` | Adds terms to the project terms file, `ste-terms.txt` |

The checker is a first pass. It reports some correct text, and it cannot find
all errors. The skill tells the agent to examine each finding. The full
instructions for each command are in [`SKILL.md`](skills/ste100/SKILL.md).

You can also run the checker without an agent, for example in CI:

```bash
python3 skills/ste100/scripts/ste.py check --domain software docs/runbook.md
```

### Local official word list (optional, bring your own copy)

The repository does not contain the official ASD-STE100 dictionary. If you own a
copy, you can build a local word list from it once:

```bash
python3 skills/ste100/scripts/ste.py import-dictionary ~/Documents/ASD-STE100.pdf
```

The command reads your copy on your machine and writes one file in your config
folder (`~/.config/ste100/dictionary.txt`). The file keeps the word, its part of
speech, its status, and the alternative words. It keeps no definitions and no
examples. `lookup` and `scan` then use it. Do not share the file: it is your copy
of the word list of the standard. The command needs `pypdf` or `pdftotext` to
read a PDF, and it is tested only with a synthetic sample: check the counts that
it prints.

## Coverage

The word lists are a working subset. The official ASD-STE100 Issue 9 dictionary
has 875 approved and 1274 not-approved entries. The counts below come from the
files in `skills/ste100/assets/`, and `tests/run.sh` checks that they are current.

| Domain | Status | Entries in the skill |
|---|---|---|
| General word list (not-approved words and their alternatives, core approved verbs) | Partial subset. The full official word list: bring your own copy (`import-dictionary`, see above) | 230 not-approved entries; 134 core approved verbs (official: 1274 and 875) |
| Software and IT operations (`--domain software`) | Term pack | 392 entries (315 TN, 77 TV) |
| Mechanical equipment and maintenance (`--domain mechanical`) | Term pack | 398 entries (321 TN, 77 TV) |
| Medical, navigation, automotive and railway, energy/oil/gas, civil and military operations, law | Named by the standard for technical verbs; no pack yet | none |
| Electronics, medical devices, pharmaceuticals, construction | No pack | none |

**What the checker finds, and what the agent checks.** `ste.py check` finds sentence
and paragraph length, contractions, semicolons, Latin abbreviations, unapproved words and
modals, perfect and progressive forms, probable passive voice, `-ing` forms, phrasal verbs,
instructions in notes, safety-instruction position (as a convention), synonyms in one
document (rule 1.11), `check` and `test` used as verbs (1.2), and some words with a
restricted meaning (1.3). The agent checks by reading: multi-word nouns (2.1), other
uses of a word with the wrong meaning or part of speech (1.2, 1.3), missing articles
(4.5), one topic per paragraph (6.5), and whether a term fits its category.

**Possible next steps.** There are no dates. A new term pack (medical, or automotive
and railway) needs a contributor who has the standard and checks each entry. A check
for long noun groups (rule 2.1) was too noisy to add in 0.2.0.

**Not planned.** The repository will not contain the official dictionary (that needs
written permission from ASD). The project gives no certification and makes no claim of
compliance.

**Propose a new domain.** Open an issue with the "New term pack" template, or a pull
request that adds `skills/ste100/assets/terms/<domain>.txt` in the pack format (see
CONTRIBUTING.md). Check each entry against your own copy of the standard, and do not
paste the text of the specification into the issue or the pull request.

## How it was tested

Three tasks (write a procedure, check a runbook, edit a guide section), each
graded against a list of assertions by an independent grader agent.

| Configuration | Version | Assertions passed | Tokens, three tasks |
|---|---|---|---|
| With the skill | 0.2.0 | 40 of 42 | 419,854 |
| With the skill, smaller model (Claude Haiku) | 0.2.0 | 39 of 42 | 426,922 |
| With the skill, before the new structure | 0.2.0 draft | 39 of 42 | 459,522 |
| Without the skill | measured with 0.1.0 | 29 of 42 | not recorded |

Read these numbers with care: one run for each configuration, three tasks, and
graders that are language models. A difference of one or two assertions is not
a result. The new structure of 0.2.0 decreased the tokens by approximately 9%;
the quality stayed the same. The run without the skill was not done again for
0.2.0. Two changes came after the 0.2.0 runs and were tested only directly: the
`check` and `test` verb findings, and `count` for many texts in one call. The
test cases are in [`evals/`](evals/).

Without the skill, the model already knows the surface rules (short sentences,
no contractions). The skill adds the word discipline (`check` and `test` are
nouns, not verbs; `press` is not approved, except for a key in computer text),
rule numbers in reports, and the structure rules (a note does not contain an
instruction; by convention, a warning goes before its step).

## Limits and disclaimer

- This is an **unofficial** project. ASD-STE100 is a registered trademark of
  ASD (Aerospace, Security and Defence Industries Association of Europe). The
  name is used here only to identify the standard.
- The repository does **not** contain the official specification or dictionary.
  The rule summaries are written in our own words. The word list is a partial,
  working subset and can contain errors. From version 0.2.0, the summaries and the
  word list were compared with the official Issue 9 text, but they remain our own
  summaries and a partial list.
- The output is **not a certification** of compliance. If compliance is a
  contract requirement, get a review from an STE-trained person with the
  official specification. ASD supplies the specification free of charge on
  request at [asd-ste100.org](https://www.asd-ste100.org).
- The skill is written for Issue 9 (January 2025).

## Security

Read a skill before you install it; a skill is a set of instructions that your
agent will follow. This one is small:

- It has one script with subcommands, [`ste.py`](skills/ste100/scripts/ste.py), and a
  wrapper, [`ste_check.py`](skills/ste100/scripts/ste_check.py). They read the files that
  you give them and print findings. Some commands write a file, and only when you run them:
  `fix --write` (the document), `terms add` (the project terms file), `scan --candidates`
  and `review --candidates` (a file you name), and `import-dictionary` (one file in your
  config folder, or the path you give). They do not use the network and have no dependencies.
  `import-dictionary` reads your own copy of the standard on your machine; the repository
  does not contain it.
- The instructions do not ask the agent to get data from the internet or to run
  any other command.

To report a security problem, see [SECURITY.md](SECURITY.md).

## Contribute

Corrections to the rule summaries, the word list, and the checker are welcome.
Read [CONTRIBUTING.md](CONTRIBUTING.md) first: do not copy text from the
official specification.

## License

[MIT](LICENSE). The license applies to this repository. It gives no rights to
the ASD-STE100 specification or trademark.
