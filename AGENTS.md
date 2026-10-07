# Recurring Posts Skill repository instructions

This package is a portable GamerHQ Skill.

Follow the canonical GamerHQ Skill Developer Guide, Authoring Contract and
Review Checklist.

Hard rules:

- Keep Skill ID `recurring-posts` stable.
- Do not import Discord.py or GamerHQ bot/cogs/services/database/hosts/config.
- Use only public `skill_runtime` contracts.
- Keep configuration behind versioned Management APIs.
- Use Skill Storage and the shared Scheduler.
- Keep tests offline and token-free.
- Preserve `posts.v1`, scheduler job keys and handler IDs across compatible releases.


## GamerHQ cross-project release boundary

This repository participates in the wider GamerHQ ecosystem.

A green PR/release in this repository means the work can be **ready for GamerHQ integration**. It does **not** independently mean the production GamerHQ server should update.

Every meaningful handoff must report:

- repository, branch, PR and immutable merge/package commit;
- public contract impact;
- storage/data migration impact;
- Runtime/API/capability impact where relevant;
- deployment/config/secret impact;
- whether this work should be included in the next GamerHQ server release snapshot.

Production deployment is decided only from one immutable GamerHQ Host release candidate and its Server Release Snapshot. Never recommend deploying a moving `develop`/latest branch merely because this repository's CI is green.

Canonical rules live in the GamerHQ Host repository:

- `docs/development/GAMERHQ_ECOSYSTEM_WORKING_RULES.md`
- `docs/development/SERVER_RELEASE_SNAPSHOT.md`

Production deployment, restart, DB mutation and production secret changes remain explicit owner actions.
