# Roadmap — Recurring Posts

This roadmap captures approved direction and repository-local priorities for the
standalone Recurring Posts Skill. It does not control GamerHQ Host, gamerhq-web,
other Skills, or production deployment.

## Product direction

Recurring Posts should remain a focused, portable utility Skill for reliable
scheduled Discord messages. The goal is not to become a general social-media
scheduler.

Core principles:

- keep Skill ID, storage namespace and scheduler identities stable;
- prefer additive public contracts and backward-compatible releases;
- use only public GamerHQ Runtime/SDK contracts;
- keep administration host-neutral and schema-driven where possible;
- avoid new persistence or complexity unless user value justifies it;
- release independently from GamerHQ Host.

## Milestone 1 — External Skill Foundation

**Status:** Completed

**Goal:** Extract Recurring Posts into an independently testable and releasable
external Skill.

Delivered:

- standalone package and `gamerhq.skills` entry point;
- stable Skill ID `recurring-posts`;
- Runtime API 1 compatibility;
- `posts.v1` Skill Storage;
- shared Scheduler handler `recurring-post.execute.v1`;
- stable `post:<post-id>` scheduler job identity;
- offline/token-free tests and Python 3.12/3.14 CI.

## Milestone 2 — Complete Management Workflow

**Status:** Completed

**Goal:** Support safe day-to-day administration without delete/recreate flows.

Delivered:

- list/get/create/update;
- pause/resume;
- read-only describe and validate/preview flow;
- safe paused drafts;
- visible 15-minute interval minimum;
- interval presets;
- delete preview before destructive deletion;
- human-readable schedule/status summaries.

Primary historical work: PR #2 / Issue #1.

## Milestone 3 — Generic Management UI Compatibility

**Status:** Completed

**Goal:** Allow generic Host/web clients to render Recurring Posts without
private Skill imports or a Skill-specific frontend implementation.

Delivered in 1.2.x:

- Management UI Schema V1 collection declaration;
- item identity mapping;
- item read binding;
- schedule hint binding;
- host-neutral fields and CRUD contracts.

## Milestone 4 — Operational UX & Delivery Visibility

**Status:** Completed

Delivered in 1.3.x:

- one-shot Test Send;
- derived delivery states: never-sent / pending / sent;
- truthful confirmed-delivery metadata;
- non-authoritative next-occurrence preview for draft validation.

The authoritative persisted Scheduler-state gap was completed in Milestone 5.

## Milestone 5 — Authoritative Scheduler Status

**Status:** Completed in 1.4.0 source — publication pending

**Goal:** Use the public scoped Scheduler read contract to expose authoritative
runtime scheduling state without Host-private access.

Dependency:

- GamerHQ Skill SDK 0.2.0 is now available on the reviewed `main` line.
- Recurring Posts 1.4.0 adopts `sdk >=0.2,<0.3` and pins the reviewed upstream
  main commit in CI.

1.4.0 scope:

- read `ctx.scheduler.get_job(key=f"post:{post_id}")`;
- expose authoritative `next_run_at` for active jobs;
- safely represent missing jobs / paused posts;
- optionally expose safe last-run/failure metadata only where it improves admin UX;
- preserve `posts.v1`, handler ID and job key identity;
- no new capability unless the public SDK contract requires one.

Non-goals:

- delivery-history database;
- analytics dashboards;
- cron syntax;
- AI-generated content;
- custom scripting;
- Skill-specific web application code.

## Milestone 6 — Release & Repository Professionalization

**Status:** In Progress

**Goal:** Make the repository as clear to external developers and reviewers as
the implementation already is.

Completed:

- added `PROJECT_STATUS.md` and this roadmap;
- added `CONTRIBUTING.md`;
- added `RELEASES.md`;
- added `SECURITY.md`;
- closed completed Issue #1;
- completed Issue #14 with the 1.4.0 authoritative Scheduler-status implementation;
- created Issue #17 for formal release/branch hygiene.

Remaining priorities:

1. publish reviewed GitHub releases/tags for stable Skill versions;
2. remove merged feature branches where practical;
3. keep this roadmap and `PROJECT_STATUS.md` current;
4. keep changelog entries unambiguous and release-scoped.

## Priority backlog

### P1 — Publish Recurring Posts 1.4.0

The reviewed SDK 0.2.x dependency and authoritative Scheduler status are
implemented in the 1.4.0 source line.

Acceptance before publication:

- exact immutable merge commit recorded;
- Python 3.12/3.14 CI is green;
- 52 offline/contract/release-metadata tests pass per supported Python version;
- release wheel build/install and entry-point smoke checks pass;
- compatibility/dependency statement is current.

### P1 — Create the next formal Skill release

Acceptance:

- exact immutable commit recorded;
- changelog current;
- compatibility/dependency statement current;
- GitHub release notes created;
- rollback target known.

### P2 — Repository hygiene

- prune merged branches where supported;
- keep status/roadmap synchronized with releases.

### P3 — Optional future improvements

Only pursue with demonstrated user demand:

- richer generic item-action schema support;
- limited delivery diagnostics;
- additional schedule convenience UX.

## Explicitly deferred

The following are not current committed scope:

- full delivery history;
- post analytics;
- AI copy generation;
- social-media publishing;
- cron expressions;
- arbitrary scripting;
- custom frontend pages;
- new storage tables solely for UI polish.
