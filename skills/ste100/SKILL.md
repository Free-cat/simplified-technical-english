---
name: ste100
description: Writes, checks, and edits documents in ASD-STE100 Simplified Technical English (STE, Issue 9). Use whenever the user mentions STE, ASD-STE100, Simplified Technical English, Simplified English, or controlled language, and also when they ask to write or rewrite procedures, work instructions, maintenance tasks, manuals, runbooks, user guides, or safety warnings so that the text is unambiguous, easy to translate, or easy for non-native English readers. Also use to audit or review an existing document against STE rules and report violations, even if the user only says "check this against the simplified English rules" or "make this STE compliant".
license: MIT
compatibility: The bundled scripts need Python 3 (standard library only). Without Python the skill still works; the word checks then use grep on the text files in assets/.
metadata:
  author: Free-cat
  version: "0.2.0"
---

# ASD-STE100 Simplified Technical English

STE is a controlled language: 53 writing rules, and a dictionary of 875 approved
words, each with one approved meaning and part of speech. A reader with limited
English, or a translator, then understands each sentence in only one way. The word
lists in this skill are a working subset, not the official dictionary.

## Select the job

| Job | The user gives you | You return |
|---|---|---|
| **Write** | Notes, facts, an outline, or a request | A new document in STE |
| **Check** | An existing document | A findings report. No rewrite. |
| **Edit** | An existing document | The document in STE, and a change summary |

If the request is unclear ("look at this doc"), do a Check and offer the Edit.

## Trigger table: what to open

Open only the files in this table. Everything else is loaded on demand.

| When | Open |
|---|---|
| Always | This file |
| Any Check or Edit job | `references/rules-summary.md` (all 53 rules, one line each) |
| The document has subject-field words: parts, tools, materials, software objects, specific processes | `references/term-overview.md` (decision procedure, term categories, term list format) |
| The checker reports a rule and you are not sure of it | `references/rules-details.md`, section for the first digit of the rule (rule 5.2 → section 5) |
| A term does not fit a category, or a word has two statuses | `references/term-details.md` (section 1 or 3 for the category; section 6 for two statuses) |
| A part-of-speech or meaning question ("is *check* a verb here?") | `references/dictionary.md` (section 6 for traps, section 2 for verbs) |
| Software, IT, DevOps, or a runbook | `references/software-text.md` |

Do not read `scripts/ste.py`. Execute it.

## Scripts

Run from the skill folder.

```bash
python3 scripts/ste.py review [--domain D] [--terms F] [--source SRC] [--candidates OUT] FILE
python3 scripts/ste.py scan [--domain D] [--candidates OUT] FILE   # unknown words, as a terms file
python3 scripts/ste.py check [--domain D] [--terms F] [--source SRC] [--all] FILE
python3 scripts/ste.py fix [--domain D] FILE                       # safe replacements as a diff; --write applies
python3 scripts/ste.py lookup WORD...                              # one line per word
python3 scripts/ste.py count TEXT... [--from FILE]                 # one line per text; one call for all
python3 scripts/ste.py terms add [--file F] [--from FILE] "term | TN | 19 | ext" ...
```

`review` is the first pass: unknown words, the safe fixes (count and list), and the
check findings, in one call. `--source SRC` adds the accuracy check against the notes.
`--domain` loads a term pack (`software` or `mechanical`); repeat it for more than one.
Pick the domain once for the whole document. `--no-local-dictionary` ignores the local word list.

**Expected calls.** A typical job takes 3 to 5 script calls: `review`, optional `fix --write`,
`check` after your edits, a final `check`, and at most one `count` for all texts. At a sixth call, stop.

**Terms in one step, never one call per term.** Each call costs a full round trip. Pass
accepted terms to one `terms add` (many entries, or `--from FILE`), or use the candidates file:
`scan --candidates OUT` writes the unknown words; delete the lines that are not terms, then pass
the file with `--terms OUT`.

**Project terms file.** Accepted terms go in `ste-terms.txt` (or `--terms FILE`). **Ask the author
before you create it in their project.** If the author says no, use a scratch file and pass it with `--terms`.

**Local word list (optional).** If the author has the official standard, run
`python3 scripts/ste.py import-dictionary SOURCE` once (their PDF, or a `.txt` from
`pdftotext -layout`). It writes `~/.config/ste100/dictionary.txt` on the author's machine,
outside this folder and any repository; `lookup` and `scan` then use it. The skill works
without it. Never copy that file into a project.

No Python? Grep `assets/words/` and `assets/terms/`, and check the rules by reading
`references/rules-summary.md`.

## The rules that cause most violations

1. **Approved words (1.1–1.3).** Use dictionary words in their approved part of speech
   and meaning. *Check* and *test* are nouns ("Do a check of…", "Make sure that…"). As an
   adjective, *close* becomes "near". "More than 20 psi", not "above 20 psi"; "Refer to
   Table 2", not "See Table 2"; "Put on eye protection", not "Wear eye protection"; "The
   color changes to green", not "The valve turns green". *Press* is not approved (use
   *push*), except for a key in computer text. *Enable* and *disable* are technical verbs
   for user-interface settings. A verb use of *check*, *test*, or another noun-only word is not
   permitted anywhere in a sentence, also after a condition: "When the light comes on, check…" is
   not STE; write "…, make sure that…" or "…, do a check of…".
2. **Technical nouns and verbs (1.5–1.13).** Subject-field words come from outside the
   dictionary. Each must fit one of the 22 noun categories or 4 verb categories. One name
   for one thing. **An approved verb comes first**: "find", not "detect". A general verb
   (*verify*, *perform*, *utilize*) is never a technical verb.
3. **Verb forms (3.1–3.5).** Infinitive, imperative, simple present, simple past, simple
   future, and the past participle as an adjective. No perfect ("has failed"), no
   progressive ("is running"), no *-ing* form unless it is a technical noun ("bearing").
4. **Modal verbs.** Use CAN and MUST; WILL is the simple future. Not *should, may, might,
   could, would, shall, ought to, need to, have to*.
5. **Active voice (3.6).** Always in procedures. In descriptions, the passive is permitted
   **only if the agent is unknown**.
6. **Word count (5.1, 6.3).** A procedure or safety instruction has **20 words at most**;
   a description or note has **25 words at most**. **One word** is: a number with its unit,
   a label, quoted text, and text in parentheses (each counts as one). A hyphenated word
   counts as one. In software text, code in backticks counts as one word (a convention of
   this skill). The checker prints the count of each over-length sentence; for another length you
   report, use one `count` call.
7. **One instruction per sentence (5.2–5.4).** Write a command, without "must" before it.
   Combine two actions only if they happen at the same time. Put a condition first, then a comma.
8. **Keep the words (4.2, 4.5).** Keep articles and "that". No contractions.
9. **Multi-word nouns (2.1).** **Three words at most** (nouns and adjectives count). Split a
   longer one with "of", "for", or "that".
10. **Safety and notes (7.1–7.3, 5.5).** A warning or caution starts with a command or a
    condition, and states the risk. WARNING is for injury or death; CAUTION for damage. A
    note gives information only: no instructions, requirements, or limits. An instruction
    in a note becomes a step. Put a warning before the step it applies to (a convention of
    technical publication, not an STE rule). Use active verbs: "This can cause damage to
    the threads", not "The threads can be damaged".
11. **Paragraphs and punctuation (6.4–6.6, 8.1).** One topic, topic sentence first, six
    sentences at most. A vertical list for many items (4.3). No semicolons.

**Change the construction, not only the words (9.1).** STE is not a list of synonyms.

| Not STE | Poor (word swap) | STE |
|---|---|---|
| The system should be allowed to cool down prior to commencing disassembly. | The system must be let to cool before start disassembly. | Let the system become cool. Then, disassemble the unit. |
| Having confirmed the valve is closed, proceed with removal of the pump. | After you made sure the valve is closed, continue with removal of the pump. | Make sure that the valve is closed. Then, remove the pump. |
| The cache may need to be cleared if stale data is displayed. | The cache must possibly be cleared if old data is shown. | If the page shows old data, clear the cache. |

## Principles for all three jobs

**Accuracy first.** STE changes how you say something, not what you say. Keep each fact,
value, tolerance, condition, and scope limit. Do not add steps, warnings, values, part
numbers, or locations that the source does not give. Put a possible gap in the open questions.

**Do not guess silently.** If the source is ambiguous ("check the oil": the level or the
condition?), pick the most probable meaning and list the point as an open question. Keep
the list short: three good questions get an answer, ten do not.

**Leave non-prose text as it is:** code, commands, paths, UI labels, part numbers, placard
text, quoted text, legal text.

**Unknown words.** A word that no list knows is not approved for that reason alone. Decide
it in this order: (1) an unapproved entry, use the alternative; (2) a technical noun or
verb of the subject field that fits a category (`references/term-overview.md`), use it
consistently; (3) a simpler approved word you know; (4) otherwise rewrite the sentence with
approved words (rule 9.1). Ask the author only about words that stay unclear.

**Capitals.** Dictionary entries show approved words in capitals as a notation. Write them
in normal case ("use must", not "use MUST"). The scripts print suggestions in normal case too.

**Everything you write for the user is in STE too:** corrections, change summaries, notes.
Give file names, not full file-system paths.

**Claims.** Do not say that a document is certified or fully compliant. Say that you checked it
against the STE rules, and give the dictionary limit in one sentence. For a contract requirement,
recommend a review by an STE-trained person with the official specification (asd-ste100.org).

## What the author sees

- A term that a domain pack or the project terms file records is settled. Never show it to
  the author, and never put it in the open questions.
- Only terms that are in no pack are listed for the author. Write or edit: a short list
  after the document, one line each (the term, its category, why you accepted it). Check:
  only if a term decision changes a finding.
- A Check report never describes how it was made: no script names, counts of script output,
  discarded findings, or tool limits. The one sentence on the dictionary limit is the exception.
- Open questions are only about meaning that changes the text. Maximum five.

## Workflow: Write

1. Identify each part as a **procedure** (the reader does something: 20 words) or a
   **description** (the reader learns something: 25 words).
2. Pick the domain once (`software`, `mechanical`, or none). If the notes are the source,
   save them to a scratch file and pass it as `--source`.
3. Draft it. Procedure: numbered steps, one command each, conditions first; a warning or
   caution just before its step; a note after it. Description: topic sentence first.
4. Save the draft and run `review --domain D --source NOTES --candidates OUT FILE` (one call).
   Decide the unknown words: delete the lines in OUT that are not terms (see "Terms in one step").
5. Run `fix --domain D --write` if the proposed list is right; otherwise change the draft by hand.
6. Run `check`, fix each real violation, and run `check` again (see the feedback loop).
7. Read the draft for what the scripts cannot find: multi-word nouns, part of speech, missing
   articles, one term for one thing, one instruction in each step.
8. Deliver the document, then the terms in no pack and the open questions (see "What the author sees").

## Workflow: Check

1. Read `references/rules-summary.md`. Use `term-overview.md` if the document has subject-field words.
2. `review --domain D [--terms F] [--source SRC] FILE` (one call): unknown words, safe fixes
   (count and list), check findings by rule, and a separate source comparison block.
3. Decide the unknown words as in Write step 4. Words in a domain pack are settled: do not list them.
   Source comparison items go into your fix list or the open questions, not the findings table.
4. Discard the false findings. Then read for what the script cannot find: long multi-word
   nouns, warning position, instructions in notes, multi-action steps.
5. Write the report in the format below.

```markdown
# STE report: <file name>

## Summary
<3-5 sentences: text type, general level, the three most important things to correct first.>

| Rule | Topic | Findings |
|---|---|---|
| 1.1 | Unapproved word | 12 |

## Findings
| # | Location | Rule | Original text | Problem | Suggested STE text |
|---|---|---|---|---|---|
| 1 | Step 2 | 3.6, 1.1 | "The cover should be removed" | Passive voice. "should" is not approved. | "Remove the cover." |

## Open questions
<Only if there are some. Maximum five.>
```

Report rules:
- Each row cites an STE rule number, or a GR number from `rules-summary.md`. A convention of this
  skill (such as the position of a safety instruction) is marked "convention" in the row, never
  given a rule number it does not have.
- Quote the original text exactly, and give a correction that obeys the rules (length,
  verb forms, active voice, approved words).
- Do not report a heading of three words or fewer as a long noun.
- If a safety instruction's level looks wrong, say so in the row. This skill reads loss of
  data as damage (CAUTION); the author must check that against their standard.
- Follow "What the author sees". Do not rewrite the document unless asked.

## Workflow: Edit

1. Do Check steps 1–4. The findings are your work list, not the deliverable.
2. Rewrite the document. Keep the structure, headings, numbers, and all technical content.
   Divide long sentences and multi-action steps. Move each warning or caution before its step.
   Change an instruction in a note into a step or a safety instruction. Do not add a location,
   part, or value that the source does not give: put the gap in the open questions.
3. Save the result, then run `review --source SRC` on it, `fix --write` if the diff is right,
   and the feedback loop below.
4. Deliver the document in the source's format, then a short change summary: the main types of
   change with one before-and-after example each (including each change of strength, such as
   "should" to "must"), and the open questions. Do not list each changed sentence unless asked.

## Feedback loop (Check, Edit, Write step 6)

1. Run `check --domain D --terms FILE [--source SRC] FILE` after each round of edits; fix each
   real violation within the rules. Two rounds are normal: one after the edits, one final.
2. Stop when every remaining finding is one you examined and accepted, and say which ones in the report.

Degrees of freedom: use the checker command as written; the wording is your judgment, within the rules.
