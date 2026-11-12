# Technical nouns and technical verbs: overview

Read this file when you build the term list (Write, Check, Edit). The words of a
subject field are not in the dictionary. STE permits them as technical nouns (TN,
rules 1.5 to 1.11) and technical verbs (TV, rules 1.12 and 1.13), but only if they fit
a category. The categories were compared with Issue 9 (22 TN, 4 TV). Their scope,
examples, and usual errors are in `term-details.md`; open a category there only when
its line below does not decide the word.

## Decide the word once, with the lookup script

Do not reason about each term from memory. Run the script:

1. Pick the domain once from the document: `software` (software, IT, DevOps),
   `mechanical` (machinery, equipment, maintenance), or none (general text).
2. Run `python3 scripts/ste.py scan --domain DOMAIN FILE`. It lists the words that no
   layer knows. Known words (general list, term pack, project terms) are not listed.
3. Decide only the words in the unknown list. Plain everyday English ("open", "pump" in a
   sentence about a pump) needs no entry; a subject-field word is decided by the procedure below.
4. Record each accepted term (see "The term list") and run `scan` again.

If the document has no subject-field words, skip this file.

## Decision procedure (for a word that the lookup does not know)

1. **Is there an approved word that gives the same information?** Use it. "If you
   find damaged wires" is correct; "If you detect damaged wires" is not.
2. **Is it a name?** Does it name a thing, a person, a place, a quantity, a condition,
   or a document of the subject field? Find a TN category below. If one fits, it is a TN.
3. **Is it a specific process?** Does the verb name an operation with a defined method
   and result in the field (*bond*, *rivet*, *reboot*)? Find a TV category below.
4. **If nothing fits, it is a general word.** Rewrite with approved words (rule 9.1).
   Put the word in the open questions only when no rewrite is possible.

Tests: a glossary of the field has an entry with one definition ("torque", "gasket":
yes; "functionality", "solution": no). A noun for a part or a material does not become a
verb ("Apply grease to the fasteners", not "Grease the fasteners").

## Technical noun categories (rule 1.5)

1. Official parts information: a name from the parts catalog or the product documentation (*stud, seal ring, billing service*).
2. Vehicles, machines, and locations on them: the machine and each named place on it (*aircraft, left wing, port 2*).
3. Tools and support equipment, and their parts: *socket wrench, debugger, package manager*.
4. Materials, consumables, and unwanted material: *primer, coolant, cable tie*; *rust, sludge*.
5. Facilities, infrastructure, and logistics: *workshop, data center, storage, shipping*.
6. Systems, components, circuits, and their functions: *hydraulic system, load balancer, read replica*.
7. Mathematical, scientific, and engineering terms, and formulas: *resistance, latency, checksum*.
8. Navigation and geographic terms: *bearing, elevation, UTC, time zone*.
9. Numbers, units, times, and their symbols: *25, psi, Nm, ms, version 2.4.1*.
10. Quoted text: placards, labels, UI labels (**Save**), messages, log lines. Keep them exactly.
11. Roles, persons, groups, organizations, countries: *technician, operator, on-call engineer, vendor*.
12. Parts of the body: *forearm, ear, knee*.
13. Personal effects, food, and beverages: *goggles, apron, tea*.
14. Medical terms: *headache, asthma, rash* (usually in warnings).
15. Official documents and parts of documentation: *manual, checklist, table, figure, runbook, pull request*. Also WARNING, CAUTION, NOTE.
16. Environmental and operational conditions: *fog, frost, peak load, outage, timeout*.
17. Colors: *blue, dark gray, light blue*; comparatives are not permitted.
18. Damage terms: *pitting, galling, memory leak, data loss*.
19. Computer science and ICT: hardware, software objects, data, network and security terms, UI elements (*repository, firewall, token, toolbar*).
20. Civil and military operations: *mission, patrol, deployment, lifecycle, support queue*.
21. Law and regulations: *contract, compliance, warranty, license agreement*.
22. Animals, plants, and other life forms: *rodent, mold, algae*.

## Technical verb categories (rule 1.12)

1. Manufacturing processes: remove, add, or attach material, change strength or shape or surface (*saw, bore, rivet, bond, anodize, forge*).
2. Computer processes: a) input and output (*scan, transmit*); b) user interface and applications (*rename, expand, bookmark*); c) system operations (*compile, deploy, mount, roll back, log in*).
3. Instructions for applicable subject fields: a) engineering and science; b) medical; c) civil and military operations; d) navigation; e) automotive and railway; f) energy, oil, and gas (for example *refuel, dock, idle, flare*).
4. Law and regulations: only in legal texts (*indemnify, ratify, certify*). Never in a procedure.

## Rules for terms

- An approved verb comes first (rule 1.12). "Go to the **Settings** page" beats "Navigate to".
- One name for one thing in the whole document (rule 1.11). Use the name that the product or the company uses.
- A multi-word term has at most three words (rule 2.1). Write a longer official name in full once, then a short form (rule 2.2).
- Do not use a TN as a verb (rule 1.7) and do not use a TV as a noun (rule 1.13).
- Choose one form of a verb for one action and keep it ("deploy" everywhere, not "deploy" and "do the deployment"). (Rules 1.11, 1.7.)
- Jargon and short forms are not terms: "prod", "creds", "repo" (rule 1.10). Write "production environment", "credentials", "repository".
- An unapproved word inside a real name is permitted (rule 1.6): "main landing gear" is a name, "primary landing gear" is not.

## The term list

Keep one line for each technical word that you use, in this format:

```
term | TN or TV | category | std or ext; note
```

- `std` = the word is in the standard's example list for that category; `ext` = added by the same principle. Use `ext` for words that you add yourself. (Rules 1.5, 1.12.)
- A word that is in a domain pack is already recorded there: do not repeat it. (Rule 1.11: one name for one item.)
- The author confirms the words that are not in a domain pack. Give the author only those words, with the reason in one line each. (Rule 1.8: the subject field decides which nouns are accepted.)
- Record accepted terms in one command, or in the candidates file (see SKILL.md). (Rules 1.5, 1.8.)
