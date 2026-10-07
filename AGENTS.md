# Recurring Posts Skill repository instructions

This package is an autonomous portable GamerHQ Skill.

## Repository ownership

Repository: `Duy-Phan96/gamerhq-skill-recurring-posts`

This project owns:

- Recurring Posts code and architecture;
- roadmap, issues, branches and pull requests;
- tests and CI;
- package versioning and independent Skill releases;
- Skill documentation;
- stable Skill/runtime identities owned by this package;
- `posts.v1` compatibility;
- Recurring Posts Management APIs;
- `recurring-post.execute.v1` handler and `post:<post-id>` job semantics;
- `recurring-post.sent.v1` event behavior.

This project does **not** own:

- `Duy-Phan96/GamerHQ` Host code or release workflow;
- `gamerhq-web`;
- public Runtime/SDK implementation;
- another `gamerhq-skill-*` repository;
- production infrastructure, VPS state, secrets or deployment decisions.

External public contracts consumed:

- GamerHQ Skill Runtime API `1`;
- public `skill_runtime` lifecycle, capability, storage, scheduler, event,
  Discord-port, Management API and Management UI Schema contracts.

Other repositories currently required:

- an available compatible public GamerHQ Skill Runtime/SDK distribution;
- no other repository is required for this package's local implementation,
  tests or independent release.

Outstanding handoffs:

- none blocking the current Skill release.
- A future generic arbitrary collection-item action contract would improve
  portable rendering of actions such as `test-send`; until then the Skill
  exposes that action through its public `describe.v1` metadata and
  `quickActions`.

Use this ownership statement as a guardrail for all work in this repository.

## Hard rules

- Keep Skill ID `recurring-posts` stable.
- Do not import Discord.py or GamerHQ bot/cogs/services/database/hosts/config.
- Do not import another Skill's private implementation.
- Use only public `skill_runtime` contracts.
- Keep configuration behind versioned Management APIs.
- Use Skill Storage and the shared Scheduler.
- Keep tests offline and token-free.
- Preserve `posts.v1`, scheduler job keys and handler IDs across compatible releases.
- Do not read or modify another repository through this project.
- Read-only inspection of another public repository is allowed only to understand
  released/public contracts, metadata, immutable commits and compatibility.
- If another repository must change, stop at a handoff. Do not create a branch,
  commit or PR there from this project.

## Handoffs

When this Skill needs a Host/SDK/web/other-Skill change:

1. finish everything possible here;
2. identify the exact missing public contract or behavior;
3. document the blocker;
4. provide a handoff prompt to the user;
5. let the repository that owns the target decide its implementation.

Use this format:

```text
HANDOFF REQUIRED

FROM REPOSITORY:
Duy-Phan96/gamerhq-skill-recurring-posts

TARGET REPOSITORY:
<target repository>

PROBLEM:
<what cannot be completed using the current public contract>

WHY THIS BELONGS TO THE TARGET:
<ownership / architecture reason>

REQUESTED OUTCOME:
<required public behavior or contract>

CURRENT CONTRACT / VERSION:
<Runtime API / SDK / package / Management API>

ACCEPTANCE CRITERIA:
- ...

COMPATIBILITY / MIGRATION CONSTRAINTS:
- ...

SECURITY / CAPABILITY IMPACT:
- ...

NON-GOALS:
- ...

SOURCE PROJECT STATUS:
<what is already complete here and what remains blocked>

WHEN COMPLETE:
<released version / immutable commit / API this Skill should consume>
```

Describe what is needed, not private implementation details.

## Independent release model

This repository releases independently.

A green PR here may mean:

- READY FOR REVIEW
- READY FOR RELEASE
- RELEASED
- BLOCKED BY HANDOFF
- WAITING FOR PUBLIC CONTRACT
- COMPATIBLE WITH RUNTIME API 1

It does **not** imply that GamerHQ production should deploy or upgrade.

A consumer such as GamerHQ may independently choose to install or pin a reviewed
immutable Skill release/commit. That integration, release snapshot and production
deployment belong to the consuming repository.

## Validation and completion

Before declaring work complete:

- run the package's offline tests;
- keep Python 3.12 and Python 3.14 CI green;
- run/retain SDK conformance and source-portability checks;
- keep package metadata aligned with `SkillManifest`;
- update README, SKILL_DESIGN, CHANGELOG and RELEASE_CHECKLIST when behavior changes;
- report public contract, storage/migration, capability/security and dependency impact.

At meaningful milestones report:

```text
COMPLETED

REPOSITORY
BRANCH
PR
VERSION / MERGE COMMIT

TESTS / CI

PUBLIC CONTRACT IMPACT

STORAGE / MIGRATION IMPACT

SECURITY / CAPABILITY IMPACT

RELEASE STATUS

DEPENDENCIES

HANDOFFS REQUIRED

PROPOSED FOLLOW-UPS
```

Production deployment, production secrets and production database mutation are
never actions of this repository.
