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
| Prior to commencing the deployment, verify that all CI checks have passed and ensure the release tag is correct. | 1. Before you deploy, make sure that all CI checks pass.<br>2. Make sure that the release tag is correct. |
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
| **Check** | An existing document | A findings report: rule number, original text, problem, corrected text |
| **Edit** | An existing document | The document in STE, and a summary of the changes |

Example requests:

- "Turn these shop-floor notes into a work instruction in Simplified Technical English."
- "Check `deploy-runbook.md` against the STE rules. Do not rewrite it, only give me a report."
- "Our customer requires ASD-STE100. Rewrite section 4 of this guide and tell me what you changed."

The [`examples/`](examples/) folder has one full input and output for each job.

## What is in the skill

```
skills/ste100/
├── SKILL.md                 # workflows for the three jobs, and the rules that cause most violations
├── references/rules.md      # a summary of all 53 writing rules, with examples
├── references/dictionary.md # common unapproved words and approved alternatives; software terms
└── scripts/ste_check.py     # checker for the rules that a program can find
```

## The checker as a standalone tool

`ste_check.py` has no dependencies (Python 3 standard library). You can use it
without an agent, for example in CI:

```bash
python3 skills/ste100/scripts/ste_check.py docs/runbook.md
python3 skills/ste100/scripts/ste_check.py docs/runbook.md --json --strict
python3 skills/ste100/scripts/ste_check.py docs/manual.md --terms terms.txt
```

It reports sentence length (20 words in a procedure, 25 in a description),
contractions, semicolons, Latin abbreviations, unapproved words and modal verbs,
perfect and progressive tenses, probable passive voice, `-ing` forms, phrasal
verbs, long paragraphs, and instructions in notes.

It is a first pass. It cannot find long multi-word nouns, a word with the wrong
meaning, missing articles, or inconsistent terms, and it reports some correct
text. The skill tells the agent to examine each finding.

## How it was tested

Three tasks (write a procedure, check a runbook, edit a guide section), each
graded against a list of assertions by an independent grader agent.

| Configuration | Assertions passed |
|---|---|
| With the skill | 39 of 42 |
| With the skill, smaller model (Claude Haiku) | 40 of 42 |
| Without the skill | 29 of 42 |

Read these numbers with care: one run for each configuration, three tasks, and
graders that are language models. With the skill, a task took about 2.5 times
longer. The test cases are in [`evals/`](evals/).

Without the skill, the model already knows the surface rules (short sentences,
no contractions). The skill adds the word discipline (`check`, `test`, `press`
are not approved verbs), rule numbers in reports, and the structure rules (a
warning goes before its step; a note does not contain an instruction).

## Limits and disclaimer

- This is an **unofficial** project. ASD-STE100 is a registered trademark of
  ASD (Aerospace, Security and Defence Industries Association of Europe). The
  name is used here only to identify the standard.
- The repository does **not** contain the official specification or dictionary.
  The rule summaries are written in our own words. The word list is a partial,
  working subset and can contain errors.
- The output is **not a certification** of compliance. If compliance is a
  contract requirement, get a review from an STE-trained person with the
  official specification. ASD supplies the specification free of charge on
  request at [asd-ste100.org](https://www.asd-ste100.org).
- The skill is written for Issue 9 (January 2025).

## Security

Read a skill before you install it; a skill is a set of instructions that your
agent will follow. This one is small:

- It has one executable file, [`ste_check.py`](skills/ste100/scripts/ste_check.py).
  The script reads the file that you give it and prints findings. It does not
  write files, does not use the network, and has no dependencies.
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
