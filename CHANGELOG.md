# Changelog

All notable changes to `gamerhq-skill-recurring-posts` are documented here.

## Unreleased

## 1.3.1

- Added derived `deliveryStatus` metadata to list/get management views.
- Distinguishes `never-sent`, `pending` and `sent` using existing delivery state.
- Added readable delivery text to compact management summaries.
- Uses `lastConfirmedScheduledFor` rather than claiming `lastSentSlot` is an exact send timestamp.
- No storage migration, scheduler change, event change or new capability.

- Clarified autonomous repository ownership and independent release responsibilities.
- Removed wording that implied this Skill repository controls GamerHQ Host integration or production deployment.
- Standardized cross-repository work as read-only contract inspection plus explicit handoffs.
- Added milestone reporting expectations for contracts, storage, capabilities, dependencies and handoffs.

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
