# Contributing to Recurring Posts

Thank you for contributing to the standalone Recurring Posts Skill.

This repository is intentionally small and focused. Contributions should improve
Recurring Posts itself without turning this project into a Host, deployment
orchestration layer, or general automation platform.

## Repository boundary

This repository owns:

- Recurring Posts behavior;
- its public Management APIs;
- `posts.v1` compatibility;
- `recurring-post.execute.v1`;
- `post:<post-id>` scheduler identity;
- `recurring-post.sent.v1`;
- package tests, documentation and independent releases.

This repository does not own:

- GamerHQ Host internals;
- gamerhq-web;
- the public Runtime/SDK implementation;
- another Skill;
- production infrastructure or deployment.

If work requires another repository to change, create a handoff rather than
editing that repository from this project.

## Before starting

Review:

- `PROJECT_STATUS.md` — current verified state and active constraints;
- `ROADMAP.md` — milestones, priorities and deferred scope;
- `AGENTS.md` — repository ownership and AI-agent rules;
- `SKILL_DESIGN.md` — public identities and architecture;
- `RELEASE_CHECKLIST.md` — compatibility and release gates.

Check existing Issues and Pull Requests before creating duplicate work.

## Branches

Use one focused branch per coherent change.

Recommended prefixes:

- `feature/`
- `fix/`
- `docs/`
- `chore/`

Examples:

```text
feature/authoritative-scheduler-status
fix/test-send-validation
docs/release-policy
```

Do not keep unrelated work on the same branch.

## Pull requests

A PR should explain:

- problem / requested outcome;
- implementation summary;
- public contract impact;
- storage or migration impact;
- scheduler/event impact;
- capability/security impact;
- tests run;
- dependency impact;
- intentionally deferred work.

Breaking public behavior requires a new versioned contract rather than silently
changing an existing one.

## Development rules

Portable Skill code must:

- use only public `skill_runtime` contracts;
- avoid Discord.py and GamerHQ private imports;
- avoid raw host database/config access;
- avoid another Skill's private implementation;
- use Skill Storage for Skill-owned state;
- use the shared Scheduler for persisted future work;
- preserve stable identities across compatible releases;
- remain testable without a Discord token or production state.

Prefer the smallest coherent change over broad refactoring.

## Stable compatibility identities

Treat these as compatibility-critical:

```text
Skill ID: recurring-posts
Storage: posts.v1
Scheduler handler: recurring-post.execute.v1
Scheduler job key: post:<post-id>
Event: recurring-post.sent.v1
Runtime API: 1
```

A compatible release should not change them casually.

## Testing

Run the package's offline tests before opening a PR:

```bash
python -m pytest
```

CI currently validates supported Python versions:

- Python 3.12
- Python 3.14

Tests must not require:

- a Discord token;
- a production database;
- a live guild;
- private environment values.

Update or add regression tests when changing behavior.

## Dependencies

The Skill Runtime/SDK is a public dependency and must be consumed deliberately.

Rules:

1. package metadata must state the supported SDK range;
2. CI should pin a reviewed immutable SDK commit/release for reproducibility;
3. do not raise the SDK range merely because a feature exists on an upstream
   development branch;
4. only use public contracts available in the dependency intentionally adopted
   by this repository;
5. document compatibility changes in README, PROJECT_STATUS, ROADMAP and
   CHANGELOG when they affect consumers.

## Versioning

Use semantic versioning for the Skill package.

- patch: backward-compatible correction or small additive presentation metadata;
- minor: backward-compatible public functionality;
- major: breaking public contract or compatibility change.

Runtime API versioning is separate from Skill package versioning.

## Release readiness

Before a release:

- relevant CI must be green;
- package/manifest metadata must agree;
- changelog must describe the release;
- storage compatibility must be reviewed;
- scheduler/event identities must be reviewed;
- dependency compatibility must be explicit;
- no new capability should be requested without justification;
- the exact immutable release commit must be known.

A Skill release does not imply a GamerHQ production deployment.

## Scope discipline

Current intentional non-goals are listed in `ROADMAP.md`.

Do not add large new areas such as analytics, AI copy generation, social-media
publishing, cron scripting or custom frontend applications without an approved
product requirement.

## Security

Never commit:

- tokens;
- passwords;
- real environment values;
- production database content;
- private logs;
- user/community private data.

Use synthetic fixtures in tests and public host-neutral contracts in Skill code.

## AI-assisted contributions

AI-assisted changes follow the same rules as human changes.

An AI agent must not use convenience as a reason to bypass:

- repository ownership;
- public SDK boundaries;
- tests;
- versioned contracts;
- review;
- compatibility checks.
