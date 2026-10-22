# Changelog

All notable changes to `gamerhq-skill-recurring-posts` are documented here.

## Unreleased

- Refreshed post-release project status on 2026-10-22 after verifying a clean GitHub state: no open Issues or Pull Requests, only `main` remains as a remote branch, and v1.4.0 remains the latest published release.
- Marked v1.4.0 as formally released after verifying the annotated tag, immutable commit, GitHub Release, wheel artifact and SHA-256 checksum artifact.
- Refreshed release-readiness status after merging the reviewed 1.4.0 source: main commit, completed Scheduler milestone, Issue #14 completion and remaining manual publication/branch-cleanup work are now documented consistently.
## 1.4.0

- Added a tag-driven GitHub Release workflow that validates tag/version/current-main alignment, builds and smoke-tests the wheel, extracts release notes from this changelog, generates SHA-256 checksums and publishes the release artifacts.
- Adopted reviewed GamerHQ Skill SDK 0.2.0 with supported range `>=0.2,<0.3`.
- Added authoritative, non-persisted `schedulerStatus` metadata to recurring-post Management responses.
- Exposes safe scheduler job key, next run, last run, failure count and revision without payload/lease/claim-token data.
- Distinguishes `scheduled`, `paused`, `missing` and `unexpected-job` scheduler states.
- Keeps draft `preview.nextOccurrence` separate and explicitly non-authoritative.
- Preserves `posts.v1`, `recurring-post.execute.v1`, `post:<post-id>`, the recurring event and existing capabilities.
- No storage migration.

- Added an explicit README compatibility matrix for the current 1.3.x SDK range and the planned SDK 0.2.x-based 1.4.0 line.
- Added a README quick start for local setup, offline testing, wheel building and consumer-installation boundaries.
- Added package discovery metadata for repository, Issues, changelog and relevant package keywords.
- Added a built-wheel smoke test that reinstalls the release artifact and verifies package version, the `gamerhq.skills` entry point, factory loading and Skill manifest identity/version.
- Added a CI release-wheel build gate that verifies the package can be built as an installable wheel and that the artifact name matches the declared package version.
- Added focused GitHub feature/bug Issue forms and a Pull Request template that capture scope, acceptance criteria, public-contract, persistence/scheduler, security, test, dependency and release impact.
- Refreshed PROJECT_STATUS after the release-metadata gate: the latest verified CI now runs 47 tests per supported Python version and the SDK 0.2 dependency remains development-line only.
- Added release-metadata regression tests that keep package, manifest, README and CHANGELOG version information synchronized.
- Refreshed project/status/design documentation after the audit follow-ups so SDK 0.2.0 is described as upstream-but-not-yet-adopted rather than missing, and completed GitHub governance work is no longer listed as outstanding.
- Added `SECURITY.md` covering vulnerability reporting, capability/guild boundaries, secrets/private data, scheduler and Management API safety.
- Added `RELEASES.md` with semantic versioning, immutable release commit, tag/GitHub Release, dependency, rollback and post-release guidance.
- Added `CONTRIBUTING.md` with repository boundaries, branch/PR workflow, test expectations, SDK dependency policy and release discipline.
- Added `PROJECT_STATUS.md` with the verified 1.3.2 implementation, quality status, dependency state, limitations and current priorities.
- Added `ROADMAP.md` with completed milestones, the planned authoritative Scheduler-status milestone, release professionalization and explicitly deferred scope.
- Recorded repository-health follow-ups from the 2026-10-12 project audit without changing runtime behavior.

## 1.3.2

- Added `preview.nextOccurrence` to validation responses.
- Next-occurrence preview is calculated from the normalized schedule at validation time.
- Explicitly marks the preview `authoritative: false` with basis `calculated-from-now`.
- Avoids claiming access to persisted Scheduler next-run state when the public scoped Scheduler API does not expose job reads.
- No storage migration, scheduler mutation change, capability change or new Management API.

## 1.3.1

- Added derived `deliveryStatus` metadata to list/get management views.
- Distinguishes `never-sent`, `pending` and `sent` using existing delivery state.
- Added readable delivery text to compact management summaries.
- Uses `lastConfirmedScheduledFor` rather than claiming `lastSentSlot` is an exact send timestamp.
- Clarified autonomous repository ownership and independent release responsibilities.
- Removed wording that implied this Skill repository controls GamerHQ Host integration or production deployment.
- Standardized cross-repository work as read-only contract inspection plus explicit handoffs.
- Added milestone reporting expectations for contracts, storage, capabilities, dependencies and handoffs.
- No storage migration, scheduler change, event change or new capability.

## 1.3.0

- Added `recurring-posts.test-send.v1` for one-shot message verification.
- Test-send supports saved posts by `postId` and unsaved drafts by `channelId` + `content`.
- Test sends do not mutate `posts.v1`, Scheduler jobs, recurring delivery slots or recurring-send events.
- Successful test sends write the separate `post-test-sent` audit action.
- Added Send test to per-item quick actions and describe metadata.
- Kept capabilities unchanged; existing Discord read/send and audit capabilities are sufficient.
- Added offline coverage for saved/draft test sends, validation, failure behavior and side-effect isolation.

## 1.2.3

- Declared `schedules` as the generic schedule hints path for the collection describe response.
- Allows generic hosts to locate schedule presets and constraints without hard-coding Recurring Posts response keys.
- No storage, scheduler, capability or Management API behavior changes.

## 1.2.2

- Declared `recurring-posts.describe.v1` as the generic collection describe contract.
- Declared `post` as the single-item management response path.
- Completes the schema metadata needed for generic host/web collection CRUD and richer UX hints.
- No storage, scheduler, capability or Management API behavior changes.

## 1.2.1

- Declared `postId` as the generic collection item identity payload key.
- Enables host/web collection edit, pause/resume and delete flows without Recurring Posts-specific payload knowledge.
- No storage, scheduler, capability or Management API behavior changes.

## 1.2.0

- Added Management UI Schema V1 as a declarative description of the existing Recurring Posts management surface.
- Declares the post list as a generic collection with list/create/get/validate/update/pause-resume/delete-preview/delete contracts.
- Declares item fields for name, Discord channel, message content, schedule and active state.
- Keeps `posts.v1`, scheduler identities and all existing Management API IDs unchanged.
- Enables generic web/host clients to render Recurring Posts without importing private Skill implementation code.
- No new Discord permissions or host capabilities are required.

## 1.1.0

- Added `recurring-posts.update.v1` for in-place editing of existing recurring posts.
- Edit preserves post IDs and scheduler job keys and uses idempotent scheduler upsert/remove behavior.
- Edit can change name, channel, message, schedule and optional active/paused state.
- Kept `posts.v1` storage backward compatible with no migration.
- Kept the 15-minute interval minimum enforced server-side for create and edit.
- Documented the Runtime API 1 management-form schema gap required for a portable UI label such as `Every N minutes (min. 15)`.
- Expanded offline tests for edit behavior, scheduler identity, validation, rollback and existing stored data.
- Added `recurring-posts.describe.v1` with host-neutral UX constraints, labels and schedule hints.
- Added read-only `recurring-posts.validate.v1` for review/preview flows without persistence or Scheduler side effects.
- Management responses now include readable derived `status` and `scheduleSummary` fields.
- Create can save a post initially paused via optional `active: false`.
- Added UX principles for error prevention, preview-before-persist, safe drafts and identity-preserving edits.
- Added quick interval presets for 15m, 30m, 1h, 3h, 6h and 12h while preserving custom intervals.
- Added read-only `recurring-posts.delete-preview.v1` so hosts can show deletion impact and explicit confirmation before calling the unchanged delete contract.
- Added derived `managementSummary`, compact-card presentation hints and Edit/Pause/Resume/Delete quick actions to make the recurring-post list easier to manage.

## 1.0.0

- First external-package release candidate.
- Stable Skill ID: `recurring-posts`.
- Interval, daily and weekly schedules.
- Persistent Skill storage under `posts.v1`.
- Shared Scheduler handler `recurring-post.execute.v1`.
- Versioned host management contracts for list/get/create/pause-resume/delete.
- External package entry point `gamerhq.skills`.
- Offline SDK conformance and source-portability tests.
