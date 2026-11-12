#!/usr/bin/env python3
"""Generate the word tables in skills/ste100/references from skills/ste100/assets/words.

  python3 tests/build_references.py          write dictionary.md and the generated block in term-details.md
  python3 tests/build_references.py --check  exit 1 if a generated file is out of date (used by tests/run.sh)

Hand-written prose stays in the reference files; only the marked tables are generated.
Standard library only.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "ste100")
WORDS = os.path.join(SKILL, "assets", "words")
REF = os.path.join(SKILL, "references")
TERM_DETAILS = os.path.join(REF, "term-details.md")
BEGIN = "<!-- generated:two-statuses:begin (tests/build_references.py) -->"
END = "<!-- generated:two-statuses:end -->"


def rows(name, count):
    out = []
    with open(os.path.join(WORDS, name), encoding="utf-8") as f:
        for line in f.read().splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                parts = [p.strip() for p in s.split(" | ")]
                if len(parts) != count:
                    raise SystemExit(f"{name}: bad line: {line}")
                out.append(parts)
    return out


def group_unapproved(section):
    """Consecutive lines with the same alternative and example make one table row."""
    groups = []
    for word, sec, pos, alt, flags, note, example in rows("unapproved.txt", 7):
        if sec != section:
            continue
        label = word + (f" ({'v' if pos == 'verb' else 'adj'})" if pos in ("verb", "adjective") else "")
        if groups and groups[-1]["alt"] == alt and groups[-1]["example"] == example:
            groups[-1]["words"].append(label)
        else:
            groups.append({"words": [label], "alt": alt, "example": example})
    return groups


def cell(s):
    return s.replace("|", "\\|")


def table(header, body):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(cell(c) for c in r) + " |" for r in body]
    return "\n".join(lines)


def verb_table():
    body = []
    for g in group_unapproved("verbs"):
        ex = "" if g["example"] == "-" else g["example"]
        body.append([", ".join(g["words"]), g["alt"], ex])
    return table(["Do not use", "Use", "Example in STE"], body)


def plain_table(section):
    body = [[", ".join(g["words"]), g["alt"]] for g in group_unapproved(section)]
    return table(["Do not use", "Use"], body)


def modal_table():
    body = []
    for w, alt, *_ in rows("modals.txt", 2):
        body.append([w, alt])
    body += [
        ["has / have / had + participle", "Simple past, or BE + adjective"],
        ["is / are + -ing", "Simple present"],
    ]
    return table(["Do not use", "Use"], body)


def pos_table():
    body = [[w, a, n, wr] for w, a, n, wr in rows("part-of-speech.txt", 4)]
    return table(["Word", "Approved as", "Not approved as", "Write"], body)


def core_verbs():
    words = [r[0].upper() for r in rows("approved-verbs.txt", 1)]
    lines, cur = [], ""
    for w in words:
        piece = w + ", "
        if len(cur) + len(piece) > 78:
            lines.append(cur.rstrip())
            cur = ""
        cur += piece
    lines.append(cur.rstrip().rstrip(","))
    return "\n".join(lines) + "."


def two_statuses():
    body = [[w, g, s] for w, g, s in rows("two-statuses.txt", 3)]
    return table(["Word", "General sense (not approved)", "Specific sense (permitted)"], body)


DICT_HEAD = """# STE dictionary: working subset

## Contents

1. How the dictionary works
2. Unapproved verbs: approved alternatives
3. Unapproved modal and helping verbs
4. Unapproved connecting words, prepositions, and phrases
5. Unapproved adjectives and adverbs
6. Approved words with a part-of-speech trap
7. Core approved verbs
8. Technical nouns and technical verbs (pointer)

This file is **not** the official ASD-STE100 dictionary. It is a working subset of
the cases that occur most frequently. The official dictionary has 875 approved
words and a selection of 1274 words that are not approved. The status of each word
in this file was compared with Issue 9 (2025-01-15). The selection, the wording,
and the examples are written for this skill. ASD supplies it free of charge on
request (asd-ste100.org). If the user has the official PDF or a company term base,
that source is the authority. If a word is not in this file and you are not sure,
prefer a word that you know is approved, or say that the word must be confirmed.

The tables are generated from `assets/words/` (by `tests/build_references.py`).
To check one word, run `python3 scripts/ste.py lookup WORD`; this file explains
the rules behind the answer.

---

## 1. How the dictionary works

- An approved word has **one part of speech** and **one meaning**. In the official
  dictionary, approved words are in CAPITAL letters and unapproved words in lower
  case. This file uses the same notation. The capitals are a notation only: in a
  document, write the words in normal case ("must", not "MUST").
- An unapproved entry gives one or more approved alternatives. The alternative
  sometimes has a different part of speech, and then you must change the sentence
  construction (rule 9.1).
- The alternatives are suggestions. If the alternative changes the meaning, use
  a different approved word or a different construction.
- A word that is not in the dictionary at all is permitted only as a technical
  noun or a technical verb (see `term-overview.md`). The list of unapproved
  words is a selection, so a word that is not listed here can still be unapproved.
  Absence from this file is not approval.
- Many approved words have a **restricted meaning** (rules 1.3 and 9.2). ABOVE
  and BELOW are for positions, not for limits ("more than 20 psi", not "above
  20 psi"). SEE is for the eyes only ("Refer to Table 2", not "See Table 2").
  TURN is movement around an axis ("The color changes to green", not "turns
  green"). WEAR is damage from friction ("Put on gloves", not "Wear gloves").
- Use only the verb forms that the dictionary gives (rule 3.1), and a past
  participle as an adjective only if the dictionary has it.

## 2. Unapproved verbs: approved alternatives

"""

DICT_TAIL_START = """
## 4. Unapproved connecting words, prepositions, and phrases

"""


def build_dictionary():
    s = DICT_HEAD + verb_table() + "\n\n## 3. Unapproved modal and helping verbs\n\n" + modal_table() \
        + "\n\n## 4. Unapproved connecting words, prepositions, and phrases\n\n" + plain_table("connecting") \
        + "\n\n## 5. Unapproved adjectives and adverbs\n\n" + plain_table("adjectives") \
        + "\n\n## 6. Approved words with a part-of-speech trap\n\n" + pos_table() \
        + "\n\n## 7. Core approved verbs\n\nWhen a suitable verb does not come to mind, start here. All of these are approved:\n\n" \
        + core_verbs() \
        + "\n\nTwo approved phrasal verbs have a restricted meaning: PUT ON (protective\n" \
          "clothing) and COME ON (a light). Do not make other phrasal verbs (rule 9.3).\n\n" \
          "## 8. Technical nouns and technical verbs\n\n" \
          "Words of the subject field (parts, tools, software objects, specific processes)\n" \
          "are not in the dictionary. They are permitted as technical nouns and technical\n" \
          "verbs if they fit a category. The categories, the rules, the words that look\n" \
          "technical but are general, and the guidance for software text are in\n" \
          "`term-overview.md` and `term-details.md`.\n"
    return s


def replace_block(text, block):
    if BEGIN not in text or END not in text:
        raise SystemExit(f"{TERM_DETAILS}: missing generated markers")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + block + "\n" + END + tail


def main(argv):
    check = "--check" in argv
    dict_text = build_dictionary()
    with open(TERM_DETAILS, encoding="utf-8") as f:
        td_now = f.read()
    td_new = replace_block(td_now, two_statuses())
    stale = []
    dict_path = os.path.join(REF, "dictionary.md")
    with open(dict_path, encoding="utf-8") if os.path.exists(dict_path) else open(os.devnull) as f:
        if f.read() != dict_text:
            stale.append(dict_path)
    if td_new != td_now:
        stale.append(TERM_DETAILS)
    if check:
        if stale:
            print("Out of date (run: python3 tests/build_references.py):")
            for p in stale:
                print("  " + os.path.relpath(p, ROOT))
            return 1
        print("Generated references are up to date.")
        return 0
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write(dict_text)
    with open(TERM_DETAILS, "w", encoding="utf-8") as f:
        f.write(td_new)
    print("Generated dictionary.md and the two-statuses table in term-details.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
