# Project Status — Recurring Posts

_Last reviewed: 2026-10-12_

## Executive status

Recurring Posts is a standalone, portable GamerHQ Skill for persistent scheduled
Discord messages.

**Current source/package version:** `1.4.0`  
**Runtime API:** `1`  
**Skill ID:** `recurring-posts`  
**Storage key:** `posts.v1`  
**Scheduler handler:** `recurring-post.execute.v1`  
**Scheduler job key:** `post:<post-id>`  
**Event:** `recurring-post.sent.v1`

**Maturity:** Beta / release-ready library. SDK 0.2.0 is adopted. The remaining
owner approval is to create/push the exact `v1.4.0` tag; the repository release
workflow will then validate and publish the GitHub Release automatically.

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
- non-authoritative next-occurrence preview;
- authoritative persisted Scheduler status in management responses.

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

The current `main` commit `f0e8b8f250a1125fcfee99def27af905069a7c62`
contains the reviewed 1.4.0 source and passed repository CI on Python 3.12 and
Python 3.14.

Latest verified 1.4.0 candidate CI run collected **52 tests** and passed all 52
on both supported Python versions, including release-wheel build/install and
entry-point smoke validation.

No code-coverage percentage is currently claimed.

## Current limitations

### Authoritative Scheduler status

The SDK 0.2.0 dependency is now available on the reviewed GamerHQ `main` line
and Recurring Posts 1.4.0 adopts it through the public scoped Scheduler read
contract.

Management responses can now distinguish scheduled, paused, missing-job and
unexpected-job states without Host/database access or new persisted Skill data.

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

- 1.4.0 is **READY FOR RELEASE**; the immutable `v1.4.0` tag still requires an
  explicit repository-owner action, after which the tag-driven workflow publishes
  the GitHub Release automatically;
- multiple merged feature/docs/test branches remain in the repository;
- release tags cannot be created or verified through the current project connector.

Repository-governance improvements completed after the audit:

- Issue #1 was closed as completed;
- `ROADMAP.md`, `CONTRIBUTING.md`, `RELEASES.md` and `SECURITY.md` were added;
- Issue #14 was completed by the merged 1.4.0 source;
- Issue #17 tracks formal GitHub release and branch-cleanup work.

## Current priorities

1. push `v1.4.0` from the final reviewed `main` commit and verify the automated GitHub Release;
2. keep the SDK 0.2.x compatibility statement current;
3. complete Issue #17 release/branch hygiene;
4. maintain repository hygiene and documentation consistency;
5. defer new feature expansion until there is demonstrated user demand.

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
