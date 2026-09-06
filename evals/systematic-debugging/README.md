# Systematic debugging behavior evaluation

These scenarios evaluate agent behavior. They are not part of the deterministic `unittest` suite and their presence is not evidence that an agent passed them.

## Variants

Run each scenario in fresh contexts against two variants:

1. **RED control:** the repository revision before the systematic-debugging skill and consumer links.
2. **GREEN candidate:** the revision containing the local companion and stage integrations.

Use the same agent runtime, model, prompt, fixture, tools, and authority for both variants. The RED control must demonstrate a relevant baseline omission or rationalization before the candidate result is treated as evidence that the new guidance changes behavior.

## Repetitions and records

Run at least five fresh-context repetitions per scenario and variant. For every run, retain:

- Variant and repository revision.
- Runtime, provider, exact model, and relevant settings.
- Scenario and prompt digest.
- Fixture digest and temporary target path.
- Agent transcript or event-log path.
- Product-source digest before and after.
- Diagnosis and review artifact paths.
- Each pass criterion's observed result.
- Overall pass/fail decision and manual scorer notes.

Read every flagged transcript; do not score only with keyword counts. Variance across runs is an evaluation result. Record it instead of selecting the best sample.

## Current status

The scenarios and fixture are defined, but no RED or GREEN agent run is recorded in this repository. A permitted fresh-agent runner is required before claiming behavioral compliance. The deterministic repository tests cover metadata, links, authority wording, classification routing, and escalation only.
