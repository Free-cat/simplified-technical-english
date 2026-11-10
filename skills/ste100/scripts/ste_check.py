#!/usr/bin/env python3
"""ste_check.py - first-pass checker for ASD-STE100 Simplified Technical English.

Finds the violations that a program can find without a parser:
sentence length, contractions, semicolons, Latin abbreviations, unapproved
words and modal verbs, perfect/progressive/passive patterns, -ing forms,
phrasal verbs, long paragraphs, instructions in notes, and more.

It is a first pass. Read each finding. See the skill's SKILL.md.

Usage:
    python3 ste_check.py FILE [--type auto|procedure|description]
                              [--terms TERMS.txt] [--json] [--strict]

--type   auto (default): numbered-list items are procedure text (20 words),
         all other text is description (25 words).
--terms  a file with one approved technical noun/verb per line. These words
         are not reported as unapproved words or as -ing forms.
--json   machine-readable output.
--strict exit code 1 if there is at least one finding of severity "error".

Standard library only.
"""
import argparse
import json
import re
import sys
from collections import Counter

# --------------------------------------------------------------------------
# Word data (working subset; see references/dictionary.md)
# --------------------------------------------------------------------------

# unapproved word (lemma) -> suggestion
UNAPPROVED = {
    # verbs
    "verify": "MAKE SURE", "ensure": "MAKE SURE", "confirm": "MAKE SURE",
    "validate": "MAKE SURE / DO A CHECK", "ascertain": "MAKE SURE",
    "inspect": "EXAMINE", "perform": "DO", "conduct": "DO", "execute": "DO",
    "accomplish": "DO", "utilize": "USE", "utilise": "USE", "employ": "USE",
    "leverage": "USE", "require": "BE NECESSARY / MUST", "allow": "LET / CAN",
    "permit": "LET / CAN", "enable": "LET / CAN", "obtain": "GET",
    "acquire": "GET", "retrieve": "GET", "provide": "GIVE / SUPPLY",
    "furnish": "GIVE / SUPPLY", "insert": "PUT ... IN", "depress": "PUSH",
    "press": "PUSH", "rotate": "TURN", "locate": "FIND", "detect": "FIND",
    "discover": "FIND", "indicate": "SHOW", "exhibit": "SHOW",
    "reveal": "SHOW", "observe": "SEE / MONITOR / OBEY", "notice": "SEE",
    "begin": "START", "commence": "START", "initiate": "START",
    "activate": "START / OPERATE", "terminate": "STOP", "cease": "STOP",
    "halt": "STOP", "deactivate": "STOP", "finish": "COMPLETE",
    "finalize": "COMPLETE", "reduce": "DECREASE", "lessen": "DECREASE",
    "diminish": "DECREASE", "elevate": "LIFT / INCREASE",
    "alter": "CHANGE", "modify": "CHANGE / ADJUST", "amend": "CHANGE",
    "maintain": "KEEP", "retain": "KEEP", "preserve": "KEEP",
    "fasten": "ATTACH", "affix": "ATTACH", "detach": "DISCONNECT / REMOVE",
    "unfasten": "DISCONNECT / REMOVE", "rectify": "REPAIR / CORRECT",
    "substitute": "REPLACE", "swap": "REPLACE", "toggle": "SET",
    "choose": "SELECT", "determine": "FIND / CALCULATE / MAKE SURE",
    "establish": "FIND / MAKE SURE", "comprise": "HAVE / INCLUDE / CONTAIN",
    "avoid": "PREVENT / DO NOT", "attempt": "(rewrite)", "repeat": "DO ... AGAIN",
    "exceed": "BE MORE THAN", "remain": "STAY", "inform": "TELL",
    "notify": "TELL", "advise": "TELL / RECOMMEND", "proceed": "CONTINUE / GO",
    "dispose": "DISCARD", "wait": "(rewrite with AFTER / UNTIL)",
    "need": "BE NECESSARY / MUST", "check": "MAKE SURE / DO A CHECK / EXAMINE (CHECK is a noun)",
    "test": "DO A TEST (TEST is a noun)",
    # connecting words and prepositions
    "since": "BECAUSE (cause) / FROM (time)", "although": "BUT", "though": "BUT",
    "whereas": "BUT", "however": "BUT", "therefore": "AS A RESULT / THUS",
    "hence": "AS A RESULT", "consequently": "AS A RESULT", "whether": "IF",
    "upon": "WHEN / AFTER / ON", "via": "THROUGH / WITH", "within": "IN / LESS THAN",
    "per": "FOR EACH / REFER TO", "till": "UNTIL", "whilst": "WHILE",
    "currently": "AT THIS TIME / NOW", "presently": "AT THIS TIME / NOW",
    "subsequently": "THEN / AFTER", "furthermore": "ALSO", "moreover": "ALSO",
    "additionally": "ALSO",
    # adjectives and adverbs
    "appropriate": "CORRECT / APPLICABLE", "proper": "CORRECT",
    "properly": "CORRECTLY", "suitable": "CORRECT / APPLICABLE",
    "adequate": "SUFFICIENT", "enough": "SUFFICIENT", "ample": "SUFFICIENT",
    "essential": "NECESSARY / IMPORTANT", "vital": "NECESSARY / IMPORTANT",
    "crucial": "NECESSARY / IMPORTANT", "mandatory": "NECESSARY",
    "big": "LARGE", "huge": "LARGE", "tiny": "SMALL", "entire": "ALL / FULL",
    "whole": "ALL / FULL", "numerous": "MANY", "multiple": "MANY / SOME",
    "several": "SOME", "various": "DIFFERENT", "additional": "MORE / OTHER",
    "extra": "MORE / OTHER", "further": "MORE / OTHER", "final": "LAST",
    "adjacent": "NEAR", "nearby": "NEAR", "faulty": "DAMAGED / UNSERVICEABLE",
    "defective": "DAMAGED / UNSERVICEABLE", "broken": "DAMAGED / UNSERVICEABLE",
    "inoperative": "UNSERVICEABLE", "gently": "CAREFULLY / SLOWLY",
    "rapidly": "QUICKLY", "swiftly": "QUICKLY", "promptly": "IMMEDIATELY",
    "nearly": "APPROXIMATELY", "roughly": "APPROXIMATELY",
    "simply": "(delete)", "just": "(delete)", "basically": "(delete)",
    "please": "(delete; give the command directly)", "robust": "(delete or be specific)",
    "seamless": "(delete or be specific)", "seamlessly": "(delete or be specific)",
    "prior": "BEFORE", "about": "APPROXIMATELY (for quantity); ABOUT is approved only for 'concerned with'",
}

# These lemmas are reported only as "info" because they are often correct
# (noun use, or an approved meaning).
SOFT = {"check", "test", "about", "since", "need", "press", "further",
        "final", "just", "within", "per", "wait", "repeat", "require"}

MODALS = {
    "should": "MUST (obligation) / RECOMMEND (advice)",
    "shall": "MUST", "ought": "MUST",
    "may": "CAN (permission) / POSSIBLY (possibility)",
    "might": "CAN / POSSIBLY", "could": "CAN", "would": "(rewrite in simple present or future)",
}

PHRASES = [  # (regex, rule, severity, message)
    (r"\bin order to\b", "1.1", "error", '"in order to" -> TO'),
    (r"\bso as to\b", "1.1", "error", '"so as to" -> TO'),
    (r"\bprior to\b", "1.1", "error", '"prior to" -> BEFORE'),
    (r"\bsubsequent to\b", "1.1", "error", '"subsequent to" -> AFTER'),
    (r"\bdue to\b", "1.1", "error", '"due to" -> BECAUSE OF'),
    (r"\bowing to\b", "1.1", "error", '"owing to" -> BECAUSE OF'),
    (r"\bin the event (that|of)\b", "1.1", "error", '"in the event that" -> IF'),
    (r"\bin case( of)?\b", "1.1", "warning", '"in case" -> IF'),
    (r"\bprovided that\b", "1.1", "error", '"provided that" -> IF'),
    (r"\bas well as\b", "1.1", "error", '"as well as" -> AND / ALSO'),
    (r"\bin addition( to)?\b", "1.1", "warning", '"in addition" -> ALSO / AND'),
    (r"\bby means of\b", "1.1", "error", '"by means of" -> WITH / THROUGH'),
    (r"\bin accordance with\b", "1.1", "error", '"in accordance with" -> REFER TO / OBEY'),
    (r"\bas per\b", "1.1", "error", '"as per" -> REFER TO / OBEY'),
    (r"\bin excess of\b", "1.1", "error", '"in excess of" -> MORE THAN'),
    (r"\bat this point\b", "1.1", "warning", '"at this point" -> AT THIS TIME / NOW'),
    (r"\bmake use of\b", "1.1", "error", '"make use of" -> USE'),
    (r"\bconsists? of\b", "1.1", "error", '"consist of" -> HAVE / INCLUDE / CONTAIN'),
    (r"\b(has|have|had) to\b", "3.4", "error", '"have to" -> MUST'),
    (r"\bneeds? to\b", "3.4", "error", '"need to" -> MUST'),
    (r"\b(is|are) to be\b", "3.4", "error", '"is to be" -> MUST BE, or use a command'),
    (r"\bought to\b", "3.4", "error", '"ought to" -> MUST'),
    (r"\b(and so on|and so forth)\b", "GR-6", "error", 'Give the full list or "and other ..."'),
    (r"\bmake sure (?!that\b)", "GR-1", "warning", 'Keep "that" after MAKE SURE'),
    (r"\bbe sure (to|that)\b", "1.1", "warning", '"be sure" -> MAKE SURE THAT'),
    (r"\bas (needed|required|necessary|applicable|appropriate)\b", "4.1", "warning",
     'Vague phrase. Say when or how much.'),
    (r"\bif (needed|required|necessary|applicable|appropriate)\b", "4.1", "info",
     'Vague condition. Say what the condition is.'),
]

PHRASAL = {
    "carry out": "DO", "set up": "PREPARE / INSTALL", "find out": "FIND",
    "figure out": "FIND / CALCULATE", "go on": "CONTINUE", "put out": "EXTINGUISH / STOP",
    "shut down": "STOP", "shut off": "STOP / CLOSE", "switch on": "SET TO ON / START",
    "switch off": "SET TO OFF / STOP", "turn on": "SET TO ON / START",
    "turn off": "SET TO OFF / STOP", "take out": "REMOVE", "take off": "REMOVE",
    "put on": "INSTALL / ATTACH", "pick up": "LIFT / GET", "look at": "SEE / EXAMINE",
    "look for": "FIND", "get rid of": "DISCARD / REMOVE", "throw away": "DISCARD",
    "fill out": "COMPLETE", "fill in": "COMPLETE / WRITE", "hook up": "CONNECT",
    "plug in": "CONNECT", "top up": "ADD / FILL", "cool down": "BECOME COOL",
    "warm up": "BECOME WARM", "end up": "(rewrite)", "come up": "(rewrite)",
    "bring up": "(rewrite)", "work out": "CALCULATE / FIND", "make up": "(rewrite)",
    "point out": "SHOW / TELL", "deal with": "(rewrite)", "kick off": "START",
    "spin up": "START", "tear down": "REMOVE / DISASSEMBLE",
}

LATIN = [
    (r"\be\.g\.?(?=\W|$)", '"e.g." -> FOR EXAMPLE'),
    (r"\bi\.e\.?(?=\W|$)", '"i.e." -> THAT IS'),
    (r"\betc\.?(?=\W|$)", '"etc." -> give the full list or "and other ..."'),
    (r"\bvs\.?(?=\W|$)", '"vs." -> COMPARED WITH'),
    (r"\bviz\.?(?=\W|$)", '"viz." -> THAT IS'),
    (r"\bN\.?B\.(?=\W|$)", '"N.B." -> NOTE'),
    (r"\bca\.(?=\W|$)", '"ca." -> APPROXIMATELY'),
]

BRITISH = {
    "colour": "color", "centre": "center", "metre": "meter", "litre": "liter",
    "fibre": "fiber", "grey": "gray", "aluminium": "aluminum", "analyse": "analyze",
    "organise": "organize", "recognise": "recognize", "minimise": "minimize",
    "maximise": "maximize", "initialise": "initialize", "authorise": "authorize",
    "licence": "license", "catalogue": "catalog", "programme": "program",
    "behaviour": "behavior", "labelled": "labeled", "cancelled": "canceled",
    "travelled": "traveled", "tyre": "tire", "vapour": "vapor", "defence": "defense",
    "customise": "customize", "synchronise": "synchronize", "prioritise": "prioritize",
}

BE = {"is", "are", "was", "were", "be", "been", "being", "am"}
HAVE = {"has", "have", "had", "having"}

IRREGULAR_PP = {
    "been", "done", "made", "given", "taken", "seen", "shown", "known", "found",
    "put", "set", "sent", "kept", "held", "written", "read", "run", "built",
    "broken", "bent", "blown", "cut", "driven", "fallen", "felt", "got", "gotten",
    "gone", "heard", "left", "lost", "paid", "sold", "told", "thought", "worn",
    "drawn", "torn", "frozen", "chosen", "begun", "become", "brought", "bought",
    "caught", "come", "fed", "hidden", "hung", "led", "met", "shut", "spent",
    "stuck", "understood", "withdrawn", "wound",
}

# -ed words that are normally adjectives of state: not reported as passive.
STATE_ADJ = {
    "closed", "damaged", "installed", "connected", "disconnected", "attached",
    "locked", "unlocked", "engaged", "disengaged", "aligned", "pressurized",
    "extended", "retracted", "approved", "related", "located", "contaminated",
    "worn", "broken", "bent", "blocked", "energized", "grounded", "sealed",
    "required", "recommended", "permitted", "prohibited", "completed",
    "tightened", "loosened", "enabled", "disabled", "satisfied", "set",
    "shut", "stuck", "frozen", "torn", "cracked", "corroded", "scratched",
}

NOT_PP = {"need", "speed", "feed", "seed", "bleed", "exceed", "proceed",
          "indeed", "hundred", "red", "bed", "shed", "embed", "led",
          "naked", "wicked", "rugged", "sacred", "biped", "unused"}

# -ing words that are not verb forms, or are very common technical nouns.
ING_OK = {
    "thing", "nothing", "something", "anything", "everything", "during",
    "ring", "string", "spring", "king", "wing", "bring", "sing", "sling",
    "swing", "cling", "ping", "bearing", "housing", "wiring", "opening",
    "setting", "warning", "fitting", "casing", "coating", "building",
    "ceiling", "tubing", "piping", "plating", "bushing", "fairing",
    "landing", "mounting", "packing", "lining", "marking", "reading",
    "rating", "meeting", "heading", "training", "drawing", "testing",
    "logging", "computing", "networking", "engineering", "manufacturing",
    "machining", "processing", "painting", "welding", "soldering", "bonding",
    "cleaning", "cooling", "heating", "lighting", "timing", "routing",
    "padding", "morning", "evening", "inning", "shilling", "sibling",
    "interesting", "according", "following", "o-ring", "plumbing", "seating",
}

IMPERATIVE_HINT = {
    "add", "adjust", "align", "apply", "attach", "calculate", "calibrate",
    "change", "clean", "click", "close", "connect", "continue", "cut",
    "decrease", "delete", "disassemble", "discard", "disconnect", "do",
    "download", "drain", "dry", "enter", "examine", "fill", "find", "get",
    "give", "hold", "identify", "increase", "install", "keep", "let", "lift",
    "lock", "loosen", "lower", "lubricate", "make", "measure", "mix",
    "monitor", "move", "obey", "open", "operate", "prepare", "pull", "push",
    "put", "read", "record", "refer", "release", "remove", "repair",
    "replace", "restart", "run", "save", "select", "send", "set", "start",
    "stop", "tell", "tighten", "torque", "touch", "turn", "type", "unlock",
    "upload", "use", "write", "copy", "paste", "log", "deploy", "merge",
    "commit", "check", "verify", "ensure", "inspect", "test", "press",
    "rotate", "insert", "wait", "restart", "reboot", "create", "wipe",
    "allow", "place", "position", "perform", "confirm", "go", "scroll",
}

CONTRACTION = re.compile(
    r"\b(?:[A-Za-z]+n[’']t|[A-Za-z]+[’'](?:ll|re|ve|d|m)|"
    r"(?:it|that|there|here|what|who|he|she|let|where|how)[’']s)\b",
    re.IGNORECASE,
)

WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")


# --------------------------------------------------------------------------
# Text preparation
# --------------------------------------------------------------------------

def lemma_candidates(w):
    """Cheap lemmatizer: returns possible base forms of a lower-case word."""
    c = [w]
    if w.endswith("ies") and len(w) > 4:
        c.append(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3:
        c.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        c.append(w[:-1])
    if w.endswith("ied") and len(w) > 4:
        c.append(w[:-3] + "y")
    if w.endswith("ed") and len(w) > 3:
        c += [w[:-2], w[:-1]]
        if len(w) > 5 and w[-3] == w[-4]:
            c.append(w[:-3])
    if w.endswith("ing") and len(w) > 5:
        c += [w[:-3], w[:-3] + "e"]
        if w[-4] == w[-5]:
            c.append(w[:-4])
    return c


def is_participle(w):
    w = w.lower()
    if w in NOT_PP:
        return False
    if w in IRREGULAR_PP:
        return True
    return len(w) > 3 and w.endswith("ed")


def mask(text):
    """Replace non-prose spans with a one-word placeholder (rule 8.6)."""
    text = re.sub(r"`[^`\n]+`", "CODE", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)      # links
    text = re.sub(r"https?://\S+", "URL", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", lambda m: m.group(1), text)
    text = re.sub(r"(?<!\w)[*_]([^*_\n]+)[*_](?!\w)", r"\1", text)
    return text


def count_words(sentence):
    """Word count with the STE conventions (rules 8.5-8.7)."""
    s = re.sub(r"\([^()]*\)", " PAREN ", sentence)             # 8.5
    s = re.sub(r'"[^"]*"|“[^”]*”', " QUOTE ", s)                # 8.6 quoted text
    s = re.sub(r"\b\d+(?:[.,]\d+)*\s?(?:°\s?[CF]|%|[A-Za-zµ]{1,4}\b(?=\W|$))?",
               lambda m: " NUM " if re.fullmatch(
                   r"\d+(?:[.,]\d+)*\s?(?:°\s?[CF]|%|mm|cm|m|km|in|ft|kg|g|mg|lb|oz|psi|bar|kPa|MPa|Pa|Nm|N|V|mV|kV|A|mA|W|kW|Hz|kHz|MHz|GHz|rpm|s|ms|min|h|hr|L|l|ml|mL|GB|MB|KB|TB|kB)?",
                   m.group(0)) else " NUM " + " X ", s)
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-./_]*", s)   # 8.7 hyphen = 1
    return len(tokens)


def split_sentences(text):
    """Split a block of prose into sentences. Returns list of strings."""
    protected = re.sub(r"\b(e\.g|i\.e|vs|Fig|No|approx|max|min|Mr|Ms|Dr|St|Ref|para)\.",
                       lambda m: m.group(0).replace(".", "§"), text)
    protected = re.sub(r"(\d)\.(\d)", r"\1§\2", protected)
    parts = re.split(r"(?<=[.!?])\s+(?=[\"“(A-Z0-9])|(?<=:)\s*\n", protected)
    return [p.replace("§", ".").strip() for p in parts if p.strip()]


class Block:
    def __init__(self, kind, line, text):
        self.kind = kind      # "step", "bullet", "para", "heading", "safety", "note"
        self.line = line
        self.text = text


SAFETY_RE = re.compile(r"^\s*(?:>\s*)?(?:\*\*|__)?\s*(WARNING|CAUTION|DANGER|NOTICE)\b\s*:?", re.I)
NOTE_RE = re.compile(r"^\s*(?:>\s*)?(?:\*\*|__)?\s*(NOTE|Note|TIP|Tip)\b\s*:?(?:\*\*|__)?\s*:?")


def parse_blocks(raw):
    """Markdown / plain text -> prose blocks with line numbers."""
    lines = raw.splitlines()
    blocks, buf, buf_line, buf_kind = [], [], 0, None
    in_code = in_front = False

    def flush():
        nonlocal buf, buf_kind
        if buf:
            blocks.append(Block(buf_kind, buf_line, " ".join(buf)))
        buf, buf_kind = [], None

    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if i == 1 and s.strip() == "---":
            in_front = True
            continue
        if in_front:
            if s.strip() == "---":
                in_front = False
            continue
        if re.match(r"^\s*(```|~~~)", s):
            flush()
            in_code = not in_code
            continue
        if in_code or re.match(r"^( {4,}|\t)\S", line) and not buf:
            continue
        if not s.strip():
            flush()
            continue
        if re.match(r"^\s*\|", s) or re.match(r"^\s*[-=*_]{3,}\s*$", s) or re.match(r"^\s*<[^>]+>\s*$", s):
            flush()
            if re.match(r"^\s*\|", s) and not re.match(r"^\s*\|[\s:|-]+\|\s*$", s):
                for cell in s.strip().strip("|").split("|"):
                    if len(cell.split()) > 3:
                        blocks.append(Block("cell", i, cell.strip()))
            continue
        m = re.match(r"^\s*#{1,6}\s+(.*)$", s)
        if m:
            flush()
            blocks.append(Block("heading", i, m.group(1)))
            continue
        if SAFETY_RE.match(s):
            flush()
            buf, buf_line, buf_kind = [SAFETY_RE.sub("", s).strip(" *_:")], i, "safety"
            continue
        if NOTE_RE.match(s):
            flush()
            buf, buf_line, buf_kind = [NOTE_RE.sub("", s).strip(" *_:")], i, "note"
            continue
        m = re.match(r"^\s*(?:\d+[.)]|[a-z][.)]|\(\d+\)|\([a-z]\)|Step\s+\d+[.:])\s+(.*)$", s)
        if m:
            flush()
            buf, buf_line, buf_kind = [m.group(1)], i, "step"
            continue
        m = re.match(r"^\s*(?:[-*+•]|\[[ xX]\])\s+(.*)$", s)
        if m:
            flush()
            buf, buf_line, buf_kind = [m.group(1)], i, "bullet"
            continue
        s2 = re.sub(r"^\s*>\s?", "", s)
        if buf:
            buf.append(s2.strip())
        else:
            buf, buf_line, buf_kind = [s2.strip()], i, "para"
    flush()
    return blocks


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_sentence(sent, line, kind, mode, terms, out, seq=0):
    def add(rule, sev, msg, hit=""):
        out.append({"line": line, "seq": seq, "rule": rule, "severity": sev,
                    "message": msg, "match": hit, "sentence": sent})

    procedure = mode == "procedure" or (mode == "auto" and kind == "step")
    # Limits from the standard: rule 5.1 (procedure) and rule 6.3 (description).
    limit = 20 if procedure else 25
    n = count_words(sent)
    if kind != "heading" and n > limit:
        add("5.1" if procedure else "6.3", "error",
            f"Sentence has {n} words. The maximum is {limit} for "
            f"{'a procedure' if procedure else 'a description'}.")

    if ";" in sent:
        add("8.1", "error", "Do not use the semicolon. Make two sentences or a list.", ";")

    for m in CONTRACTION.finditer(sent):
        add("4.2", "error", "Do not use contractions.", m.group(0))

    for rx, msg in LATIN:
        for m in re.finditer(rx, sent, re.I if "N" not in rx else 0):
            add("GR-6", "error", msg, m.group(0))

    low = sent.lower()
    for rx, rule, sev, msg in PHRASES:
        for m in re.finditer(rx, low):
            add(rule, sev, msg, m.group(0).strip())

    for ph, sug in PHRASAL.items():
        a, *rest = ph.split()
        rx = r"\b" + a + r"(?:s|ed|ing)?\s+(?:(?!to\b)\w+\s+){0,2}?" + r"\s+".join(rest) + r"\b" \
            if len(rest) == 1 else r"\b" + ph.replace(" ", r"\s+") + r"\b"
        m = re.search(rx, low)
        if m and (len(m.group(0).split()) == len(ph.split()) or a in ("turn", "switch", "shut", "plug", "hook", "pick")):
            add("9.3", "warning", f'Phrasal verb "{ph}" -> {sug}', m.group(0))

    words = [(m.group(0), m.start()) for m in WORD.finditer(sent)]
    lows = [w.lower().replace("’", "'") for w, _ in words]

    seen = set()
    for idx, w in enumerate(lows):
        raw = words[idx][0]
        if w in terms or raw in ("CODE", "URL") or (raw.isupper() and len(raw) > 1):
            continue
        if w in MODALS:
            # "may" as month, "can" fine
            add("3.4", "error", f'"{raw}" is not approved -> {MODALS[w]}', raw)
            continue
        if w in BRITISH:
            add("1.14", "warning", f'Use American spelling: "{BRITISH[w]}"', raw)
        hit = next((c for c in lemma_candidates(w) if c in UNAPPROVED), None)
        if hit and hit not in seen and not any(c in terms for c in lemma_candidates(w)):
            # skip words covered by a phrase finding (need to, prior to, ...)
            nxt = lows[idx + 1] if idx + 1 < len(lows) else ""
            if (hit in ("need",) and nxt == "to") or (hit == "prior" and nxt == "to") \
               or (hit == "further" and w != "further"):
                continue
            if hit in ("check", "test"):
                # CHECK and TEST are approved nouns. Report only clear verb use:
                # an inflected verb form, the first word of a sentence, or a word
                # after "to", a modal, a pronoun, or a connecting word.
                prev = lows[idx - 1] if idx > 0 else ""
                verb_use = (w.endswith(("ed", "ing")) or idx == 0 or prev in (
                    "to", "and", "then", "must", "can", "you", "not", "always",
                    "never", "also", "please", "should", "will", "or", "but"))
                if not verb_use:
                    continue
            if hit == "about" and not (nxt[:1].isdigit() or re.search(r"\babout\s+\d", low)):
                continue
            seen.add(hit)
            sev = "info" if hit in SOFT else "error"
            add("1.1", sev, f'"{raw}" is not approved -> {UNAPPROVED[hit]}', raw)

        # verb constructions
        if w in HAVE and idx + 1 < len(lows):
            j = idx + 1
            if lows[j] in ("not", "never", "already", "just", "also", "now") and j + 1 < len(lows):
                j += 1
            if is_participle(lows[j]) and lows[j] not in ("need",):
                add("3.2", "error", "Perfect tense. Use the simple past or BE + adjective.",
                    f"{raw} {words[j][0]}")
        if w in BE and idx + 1 < len(lows):
            j = idx + 1
            while j < len(lows) and (lows[j] in ("not", "never", "also", "now", "then", "always",
                                                 "only", "still", "currently", "automatically")
                                     or lows[j].endswith("ly")) and j - idx < 3:
                j += 1
            if j < len(lows):
                t = lows[j]
                if t.endswith("ing") and len(t) > 4 and t not in ING_OK and t not in terms:
                    add("3.4", "error", "Progressive tense. Use the simple present or past.",
                        f"{raw} {words[j][0]}")
                elif is_participle(t) and t not in STATE_ADJ and t not in terms:
                    by = bool(re.search(r" by (?!means of)", low[words[j][1]:]))
                    add("3.6", "error" if (procedure or by) else "warning",
                        "Possible passive voice. Use the active voice"
                        + (" (the agent is given with 'by')." if by else
                           ". (Correct if the participle is an adjective of state, "
                           "or if the agent is unknown in a description.)"),
                        f"{raw} {words[j][0]}")

        if w.endswith("ing") and len(w) > 4 and w not in ING_OK and w not in terms \
                and "-" not in w and not (idx > 0 and lows[idx - 1] in BE):
            nxt = lows[idx + 1] if idx + 1 < len(lows) else ""
            add("3.5", "info" if idx > 0 and lows[idx - 1] in ("the", "a", "an") else "warning",
                'The "-ing" form is permitted only as a technical noun or in one. '
                'Rewrite (for example "before removing" -> "before you remove").', raw)

    # instruction-level checks
    if procedure and kind == "step" and words:
        first = lows[0]
        if first in ("you", "the", "user", "users", "operator", "it", "we", "please", "then", "next", "now", "once") \
                and not re.match(r"^(if|when|before|after|to|while|until)\b", low):
            if first in ("you", "we", "please") or re.search(r"\b(must|should|can|will|needs?)\b", low):
                add("5.3", "warning", "Write the instruction as a command (imperative).", words[0][0])
        cmds = re.findall(r"(?:,|\band\b|\bthen\b|\.)\s+(?:then\s+)?(\w+)\b", low)
        extra = [c for c in cmds if c in IMPERATIVE_HINT]
        if extra and lows[0] in IMPERATIVE_HINT | {"if", "when", "before", "after", "to"}:
            if re.search(r"\b(and|then)\s+(?:then\s+)?(" + "|".join(map(re.escape, extra)) + r")\b", low):
                add("5.2", "warning",
                    "Possibly more than one instruction in the sentence. Use one sentence for each "
                    "instruction, unless the actions occur at the same time.",
                    ", ".join(extra))
        if re.match(r"^(if|when|before|after|while|until|to)\b[^,]{8,}$", low) and len(lows) > 6:
            add("5.4", "info", "If the sentence starts with a condition or purpose, put a comma before the command.")

    if kind == "note" and words and lows[0] in IMPERATIVE_HINT | {"do", "never", "always", "make"}:
        add("5.5", "warning", "A note gives information only. Make this instruction a step.", words[0][0])

    if kind == "safety" and words:
        if re.match(r"^(care|caution|attention|extreme|it is|there is|be aware|note that|failure)\b", low):
            add("7.2", "warning", "Start the safety instruction with a clear command or condition.", words[0][0])

    if re.match(r"^this\s+(is|are|can|will|must|does|has|removes|shows|makes|lets|causes|prevents|occurs|means)\b", low):
        add("GR-4", "info", 'Use "this" with a noun ("This procedure ...").', "This")

    if re.search(r"\b(he|she|his|her|him|manpower|mankind|man-hours?|chairman|foreman)\b", low):
        add("GR-7", "info", "Use gender-neutral language.")


def check(raw, mode="auto", terms=()):
    terms = {t.lower() for t in terms}
    out = []
    seq = 0
    blocks = parse_blocks(raw)
    for i, b in enumerate(blocks):
        text = mask(b.text)
        sents = split_sentences(text)
        if b.kind == "para" and len(sents) > 6:  # rule 6.6: six sentences maximum
            out.append({"line": b.line, "rule": "6.6", "severity": "error",
                        "message": f"Paragraph has {len(sents)} sentences. The maximum is 6.",
                        "match": "", "sentence": sents[0]})
        if b.kind == "safety":
            # a warning must come before the step it applies to
            nxt = blocks[i + 1].kind if i + 1 < len(blocks) else None
            if nxt not in ("step", "safety", "note", "bullet", "para"):
                out.append({"line": b.line, "rule": "7.1", "severity": "info",
                            "message": "Make sure that this safety instruction is before the step it applies to.",
                            "match": "", "sentence": sents[0] if sents else ""})
        for s in sents:
            seq += 1
            check_sentence(s, b.line, b.kind, mode, terms, out, seq)
    out.sort(key=lambda f: (f["line"], f.get("seq", 0)))
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

RULE_TOPIC = {
    "1.1": "Unapproved word or phrase", "1.14": "Spelling (American English)",
    "3.2": "Verb tense (perfect)", "3.4": "Complex verb construction / modal verb",
    "3.5": "-ing form", "3.6": "Passive voice", "4.1": "Vague wording",
    "4.2": "Contraction", "5.1": "Procedure sentence longer than 20 words",
    "5.2": "More than one instruction in a sentence", "5.3": "Instruction not a command",
    "5.4": "Comma after condition", "5.5": "Instruction in a note",
    "6.3": "Descriptive sentence longer than 25 words", "6.6": "Paragraph longer than 6 sentences",
    "7.1": "Position of safety instruction", "7.2": "Start of safety instruction",
    "8.1": "Semicolon", "9.3": "Phrasal verb", "GR-1": 'Missing "that"',
    "GR-4": '"This" without a noun', "GR-6": "Latin abbreviation", "GR-7": "Inclusive language",
}


def main():
    ap = argparse.ArgumentParser(description="First-pass ASD-STE100 checker.")
    ap.add_argument("file")
    ap.add_argument("--type", choices=["auto", "procedure", "description"], default="auto")
    ap.add_argument("--terms", help="file with approved technical nouns/verbs, one per line")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    try:
        with open(a.file, encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError as e:
        sys.exit(f"Cannot read {a.file}: {e.strerror}. Give the path of a text or "
                 "Markdown file. Convert .docx or .pdf to text first.")
    if "\x00" in raw[:2000]:
        sys.exit(f"{a.file} is not a text file. Convert it to text or Markdown first.")
    terms = []
    if a.terms:
        try:
            with open(a.terms, encoding="utf-8") as f:
                terms = [t.strip() for t in f if t.strip() and not t.startswith("#")]
        except OSError as e:
            print(f"Cannot read the terms file {a.terms}: {e.strerror}. "
                  "The check continues without it.", file=sys.stderr)

    findings = check(raw, a.type, terms)
    by_sev = Counter(f["severity"] for f in findings)
    by_rule = Counter(f["rule"] for f in findings)

    if a.json:
        json.dump({"file": a.file, "summary": {"total": len(findings), **by_sev},
                   "by_rule": dict(by_rule), "findings": findings}, sys.stdout, indent=2)
        print()
    else:
        print(f"STE check: {a.file}")
        print(f"{len(findings)} findings: {by_sev.get('error', 0)} error, "
              f"{by_sev.get('warning', 0)} warning, {by_sev.get('info', 0)} info\n")
        if findings:
            print("By rule:")
            for r, c in sorted(by_rule.items(), key=lambda x: -x[1]):
                print(f"  {r:<5} {RULE_TOPIC.get(r, ''):<45} {c}")
            print()
        last = None
        for f in findings:
            if (f["line"], f["sentence"]) != last:
                print(f"line {f['line']}: {f['sentence'][:160]}")
                last = (f["line"], f["sentence"])
            hit = f" [{f['match']}]" if f["match"] else ""
            print(f"    {f['severity']:<7} {f['rule']:<5}{hit} {f['message']}")
        print("\nNot checked by this script: multi-word nouns (2.1), wrong meaning or part of "
              "speech (1.2, 1.3), missing articles (4.5), term consistency (1.11), "
              "one topic per paragraph (6.5). Read the text for these.")
    if a.strict and by_sev.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
