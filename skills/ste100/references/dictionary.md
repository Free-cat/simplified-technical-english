# STE dictionary: working subset

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

| Do not use | Use | Example in STE |
|---|---|---|
| verify, ensure, confirm, ascertain | MAKE SURE | Make sure that the pressure is 30 psi. |
| check (v) | MAKE SURE; DO A CHECK; EXAMINE (CHECK is a noun) |  |
| validate | MAKE SURE; DO A CHECK |  |
| inspect | EXAMINE; DO AN INSPECTION | Examine the seal for damage. |
| test (v) | DO A TEST (TEST is a noun) | Do a leak test of the fuel line. |
| perform, conduct, execute, accomplish, carry out | DO | Do the functional test. |
| utilize, utilise, employ, leverage, make use of | USE | Use a soft cloth. |
| require, need (v) | BE NECESSARY; MUST | A second person is necessary for this task. |
| allow, permit | LET; CAN | Let the adhesive dry. |
| enable (v) | LET; CAN (ENABLE is a technical verb for user-interface settings) |  |
| obtain, acquire, retrieve | GET | Get the access code from the supervisor. |
| provide, furnish, deliver (v) | GIVE; SUPPLY | The pump supplies fuel to the engine. |
| insert, place (v), position (v), lay (v) | PUT | Put the washer on the bolt. |
| depress | PUSH | Push the RESET button. |
| press (v) | PUSH (PRESS is a technical verb for a key in computer text) | Push the RESET button. |
| rotate, spin | TURN | Turn the knob clockwise. |
| locate, discover, detect | FIND | Find the cause of the leak. |
| indicate, exhibit, reveal, display (v) | SHOW | The gauge shows the pressure. |
| observe, notice | SEE; MONITOR; OBEY (for rules) | If you see corrosion, replace the bracket. |
| view (v) | SEE; MONITOR | If you see corrosion, replace the bracket. |
| begin, commence, initiate, launch | START | Start the engine. |
| end (v), terminate, cease, halt, shut down | STOP | Stop the pump. |
| finish, finalize | COMPLETE | Complete the installation. |
| reduce, lessen, diminish | DECREASE | Decrease the pressure to 10 psi. |
| elevate, raise (v) | LIFT; INCREASE | Lift the cover. |
| alter, modify, amend, vary (v) | CHANGE; ADJUST | Change the filter. |
| maintain, retain | KEEP; HOLD | Keep the container closed. |
| preserve | KEEP | Keep the cables in the box until you use them. |
| fasten, affix | ATTACH; INSTALL | Attach the cable to the bracket. |
| secure (v), fix (v), mount (v) | ATTACH; INSTALL; SAFETY (verb: lock with wire) | Attach the cable to the bracket. |
| detach, unfasten, separate (v) | DISCONNECT; REMOVE | Disconnect the hose. |
| rectify | REPAIR; CORRECT | Repair the damaged insulation. |
| restore (v) | REPAIR; CORRECT; INSTALL AGAIN | Repair the damaged insulation. |
| substitute, exchange (v) | REPLACE | Replace the seal with a new seal. |
| swap | INTERCHANGE | Interchange cables 1 and 2. |
| toggle, switch (v) | SET | Set the switch to ON. |
| choose, pick (v) | SELECT | Select the applicable procedure. |
| determine, establish | FIND; CALCULATE; MAKE SURE | Calculate the total weight. |
| function (v), run (v) | OPERATE | The unit operates at 28 V. |
| work (v) | DO WORK (WORK is a noun) | Be careful when you do work near the tank. |
| damage (v) | CAUSE DAMAGE TO (DAMAGE is a noun) | Heat can cause damage to the seal. |
| harm (v), hurt (v) | CAUSE INJURY TO | The spray can cause injury to your eyes. |
| leak (v) | THERE IS A LEAK (LEAK is a noun) | If there is a leak, tighten the fitting. |
| fail (v) | BE UNSERVICEABLE (rewrite the sentence; FAILURE is a technical noun) | The pump is unserviceable. |
| comprise, consist of | HAVE; INCLUDE; CONTAIN | The kit contains four seals. |
| avoid | PREVENT; DO NOT | Do not touch the hot surface. |
| attempt | TRY | Try to move the lever. |
| repeat | DO ... AGAIN | Do steps 3 to 5 again. |
| exceed | BE MORE THAN | The temperature must not be more than 80 °C. |
| remain | STAY | Stay away from the air intake. |
| inform, notify, advise | TELL | Tell the supervisor. |
| proceed | CONTINUE; GO | Continue the procedure. |
| return (v) | PUT BACK; GO BACK | Put the tool back in the kit. |
| dispose, dispose of, throw away | DISCARD | Discard the used seal. |
| wipe (v), wash (v), rinse (v) | CLEAN | Clean the surface with a dry cloth. |
| handle (v) | MOVE; HOLD; TOUCH; BE CAREFUL WITH | Be careful when you move the unit. |

## 3. Unapproved modal and helping verbs

| Do not use | Use |
|---|---|
| should | MUST (for an obligation, or write the command); RECOMMEND (advice); IF (= if) |
| shall | MUST |
| ought | MUST |
| may | CAN (permission); POSSIBLY (possibility) |
| might | CAN; POSSIBLY |
| could | CAN |
| would | CAN; or rewrite in the simple present or simple future |
| has / have / had + participle | Simple past, or BE + adjective |
| is / are + -ing | Simple present |

## 4. Unapproved connecting words, prepositions, and phrases

| Do not use | Use |
|---|---|
| in order to, so as to | TO |
| prior to, previous to | BEFORE |
| subsequent to, following | AFTER |
| since, as | BECAUSE; BECAUSE OF |
| due to, owing to | BECAUSE OF |
| though, whereas, however | BUT |
| therefore, hence, consequently, thus far | AS A RESULT; THUS |
| in case, in the event that, provided that | IF |
| should | MUST (for an obligation, or write the command); RECOMMEND (advice); IF (= if) |
| whether | IF |
| upon, once | WHEN; AFTER |
| via, by means of | THROUGH; WITH |
| within | IN; LESS THAN (for time and quantity) |
| over | MORE THAN (for a quantity or a limit); ABOVE; ON; ALONG (for a position) |
| in excess of | MORE THAN |
| under, below | LESS THAN (for a quantity or a limit); BELOW; IN (for a position) |
| the following | THESE; THAT FOLLOW(S) |
| about | APPROXIMATELY (for a quantity); ABOUT is approved only for 'concerned with' |
| around, circa | APPROXIMATELY (for a quantity) |
| per | FOR EACH; REFER TO (for documents) |
| as well as, in addition to | AND; ALSO |
| e.g. | FOR EXAMPLE |
| i.e. | THAT IS |
| etc. | give the full list, or "and other ..." |
| prior | BEFORE |
| former | BEFORE; INITIAL |
| in accordance with, as per | REFER TO; OBEY |
| currently, presently, now, at this point | AT THIS TIME |
| till | UNTIL |
| whilst | WHILE |
| furthermore, moreover, additionally | ALSO |

## 5. Unapproved adjectives and adverbs

| Do not use | Use |
|---|---|
| appropriate, suitable | CORRECT; APPLICABLE |
| proper | CORRECT |
| right | CORRECT (RIGHT is approved as 'side') |
| properly | CORRECTLY |
| adequate, enough, ample | SUFFICIENT |
| essential, crucial | NECESSARY; IMPORTANT |
| vital | MANDATORY |
| critical | VERY IMPORTANT; CAREFUL (for 'a careful estimate') |
| big, huge, sizeable | LARGE |
| tiny, little, minor | SMALL |
| entire, whole | ALL; FULL |
| numerous | MANY |
| multiple | MANY; SOME |
| several | SOME |
| various | DIFFERENT |
| additional, extra, further | MORE; OTHER |
| main | PRIMARY (MAIN can be part of a technical name, for example 'main landing gear') |
| final, ultimate | LAST |
| close (adj) | NEAR; ADJACENT |
| nearby | NEAR |
| faulty | DEFECTIVE; UNSERVICEABLE |
| broken | DEFECTIVE; UNSERVICEABLE; DAMAGED |
| inoperative | OFF; DOES NOT OPERATE |
| functional, working, operative | SERVICEABLE; OPERATES CORRECTLY |
| visible | 'that you can see' |
| accessible | 'that you can get access to' |
| prone to, liable to | CAN; EASILY |
| gently, cautiously | CAREFULLY; LIGHTLY |
| rapidly, swiftly | QUICKLY |
| promptly | IMMEDIATELY |
| nearly | ALMOST |
| roughly | APPROXIMATELY |
| simply, basically | (delete the word) |
| just | IMMEDIATELY (time); ONLY ('Only apply light pressure'); or delete the word |
| difficult, hard | NOT EASY |
| acceptable | PERMITTED |
| please | (delete; give the command directly) |
| robust, seamless, seamlessly | (delete, or be specific) |
| and so on | give the full list |

## 6. Approved words with a part-of-speech trap

| Word | Approved as | Not approved as | Write |
|---|---|---|---|
| check | noun | verb | Do a check of / Make sure that |
| test | noun | verb | Do a test of |
| close | verb | adjective, adverb | near |
| clear | adjective ('clear of obstructions') | verb | Remove ...; Make sure that ... is clear |
| clean | verb, adjective | - | Clean the surface. The surface is clean. |
| damage | noun | verb | cause damage to |
| leak | noun | verb | There is a leak |
| work | noun | verb | do work |
| control | noun; verb (adjust, operate) | verb meaning 'check' | make sure / examine |
| follow | verb (come after) | verb meaning 'obey' | obey |
| hard | adjective (not easy to cut) | 'difficult' | not easy |
| about | preposition (concerned with) | 'approximately' | approximately |
| as | conjunction of comparison ('as ... as') | 'because', 'while' | because, while |
| since | conjunction for time ('since you mixed the compound') | 'because' | because |
| once | - | adverb, conjunction | one time; when |
| over | - | all uses | above, on, along (position); more than (quantity) |
| right | adjective (side) | 'correct' | correct |
| last | adjective (final) | verb | continue for |
| use | verb | noun in 'make use of' | use (verb) |
| need | - | verb | be necessary |
| help | verb | noun | Get medical aid. This helps to prevent corrosion. |
| aid | noun | verb | Get medical aid. |
| cool | adjective | verb | Let the unit become cool. |
| wear | verb (become damaged by friction) | 'wear clothing' | put on, use |
| see | verb (with the eyes) | 'see Table 2' | refer to |
| turn | verb (move around an axis) | 'turns green' | changes to green |
| activate | verb (make a function ready for operation) | - | start |
| deactivate | verb (make a function not ready for operation) | - | stop |
| warning | technical noun (safety signal word) | 'warn' as a verb | tell |
| caution | technical noun (safety signal word) | 'warn' as a verb | tell |
| function | noun | verb | operate |
| safety | noun; verb (lock with wire or a pin) | - | Safety the nut with lockwire. |
| monitor | verb | - | Monitor the pressure. |
| refer | verb, with TO | - | Refer to Figure 3. |

## 7. Core approved verbs

When a suitable verb does not come to mind, start here. All of these are approved:

ABSORB, ACCEPT, ACTIVATE, ADD, ADJUST, AGREE, ALIGN, APPLY, ASSEMBLE, ATTACH,
BALANCE, BE, BECOME, BEND, BLEED, BLOW, BREAK, CALCULATE, CALIBRATE, CAN,
CANCEL, CAUSE, CHANGE, CLEAN, CLOSE, COLLECT, COME, COMPARE, COMPLETE,
CONNECT, CONTAIN, CONTINUE, CONTROL, CORRECT, COUNT, CUT, DEACTIVATE,
DECREASE, DISASSEMBLE, DISCARD, DISCONNECT, DISENGAGE, DIVIDE, DO, DRAIN,
DRY, ENGAGE, ERASE, EXAMINE, EXTEND, EXTINGUISH, FALL, FEEL, FILL, FIND,
FLOW, FLUSH, FOLD, FOLLOW, GET, GIVE, GO, HAVE, HEAR, HELP, HOLD, IDENTIFY,
IGNORE, INCLUDE, INCREASE, INSTALL, INTERCHANGE, ISOLATE, KEEP, KNOW, LET,
LIFT, LISTEN, LOCK, LOOK, LOOSEN, LOWER, LUBRICATE, MAKE, MAKE SURE, MEASURE,
MIX, MONITOR, MOVE, MUST, OBEY, OCCUR, OPEN, OPERATE, PREPARE, PREVENT, PULL,
PUSH, PUT, PUT ON, READ, RECEIVE, RECOMMEND, RECORD, REFER, RELEASE, REMOVE,
REPAIR, REPLACE, RETRACT, SAFETY, SEAL, SEE, SELECT, SEND, SET, SHOW, START,
STAY, STOP, SUPPLY, TAG, TELL, TIGHTEN, TORQUE, TOUCH, TRY, TURN, UNLOCK,
USE, WAIT, WEAR, WEIGH, WRITE.

Two approved phrasal verbs have a restricted meaning: PUT ON (protective
clothing) and COME ON (a light). Do not make other phrasal verbs (rule 9.3).

## 8. Technical nouns and technical verbs

Words of the subject field (parts, tools, software objects, specific processes)
are not in the dictionary. They are permitted as technical nouns and technical
verbs if they fit a category. The categories, the rules, the words that look
technical but are general, and the guidance for software text are in
`term-overview.md` and `term-details.md`.
