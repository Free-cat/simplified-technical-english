# Technical nouns and verbs: category details

Open this file only for a specific word or category in doubt. The one-line summaries
are in `term-overview.md`. The examples and the scope notes are our own. "Software"
marks an interpretation for software text.

## Contents

1. Technical noun categories 1–22: scope, examples, usual error
2. Rules for technical nouns
3. Technical verb categories 1–4: examples
4. Rules for technical verbs
5. Words that are not technical nouns or verbs
6. One word, two statuses (generated table)

---

## 1. Technical noun categories

**1. Official parts information.** Scope: names in the illustrated parts catalog, the bill of materials, or the drawing. Examples: *stud, seal ring, hinge pin, fuse, spacer*. Software: *billing service, ingest worker, admin console*. Usual error: a second name for one part. If the catalog says "retaining ring", do not write "circlip".

**2. Vehicles, machines, and locations on them.** Scope: the machine and each named place on it. Examples: *aircraft, forklift, cockpit, engine bay, left wing, slot 3*. Software: *laptop, rack, printer, port 2*. Usual error: a vague location ("the back part"). Name the location.

**3. Tools and support equipment, their parts, and locations on them.** Examples: *socket wrench, crimping tool, bench vise, hoist*. Software: *debugger, terminal, package manager, load generator* (use the vendor's product name). Usual error: the tool name as a verb ("wrench the nut").

**4. Materials, consumables, and unwanted material.** Examples: *primer, thread compound, desiccant, coolant*; unwanted: *rust, sludge, grit, condensation*. Software: hardware consumables only (*thermal paste, cable tie, toner*). Usual error: the material as a verb ("Grease the bearing" → "Apply grease to the bearing").

**5. Facilities, infrastructure, and logistic procedures.** Examples: *hangar, workshop, airport, storage, packaging, shipping*. Software: *data center, server room, availability zone, region*. Usual error: local names that a reader elsewhere does not know ("the cage", "the pit").

**6. Systems, components and circuits, their functions, configurations, and parts.** Examples: *hydraulic system, fuel pump, relay, control loop, standby mode*. Software: *authentication service, load balancer, message queue, failover, read replica*. Usual error: a long noun cluster. Split it with "of" (rule 2.1).

**7. Mathematical, scientific, and engineering terms, and formulas.** Examples: *resistance, frequency, density, capacitance*. Software: *latency, throughput, percentile, checksum, hash, bit rate*. A formula is quoted text and counts as one word. Usual error: a term in a loose sense ("the latency of the team").

**8. Navigation and geographic terms.** Examples: *east, meridian, bearing, elevation*. Software: *time zone, UTC, country and city names*. Usual error: a direction word for a screen position when the UI has a name for the area.

**9. Numbers, units of measurement and time, and their symbols.** Examples: *25, psi, mm, Nm, second, 14:00*. Software: *ms, GB, requests per second, version 2.4.1*. Usual error: a number without its unit, or a mix of unit systems.

**10. Quoted text.** Scope: text that you cannot change: placards, labels, markings, display text. Examples: "LOW PRESSURE", the START button. Software: UI labels (**Save**, `Settings > Security`), error messages, status values (`Running`), log lines, command output. Usual error: changing the quoted text to make it STE. Keep it exactly as it is; it may contain unapproved words.

**11. Professional roles, persons, groups, organizations, and geopolitical entities.** Examples: *technician, operator, inspector, crew, supervisor, the manufacturer*. Software: *administrator, on-call engineer, reviewer, customer, vendor*. Usual error: two role names for one person ("user", then "customer", then "client").

**12. Parts of the body.** Examples: *forearm, ear, knee, toe*. Usually in safety instructions.

**13. Common personal effects, food, and beverages.** Examples: *goggles, apron, bottled water, tea*.

**14. Medical terms.** Examples: *headache, asthma, fainting, rash*. Usual error: a risk that is not specific ("can be harmful"). Name the injury (rule 7.3).

**15. Official documents, parts of documentation, standards, and guidelines.** Scope includes the words *warning, caution, note, table, figure, page, paragraph, section*. Examples: *maintenance manual, checklist, service bulletin, logbook, figure, step, appendix*. Software: *runbook, release notes, changelog, ticket, pull request*. Usual error: a short informal name ("the doc", "the wiki") when the document has a title.

**16. Environmental and operational conditions.** Examples: *fog, hail, frost, heat wave, dusk*. Software: *peak load, outage, maintenance window, timeout* (interpretation). Usual error: a condition without its value when the value is known ("high temperature" → "a temperature of more than 60 °C").

**17. Colors.** Examples: *blue, white, orange, dark gray, light blue*. Comparative forms ("redder") are not permitted. Usual error: color as the only identification; give the label too ("the green START button").

**18. Damage terms.** Examples: *pitting, fretting, galling, warping, bulge*. Software: *data corruption, memory leak, data loss*. Usual error: the damage term as a verb ("The pipe cracked" → "The pipe has a crack").

**19. Computer science, information and communication technology.** Hardware: *switch, memory module, scanner*. Software objects: *repository, branch, container, endpoint, queue, dashboard, snapshot, pipeline, release tag, cluster, node*. Data: *index, schema, log entry*. Network and security: *firewall, port, proxy, token, password, API key, certificate, role*. UI elements: *icon, toolbar, list box, scroll bar*. Usual error: jargon and short forms ("prod", "the box", "creds", "repo").

**20. Civil and military operations.** Examples: *mission, patrol, evacuation, checkpoint, contractor, customer support, end user, deployment, lifecycle*. Software: *support queue, on-call rotation*; *rollout* as a noun.

**21. Law and regulations.** Scope: terms of legal and regulatory texts. Examples: *contract, compliance, jurisdiction, waiver, signature, scope, term*. Software: *license agreement, terms of service, data processing agreement* (interpretation).

**22. Animals, plants, and other life forms.** Examples: *rodent, mold, algae, lichen, shrub*.

## 2. Rules for technical nouns

| Rule | What to do | Example |
|---|---|---|
| 1.8 | Use the name that the company, the industry, or the product gives. | The UI says **Workspace**: do not write "project space". |
| 1.9 | If you must select a name, select a short and clear one. | "drain valve", not "fluid evacuation valve" |
| 1.10 | No slang, jargon, or regional words. | "the production environment", not "prod" |
| 1.11 | One name for one thing in the full document. | "access panel" always, not "cover" later |
| 1.7 | Do not use a TN as a verb. | "Send the report by email", not "Email the report" |
| 2.1 | Three words maximum in a multi-word noun. | "the filter of the fuel pump" |
| 2.2 | For a long official name, write it in full, then use a short name. | "release approval checklist (the checklist)" |
| 4.5 | Keep the article. | "Open the dashboard", not "Open dashboard" |

- **Abbreviations.** Write the full name with the abbreviation at first use: "continuous integration (CI)". Then use the abbreviation. (Rule 1.1: an abbreviation is not an approved word.)
- **Capitals.** A label keeps its capitals (the START button). A common noun does not get a capital. (Rules 1.5, 8.6: a label is one word.)
- **A name the reader may not know.** Give a short definition at first use, or put the term in a glossary. (Rules 1.9, 1.10.)
- **Unapproved words in names** are permitted (rule 1.6) when the name is real: "main menu", "backup file". The rule applies to the name, not to the word alone.

## 3. Technical verb categories

1. **Manufacturing processes.** a) remove material: *saw, bore, hone, sand*; b) add material: *laminate, coat*; c) attach material: *rivet, bond, pin*; d) change strength, structure or physical properties: *temper, harden, nitride*; e) change the surface finish: *anodize, galvanize*; f) change the shape: *forge, swage, roll*.
2. **Computer processes and applications.** a) input and output: *scan, dictate, transmit*; b) user interface and applications: *rename, expand, collapse, bookmark*; c) system operations: *partition, compile, mount, rebuild*. Software (interpretation): *compile, build, deploy, commit, merge, roll back, migrate, provision, scale, restore, mount, log in, log out, back up, run* (a script or a command).
3. **Instructions for applicable subject fields.** a) engineering, mathematics, science: *amplify, sample, oxidize*; b) medical: *intubate, suture, irrigate*; c) civil and military operations: *refuel, dispatch, evacuate*; d) navigation: *climb, hover, dock*; e) automotive and railway: *idle, tow, reverse*; f) energy, oil, and gas: *flare, refine, degas*.
4. **Law and regulations.** Only for legal and regulatory texts: *indemnify, ratify, certify*.

## 4. Rules for technical verbs

- **An approved verb comes first (1.12).** "Go to the **Settings** page" is better than "Navigate to the **Settings** page".
- **The verb names the process, not a general action.** "Crimp the terminal" is correct; "Process the terminal" is not. (Rule 1.12.)
- **The context decides.** "Enter your password" is correct (input). "Do not enter the test area" is not: write "Do not go into the test area". (Rules 1.2, 1.3.)
- **A TV is not a noun (1.13).** "Give the panel a sand" → "Sand the panel." The past participle as an adjective is permitted ("the sanded panel").
- **A word can be a TN and a TV** (*drill, plate, download, backup / back up*). Each use must fit its category. (Rules 1.5, 1.7, 1.12, 1.13.)
- **Spelling of two-word verbs.** The verb has two words; the noun has one: *log in / login, back up / backup, roll back / rollback*. (Rules 9.3, 1.11.)
- **Phrasal verbs (9.3).** Do not make a new phrasal verb from approved words ("put out", "carry out"). A term of the field such as *log in* or *take off* is a TV.
- **The verb rules of section 3 apply to TVs.** "Deploy the service", "the deployed version". Not "is deploying", not "has deployed".

## 5. Words that are not technical nouns or verbs

These words look technical. In the general sense they fit no category.

| Not a TN or TV | Why | Write | Rule |
|---|---|---|---|
| functionality, capability, feature set | no one thing to point to | Name the function: "the export function" | 1.5 |
| solution, approach, methodology, mechanism | abstract | Say what it is: "the procedure", "the script" | 1.5 |
| verify, ensure, confirm, check (v) | general | "Make sure that…" / "Do a check of…" | 1.1 |
| perform, execute, carry out, conduct | general | "Do…", or the specific verb | 1.1 |
| utilize, leverage, employ | general | "Use" | 1.1 |
| implement, handle, address | no defined method | The specific action: "install", "correct", "send" | 1.1 |
| launch, initiate | general | "Start" | 1.1 |
| terminate, kill (a process) | general | "Stop" | 1.1 |
| restart | not approved | "Start … again", or "reboot" for a computer | 1.1 |
| modify | general | "Change" | 1.1 |
| display, indicate | general | "Show" | 1.1 |
| create | not approved | "Make" | 1.1 |
| machine (v), process (v) in a manufacturing step | too general | The specific process: "bore", "hone" | 1.12 |
| robust, seamless, powerful, intuitive | marketing | Delete, or give the fact with a value | 1.1 |

If a word in this table is the text of a command or a button, quote it (category 10) and keep the prose verb approved: "Select **Create**."

## 6. One word, two statuses

Some words are not approved in the general sense, and are technical in a specific
sense. The sense decides. The table is generated from `assets/words/two-statuses.txt`.
If you are not sure which sense the source has, it is an open question for the author.

<!-- generated:two-statuses:begin (tests/build_references.py) -->
| Word | General sense (not approved) | Specific sense (permitted) |
|---|---|---|
| enter | not approved in the sense 'go into'; write 'go into' | technical verb for input ('Enter your password.') |
| press | not approved; write 'push' | technical verb for a key ('Press Enter.') |
| enable | not approved in the general sense; write LET or CAN | technical verb for a user-interface setting ('Enable the option.') |
| disable | not approved in the general sense | technical verb for a user-interface setting ('Disable the option.') |
| validate | not approved; write 'make sure that ... is correct' | technical verb for an application function ('Validate the form.') |
| navigate | not approved; write 'go' | technical verb for the user interface ('Navigate to the page.'); 'Go to the page' is better |
| delete | not approved in the general sense; write 'remove' or 'discard' | technical verb for a record ('Delete the record.') |
| save | not approved in the sense 'keep'; write 'keep' | technical verb for a file ('Save the file.') |
| detect | not approved; write 'find' | technical verb for an equipment function ('The scanner detects metal objects.') |
| load | not approved in the sense 'install'; write 'install' | technical verb for a system operation ('Load the configuration.') |
| deploy | approved only in the sense 'move a part out of its stowed position' | technical verb for software ('Deploy the release.') |
| run | not approved in the sense 'operate'; write 'operate' | technical verb for a script or a command ('Run the script.') |
| restore | not approved in the sense 'put back'; write 'install again' | technical verb for a system operation ('Restore the database from the backup.') |
| check | not approved as a verb; write 'make sure' or 'do a check of' | part of a name ('check valve'); CHECK as a noun is approved |
| test | not approved as a verb; write 'do a test of' | part of a technical noun ('test rig') |
| close | not approved as an adjective or adverb; write 'near' | approved verb ('Close the valve.') |
| main | not approved; write 'primary' | only in a name ('main landing gear', 'main menu') |
| backup | not approved in the general sense ('a person as backup') | IT term ('backup file') |
| oil | not permitted as a verb; write 'apply oil to' | technical noun |
| grease | not permitted as a verb; write 'apply grease to' | technical noun |
| clamp | not permitted as a verb; write 'put a clamp on' | technical noun |
| wire | not permitted as a verb | technical noun |
<!-- generated:two-statuses:end -->
