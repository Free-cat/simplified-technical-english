# Software and IT documentation

Read this file only for software or IT text (user guides, API and admin documents,
runbooks, DevOps procedures). STE started in aerospace, but it is used for software,
medical devices, and machinery. Use `term-overview.md` for the term list, with the
`software` domain: `python3 scripts/ste.py scan --domain software FILE`.

Each bullet cites the STE rule it rests on. Where the bullet is this skill's interpretation,
it says "interpretation" and gives the nearest rule as a "related rule". Neither is a
rule of the standard.

## Rules for software text

- **UI labels are quoted text (category 10).** Write them exactly as on the screen, in the user's markup: **Save**, `Settings > Security`. (Rules 1.5, 8.6.)
- **Software objects are technical nouns (category 19).** One name for one object, the name that the product uses. (Rules 1.5, 1.11.)
- **Software operations are technical verbs (TV category 2c)** when the verb names a specific operation that the reader does with a tool, and no approved verb gives the same instruction. (Rule 1.12.)
- **General verbs still follow the dictionary.** "Make sure that the service operates" (not "Verify the service is running"). "Use the `--force` flag" (not "Leverage"). (Rules 1.1, 1.12.)
- **Settings.** "Turn on" and "turn off" are not permitted. Write "Set <the setting> to ON / OFF", use the label of the control ("Select **Maintenance mode**"), or use "enable" / "disable" as technical verbs. (Rules 9.3, 1.12.)
- **Code, commands, paths, and log text are not prose.** Do not change them. Each code span counts as one word: interpretation (related rule 8.6).
- **Words to delete or replace:** *leverage, robust, seamless, simply, just, please, straightforward, feature-rich, in order to, as needed, if applicable*. "Please" is not approved: give the command directly. (Rule 1.1 for the unapproved words; rule 4.1 for the vague phrases, as related rule.)

## Typical conversions

| Source | STE | Rules |
|---|---|---|
| Navigate to the Deployments page and verify the rollout has completed. | 1. Go to the **Deployments** page. 2. Make sure that the status of the rollout is `Complete`. | 1.1, 5.2, 5.3 |
| Kill the stuck worker and bounce the service. | 1. Stop the worker that does not operate. 2. Start the service again. | 1.1, 1.12, 5.2 |
| SSH into the box and tail the logs. | 1. Connect to the server with SSH. 2. Monitor the log file with `tail -f`. | 1.5, 1.12, 8.6 |
| Whitelist the IP in prod. | Add the IP address to the allowlist of the production environment. | 1.1, 1.10 |
| The job should be re-triggered if it errors out. | If the job is not completed, start the job again. | 3.4, 5.4, 9.1 |
