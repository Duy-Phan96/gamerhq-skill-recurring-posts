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

**Status:** Completed except for authoritative Scheduler state

Delivered in 1.3.x:

- one-shot Test Send;
- derived delivery states: never-sent / pending / sent;
- truthful confirmed-delivery metadata;
- non-authoritative next-occurrence preview for draft validation.

Remaining gap:

- authoritative persisted Scheduler next-run state for an existing active post.

## Milestone 5 — Authoritative Scheduler Status

**Status:** Planned / dependency pending

**Goal:** Use the public scoped Scheduler read contract to expose authoritative
runtime scheduling state without Host-private access.

Dependency:

- GamerHQ Skill SDK 0.2.x must be available as a reviewed, consumable dependency
  for this repository.
- Current Skill package metadata remains on `sdk >=0.1,<0.2`; do not raise the
  range until the dependency is intentionally adopted.

Proposed scope for the next feature release:

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

**Status:** Planned

**Goal:** Make the repository as clear to external developers and reviewers as
the implementation already is.

Priorities:

1. publish reviewed GitHub releases/tags for stable Skill versions;
2. keep this roadmap and `PROJECT_STATUS.md` current;
3. close completed/stale Issues;
4. remove merged feature branches where practical;
5. document the long-term SDK dependency/release policy;
6. keep changelog entries unambiguous and release-scoped.

## Priority backlog

### P1 — Adopt reviewed SDK 0.2.x

Only after the public Scheduler read contract is available as an intended
consumer dependency.

Acceptance:

- package metadata and CI use the intended reviewed SDK release/commit;
- Runtime API compatibility remains explicit;
- Python 3.12/3.14 CI is green.

### P1 — Implement authoritative Scheduler status

Acceptance:

- active post can report the persisted scheduler next run;
- paused/no-job state is explicit;
- no Host/database imports;
- no storage migration;
- existing Management API consumers remain compatible.

### P1 — Create the next formal Skill release

Acceptance:

- exact immutable commit recorded;
- changelog current;
- compatibility/dependency statement current;
- GitHub release notes created;
- rollback target known.

### P2 — Repository hygiene

- close completed Issue #1;
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
