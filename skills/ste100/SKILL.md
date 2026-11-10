---
name: ste100
description: Writes, checks, and edits documents in ASD-STE100 Simplified Technical English (STE, Issue 9). Use whenever the user mentions STE, ASD-STE100, Simplified Technical English, Simplified English, or controlled language, and also when they ask to write or rewrite procedures, work instructions, maintenance tasks, manuals, runbooks, user guides, or safety warnings so that the text is unambiguous, easy to translate, or easy for non-native English readers. Also use to audit or review an existing document against STE rules and report violations, even if the user only says "check this against the simplified English rules" or "make this STE compliant".
license: MIT
compatibility: The bundled checker script needs Python 3 (standard library only). The skill works without it, but with less reliable checks.
metadata:
  author: Free-cat
  version: "0.1.0"
---

# ASD-STE100 Simplified Technical English

STE is a controlled language: 53 writing rules and a dictionary of about 900
approved words, each with one meaning and one part of speech. The purpose is that
a reader with limited English, or a translator, can understand each sentence in
only one way.

## Select the job

| Job | The user gives you | You return |
|---|---|---|
| **Write** | Notes, facts, an outline, or a request | A new document in STE |
| **Check** | An existing document | A findings report. No rewrite. |
| **Edit** | An existing document | The document in STE, and a change summary |

If the request is unclear ("look at this doc"), do a Check and offer the Edit.

## Resources

- [references/rules.md](references/rules.md) — all 53 rules with examples. Read it for a Check or Edit
  job, and when you are not sure about a rule.
- [references/dictionary.md](references/dictionary.md) — unapproved words with approved alternatives,
  part-of-speech traps, technical noun and technical verb categories, and a
  section for software text. Read it for every job. Most violations are word choice.
- `scripts/ste_check.py` — finds the violations that a program can find. Run it;
  do not read it. Python 3 standard library only. It reads one file and prints
  findings. It does not change files and does not use the network.

```bash
python3 scripts/ste_check.py <file> [--type auto|procedure|description] [--terms terms.txt] [--json]
```

`--terms` takes a file with one technical noun or verb on each line (for example
`press`, `torque`). The script then stops reporting those words.

The script is a first pass. It cannot find long multi-word nouns, a wrong meaning,
missing articles, or inconsistent terms. It also reports some correct text (a past
participle used as an adjective looks like passive voice). Examine each finding.

## The rules that cause most violations

1. **Approved words (1.1–1.3).** Use dictionary words with their approved part of
   speech and meaning. *Check* and *test* are nouns ("Do a check of…", "Make sure
   that…"). *Close* is a verb (write "near").
2. **Technical nouns and verbs (1.5–1.13).** Subject-field words come from outside
   the dictionary: parts, tools, materials, software objects, units (nouns), and
   specific processes such as *drill*, *weld*, *click*, *deploy* (verbs). Use one
   term for one thing. A general verb (*verify*, *perform*, *utilize*) is never a
   technical verb.
3. **Verb forms (3.1–3.5).** Infinitive, imperative, simple present, simple past,
   simple future, and the past participle as an adjective. No perfect tense ("has
   failed"), no progressive ("is running"), no *-ing* form unless it is a
   technical noun ("bearing", "operating temperature").
4. **Modal verbs.** CAN and MUST only. Not *should, may, might, could, would, shall*.
5. **Active voice (3.6).** Always in procedures. In descriptions, the passive is
   permitted only if the agent is unknown or not important.
6. **Sentence length (5.1, 6.3).** Procedure: 20 words. Description: 25 words.
   Code, a number with its unit, a label, and text in parentheses each count as one word.
7. **One instruction in each sentence (5.2–5.4).** Write a command. Combine two
   actions only if they occur at the same time. Put a condition first, then a comma.
8. **Do not omit words (4.2, 4.5).** Keep articles and "that". No contractions.
9. **Multi-word nouns (2.1).** Three nouns maximum. Divide a longer one with "of",
   "for", "that", or a hyphen.
10. **Safety and notes (7.1–7.3, 5.5).** A warning or caution starts with a command
    or condition, gives the risk, and goes *before* the step it applies to. A note
    gives information only. If a note contains an instruction, make it a step.
    Safety text obeys the same verb rules: "The threads can become damaged" or
    "This can cause damage to the threads", not "The threads can be damaged".
11. **Paragraphs (6.4–6.6).** One topic, topic sentence first, six sentences
    maximum. Use a vertical list for three or more parallel items (4.3). No semicolons (8.1).

**Change the construction, not only the words (9.1).** STE is not a synonym swap.

| Not STE | Poor (word swap) | STE |
|---|---|---|
| The system should be allowed to cool down prior to commencing disassembly. | The system must be let to cool before start disassembly. | Let the system become cool. Then, disassemble the unit. |
| Having confirmed the valve is closed, proceed with removal of the pump. | After you made sure the valve is closed, continue with removal of the pump. | Make sure that the valve is closed. Then, remove the pump. |
| The cache may need to be cleared if stale data is displayed. | The cache must possibly be cleared if old data is shown. | If the page shows old data, clear the cache. |

## Principles for all three jobs

**Accuracy first.** STE changes how you say something, not what you say. Keep
each fact, value, tolerance, condition, and scope limit. Do not add steps,
warnings, or values that the source does not contain; put a possible gap in the
open questions.

**Do not guess silently.** If the source is ambiguous ("check the oil" — the level
or the condition?), select the most probable meaning and list the point as an open
question. Keep the list short: only points where the answer changes the text.
Three good questions get an answer. Ten do not.

**Leave non-prose text as it is:** code, commands, paths, UI labels, part numbers,
placard text, quoted text, legal text.

**Words that are not in `dictionary.md`.** The file is a subset, so most words are
not in it. Decide in this sequence, and do not make a list of ordinary words "to
confirm":
1. Is it in the unapproved tables? Use the alternative.
2. Does it name a thing or a specific process of the subject field? It is a
   technical noun or verb. Use it, consistently.
3. Is there a simpler word that you know is approved (the core verb list, or a
   word in the STE examples)? Use that word.
4. If not, and the word is plain and has one clear meaning here, use it. Flag a
   word only when a wrong selection can change the meaning.

**Capital letters.** The dictionary file shows approved words in CAPITALS as a
notation. Write them in normal case in documents and in report text ("use must", not
"use MUST").

**Everything you write for the user is in STE too:** suggested corrections,
change summaries, and notes. A correction that has its own violations ("is usually
done by deploying…") teaches the wrong thing. Give file names, not full
file-system paths.

**Claims.** Do not say that a document is certified or fully compliant. Say that
you wrote or checked it against the STE rules. Give the dictionary limit in one
sentence, one time. If compliance is a contract requirement, recommend a review
by an STE-trained person with the official specification (free of charge on
request from asd-ste100.org).

## Workflow: Write

1. Identify each part as a **procedure** (the reader does something) or a
   **description** (the reader learns something). The limits are different.
2. Make the term list: one technical noun for each thing, one verb for each
   process. Use the user's glossary if there is one.
3. Write the draft.
   - Procedure: numbered steps, one command each, conditions first. Put each
     warning or caution immediately before its step, and each note after its step.
   - Description: short paragraphs, topic sentence first.
   - Headings: a short noun phrase or a command ("Start the unit"), not an *-ing* form.
4. Run `scripts/ste_check.py`. Correct the findings. Run it again. Stop when each
   finding that stays is one that you examined and accepted.
5. Read the draft for the points that the script cannot find: multi-word nouns,
   part of speech, articles, one term for one thing, one instruction in each step.
6. Deliver the document. After it, in the reply (or below a rule line, marked as
   notes for the author), give:
   - the technical nouns and verbs from outside the dictionary (not approved
     words such as *remove* or *install*);
   - the open questions.

## Workflow: Check

1. Read `references/rules.md` and `references/dictionary.md`.
2. Run `scripts/ste_check.py` on the document.
3. Examine the findings and discard the false ones. Then read the document for
   the points that the script cannot find (Write step 5), and for structure:
   position of warnings, instructions in notes, steps with more than one action.
4. Write the report with this structure. Keep it short enough to act on: one
   row for each sentence that has a problem, and one row for a problem that
   repeats in many places.

```markdown
# STE report: <file name>

## Summary
<3-5 sentences: text type, general level, the three most important things to
correct first.>

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

Rules for the report:
- Give the rule number or numbers for each row. Quote the original text exactly.
- Give a correction for each row, and make sure that the correction obeys the
  rules (length, verb forms, active voice, approved words).
- Do not report a heading as a long sentence or as a multi-word noun if it has
  three nouns or fewer.
- If the level of a safety instruction looks incorrect (for example WARNING for
  loss of data), say so in the row. WARNING is for injury, CAUTION for damage or
  loss of data.
- Do not include how you made the report (script counts, false findings that you
  discarded, a "limits" section). One sentence about the dictionary limit in the
  summary is sufficient.
- Do not rewrite the full document unless the user asks.

## Workflow: Edit

1. Do Check steps 1–3. The findings are your work list, not the deliverable.
2. Rewrite the document. Keep the structure, the headings, the numbers, and all
   technical content. Divide long sentences and multi-action steps. Move each
   warning or caution to the position before its step. Change an instruction in a
   note into a step or a safety instruction.
3. Run `scripts/ste_check.py` on the result. Correct it and run the script again,
   as in Write step 4.
4. Deliver the document in the same format as the source. Then give a short
   change summary: the main types of change with one before-and-after example of
   each, each place where you changed the structure or the strength of a
   statement ("should" to "must", a note to a step), and the open questions. Do
   not list each changed sentence unless the user asks for a full change log.
