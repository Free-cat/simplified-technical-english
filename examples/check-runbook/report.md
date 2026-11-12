# STE report: deploy-runbook.md

## Summary

The file is a mixed text: an overview (description), a numbered procedure, one warning, one note, and a rollback section. The general STE level is low. Most findings are unapproved words (should, may, ensure, verify, utilizing, via), perfect and progressive verb forms, contractions, and steps that contain more than one action. Correct these first: (1) split the multi-action procedure steps, and write each step as one command; (2) change the rollback warning to CAUTION (this skill reads loss of data as damage; confirm this with your own standard), and move it before the rollback step; (3) turn the note that contains an instruction into a step, and replace should, may, and has to with MUST or CAN after you confirm the intended strength. This check used a working subset of the ASD-STE100 dictionary, so confirm the word choices against the official dictionary.

| Rule | Topic | Findings |
|---|---|---|
| 1.1 | Unapproved word or phrase | 12 |
| 1.10 | Regional word | 1 |
| 2.1 | Multi-word noun of more than three words | 1 |
| 3.2 | Perfect tense | 3 |
| 3.4 | Modal verb or complex verb construction | 6 |
| 3.5 | -ing form | 4 |
| 3.6 | Passive voice | 5 |
| 4.2 | Contraction | 2 |
| 5.1 | Procedure sentence longer than 20 words | 1 |
| 5.2 | More than one instruction in a sentence | 2 |
| 5.3 | Instruction not in command form | 2 |
| 5.5 | Instruction in a note | 1 |
| 6.3 | Description sentence longer than 25 words | 1 |
| 7.1 | Safety level does not match the risk | 1 |
| 7.2 | Safety instruction does not start with a command or condition | 1 |
| 8.1 | Semicolon | 1 |
| 9.3 | Phrasal verb | 1 |
| GR-1 | "that" missing after MAKE SURE | 1 |
| GR-6 | Latin abbreviation | 2 |

## Findings

| # | Location | Rule | Original text | Problem | Suggested STE text |
|---|---|---|---|---|---|
| 1 | Overview, sentence 1 | 3.4 | "This runbook describes how the payment service should be deployed to production." | "should" is not approved. | "This runbook describes how to deploy the payment service to production." |
| 2 | Overview, sentence 2 | 6.3, 8.1, 1.1, GR-6, 3.2, 3.4 | "The service has been running on the new cluster since March; it consists of three components, i.e. the API gateway, the worker pool and the ledger database, which are deployed independently and which must be upgraded in a specific order in order to avoid data inconsistencies between the ledger and the workers." | 52 words (description maximum is 25). Semicolon not allowed. "has been running" is a perfect progressive. "consists of", "since", "i.e.", and "in order to" are not approved. | "The service operates on the new cluster from March. The service has three components: the API gateway, the worker pool, and the ledger database. Each component is deployed independently. The components must be upgraded in a specific order. This order prevents data inconsistencies between the ledger and the workers." |
| 3 | Overview, sentence 3 | 3.4, 3.6 | "Deployments may only be carried out by on-call engineers." | "may" is not approved. Passive voice with a named agent in a requirement. Also, the overview paragraph would have more than six sentences after the fixes (6.6). | Start a new paragraph here. Then: "Only on-call engineers can deploy the payment service." |
| 4 | Overview, sentence 4 | 4.2, 1.1, 1.10 | "If you aren't on the on-call rota, don't proceed." | Two contractions. "proceed" is not approved (CONTINUE, GO). "rota" is a regional word for a schedule. | "If you are not on the on-call schedule, do not continue." |
| 5 | Procedure, step 1 | 5.2, 1.1, 3.2, 3.5 | "Prior to commencing the deployment, verify that all CI checks have passed and ensure the release tag is correct." | Two instructions in one sentence (5.2). "prior to" (use BEFORE), "commencing" (use START), "verify" and "ensure" (use MAKE SURE), "have passed" (perfect tense), -ing form. | Step 1 (a): "Before you deploy, make sure that all CI checks pass." Step 1 (b): "Make sure that the release tag is correct." |
| 6 | Procedure, step 2 | 3.4, 1.1, 3.6, 5.3 | "The maintenance banner should be enabled by the operator via the admin console." | "should" is not approved (MUST or RECOMMEND, see open question 1). "enabled" is not approved; use SET to on. "via" is not approved (use WITH or THROUGH). Passive voice in a procedure step. Not a command. | "The operator must use the admin console to set the maintenance banner to on." |
| 7 | Procedure, step 3 | 5.1, 5.2, 3.2, 1.1 | "Run `./scripts/drain.sh payments` and wait until the queue depth has dropped below 100, then scale the worker pool down to zero and take a database snapshot." | 25 words (procedure maximum is 20). Four instructions in one sentence (5.2). "has dropped" is a perfect tense. "wait" is not approved. "below" is not approved for a quantity (use LESS THAN). "take" is not approved (use MAKE). | Split into four sub-steps. (a) "Run `./scripts/drain.sh payments`." (b) "Do not continue until the queue depth is less than 100." (c) "Scale the worker pool down to zero." (d) "Make a database snapshot." |
| 8 | Procedure, step 4 | 1.1, 3.5 | "Deploy the ledger migration utilizing the `migrate` job." | "utilizing" is not approved (use USE, or WITH for a tool). -ing form. | "Deploy the ledger migration with the `migrate` job." |
| 9 | Procedure, step 5 | 1.1 | "Check the migration logs for errors." | "Check" is a noun in STE. As a verb, use EXAMINE or MAKE SURE. | "Examine the migration logs for errors." |
| 10 | Procedure, step 6 | 1.1, 3.6, 5.3 | "Once the migration is finished, the API gateway and workers can be deployed." | "Once" is not approved (use AFTER or WHEN). "finished" is not approved (use COMPLETE). Passive voice in a procedure. Not a command. | "After you complete the migration, deploy the API gateway and the workers." |
| 11 | Procedure, step 7 | 9.3 | "Turn off the maintenance banner." | "Turn off" is a phrasal verb. Write the setting and its state. | "Set the maintenance banner to off." |
| 12 | Procedure, after step 7 (warning) | 7.1, 7.2, 3.4, 3.6, 3.5, 1.1 | "WARNING: Extreme care should be exercised when running the rollback script, as it will drop the new ledger tables." | Level: the risk is loss of data. This skill reads that as damage, so the level is CAUTION, not WARNING (confirm with your standard). Does not start with a command or condition. "should" (use MUST), passive, -ing form, and "as" (use BECAUSE). Position: the warning is after step 7, but no procedure step runs the rollback script. Move it into the Rollback section, before the step that runs the script. | "CAUTION: BE CAREFUL WHEN YOU RUN THE ROLLBACK SCRIPT. IT WILL DELETE THE NEW LEDGER TABLES." |
| 13 | Procedure, note | 5.5, 1.1, GR-1 | "Note: Make sure you notify the #payments channel after the deployment." | An instruction in a note (5.5). "notify" is not approved (use TELL or SEND). "Make sure" needs "that" (GR-1). | Make this a step after step 7: "After the deployment, send a message to the #payments channel." |
| 14 | Rollback, sentences 1 and 2 | 4.2, 1.1, 3.5, GR-6 | "Rollback is usually straightforward. It's performed by re-deploying the previous release tag, etc." | "straightforward" is a word to delete (references/software-text.md). Contraction "It's". "performed" is not approved (use DO). -ing form. "etc." (give the full list). | "Usually, to roll back, deploy the previous release tag again. Then, do these other rollback steps: [list the steps]." |
| 15 | Rollback, sentence 3 | 2.1, 1.1, 3.4, 3.6 | "The payment service production cluster ledger database migration rollback job has to be triggered manually." | Nine words in one noun group (2.1 allows three). "has to" is not approved (use MUST). Passive voice. | "In the production cluster of the payment service, start the migration rollback job of the ledger database manually." |

## Open questions

1. Step 2: Is the banner step required (MUST) or only advised (RECOMMEND)? The source says "should". The suggested text uses MUST.
2. Rollback: Which step runs the rollback script? The CAUTION must go before that step, and the source does not name it.
3. Rollback: Which steps does "etc." stand for?
4. Overview and steps 3 and 6: Are "workers" and "worker pool" the same thing? The text uses both. The suggested text uses "the workers" in step 6.
