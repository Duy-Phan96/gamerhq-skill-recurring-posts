# Changelog

All notable changes to `gamerhq-skill-recurring-posts` are documented here.

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
