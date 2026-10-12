# Project Status — Recurring Posts

_Last reviewed: 2026-10-12_

## Executive status

Recurring Posts is a standalone, portable GamerHQ Skill for persistent scheduled
Discord messages.

**Current package version:** `1.3.2`  
**Runtime API:** `1`  
**Skill ID:** `recurring-posts`  
**Storage key:** `posts.v1`  
**Scheduler handler:** `recurring-post.execute.v1`  
**Scheduler job key:** `post:<post-id>`  
**Event:** `recurring-post.sent.v1`

**Maturity:** Beta / release-ready library, pending stronger formal release
publishing and the next reviewed SDK dependency update.

## Verified implementation

Scheduling:

- interval;
- daily fixed time;
- weekly fixed time;
- IANA timezones through the public schedule contract;
- Skill-level 15-minute interval minimum.

Management:

- list;
- get;
- create;
- validate/preview;
- update in place;
- pause/resume;
- delete preview;
- delete;
- one-shot test send.

UX metadata:

- Management UI Schema V1 collection;
- field and schedule hints;
- common interval presets;
- compact management summaries;
- quick actions;
- delivery status;
- non-authoritative next-occurrence preview.

Reliability:

- persisted delivery reservation state;
- duplicate protection for the same scheduler slot;
- known-send-failure retry path;
- identity-preserving edits;
- scheduler rollback on failed updates;
- non-destructive disable behavior.

## Current public Management APIs

- `recurring-posts.list.v1`
- `recurring-posts.get.v1`
- `recurring-posts.create.v1`
- `recurring-posts.describe.v1`
- `recurring-posts.validate.v1`
- `recurring-posts.test-send.v1`
- `recurring-posts.update.v1`
- `recurring-posts.set-active.v1`
- `recurring-posts.delete-preview.v1`
- `recurring-posts.delete.v1`

## Capabilities

- `discord.channels.read`
- `discord.messages.send`
- `scheduler.jobs`
- `storage.skill`
- `events.emit`
- `audit.write`

No direct Discord.py, GamerHQ database, Host service, config, or another Skill's
private implementation is allowed.

## Quality status

The current `main` commit for 1.3.2 passed the repository CI on Python 3.12 and
Python 3.14.

Latest verified CI run collected **47 tests** and passed all 47 on both supported
Python versions.

No code-coverage percentage is currently claimed.

## Current limitations

### Authoritative next run

Version 1.3.2 can calculate a draft next-occurrence preview, but intentionally
marks it non-authoritative.

The required public Scheduler read contract has since been implemented upstream
in GamerHQ Skill SDK 0.2.0 on the GamerHQ development line. As of the latest
2026-10-12 verification, GamerHQ `main` still publishes SDK 0.1.0 while
`develop` carries 0.2.0. This repository has
not yet intentionally adopted SDK 0.2.x and still declares:

`sdk >=0.1,<0.2`

Therefore authoritative Scheduler state is not yet part of the current Skill
release. Issue #14 tracks the planned 1.4.0 adoption once 0.2.x is an intended
consumer dependency.

### Generic Test Send action rendering

The Skill exposes Test Send through public `describe.v1` metadata and
`quickActions`. A fully standardized generic arbitrary collection-item action
schema is still an optional upstream improvement, not a blocker.

## Repository / release health

Strengths:

- clear repository ownership;
- stable compatibility identities;
- small focused codebase;
- strong offline contract tests;
- dual-version Python CI;
- explicit release checklist.

Current repository-management gaps:

- package version 1.3.2 exists, but no GitHub Release was found during the
  2026-10-12 audit;
- multiple merged feature/docs branches remain in the repository;
- release tags could not be reliably verified through the available audit tooling.

Repository-governance improvements completed after the audit:

- Issue #1 was closed as completed;
- `ROADMAP.md`, `CONTRIBUTING.md`, `RELEASES.md` and `SECURITY.md` were added;
- Issue #14 now tracks the 1.4.0 Scheduler-status milestone;
- Issue #17 tracks formal GitHub release and branch-cleanup work.

## Current priorities

1. keep 1.3.2 stable;
2. adopt reviewed SDK 0.2.x when intentionally consumable;
3. implement authoritative Scheduler status as the next focused feature;
4. publish the next formal GitHub release with clear compatibility notes;
5. maintain repository hygiene and documentation consistency.

## Not current scope

Do not expand this Skill into a general social-media automation platform.

Deferred unless user demand proves otherwise:

- delivery-history storage;
- analytics;
- AI-generated copy;
- cron expressions;
- arbitrary scripts;
- custom Skill-specific web frontend;
- unrelated community automation.

## Repository boundary

This repository owns only Recurring Posts.

Changes required in GamerHQ Host, the public Runtime/SDK implementation,
gamerhq-web, or another Skill must be handled through public contracts and
handoffs. A release here does not imply a GamerHQ production deployment.
