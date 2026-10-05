# GamerHQ Skill — Recurring Posts

Reference external Skill package for the GamerHQ Skill Runtime.

Skill ID: `recurring-posts`  
Version: `1.1.0`  
Runtime API: `1`

## Purpose

Create persistent interval, daily or weekly Discord posts through host
capabilities and the shared Skill Scheduler.

## Capabilities

- `discord.channels.read`
- `discord.messages.send`
- `scheduler.jobs`
- `storage.skill`
- `events.emit`
- `audit.write`

## Management APIs

- `recurring-posts.list.v1`
- `recurring-posts.get.v1`
- `recurring-posts.create.v1`
- `recurring-posts.describe.v1`
- `recurring-posts.validate.v1`
- `recurring-posts.update.v1`
- `recurring-posts.set-active.v1`
- `recurring-posts.delete-preview.v1`
- `recurring-posts.delete.v1`

The host UI must use these management contracts. It must not import this
package's private models or implementation.

`recurring-posts.update.v1` updates an existing post in place. The request keeps
the same `postId` and accepts `name`, `channelId`, `content`, `schedule`, and
optional boolean `active`. Compatible edits preserve the scheduler identity
`post:<post-id>` and use scheduler upsert rather than delete + recreate.

Interval schedules are validated server-side with a minimum of 15 minutes.

### UX-oriented management flow

A host can build a friendlier configuration flow without importing private Skill
classes:

1. Call `recurring-posts.describe.v1` to read limits, field hints, supported
   schedules and the interval label/constraint.
2. Let the user review the draft.
3. Call `recurring-posts.validate.v1` to validate the destination channel and
   normalized schedule without writing storage, creating jobs or auditing a
   configuration change.
4. Show the returned preview, including readable status and schedule summary.
5. Only after confirmation call create or update.

Create also accepts optional boolean `active`, so a recurring post may be saved
as a paused draft before it ever schedules a job.

For interval schedules, `describe.v1` also exposes quick choices for 15 minutes,
30 minutes, 1 hour, 3 hours, 6 hours and 12 hours. These are UX shortcuts only;
custom intervals remain supported and the 15-minute server-side minimum remains
authoritative.

Before a destructive delete, a host should call
`recurring-posts.delete-preview.v1`. It returns the affected post, a warning,
the exact impact, and a suggested confirmation value. The preview is read-only
and does not remove configuration or Scheduler jobs.

## Persistence

Storage key: `posts.v1`

Scheduler handler: `recurring-post.execute.v1`

This Skill now lives in its own Git repository. Changing repository location must never change its Skill ID, storage namespace or scheduler identity.

## Development

This is the standalone reference repository for an external GamerHQ Skill. GamerHQ installs a reviewed, pinned commit of this repository during its image build.

Run the GamerHQ SDK conformance/source-audit checks and the package's offline
tests before release.


## Developer workflow

Before changing behavior, review:

- `SKILL_DESIGN.md` — architecture and contract inventory;
- `AGENTS.md` — repository rules for developers and coding agents;
- `RELEASE_CHECKLIST.md` — release and deployment readiness.

The host-side extraction/deployment rules are documented in the GamerHQ repository under `docs/skills/recurring-posts-extraction.md`.

The package must remain independently testable without a Discord token or
production database.

## User experience principles

Recurring Posts follows a small set of portable UX rules:

- **Prevent errors early:** expose constraints before submit and keep server-side
  validation authoritative.
- **Preview before persistence:** validation is read-only and safe to call from
  review/confirm flows.
- **Preserve identity during edits:** editing never forces users to delete and
  recreate a post.
- **Use understandable state:** Management responses include derived `status`
  and `scheduleSummary` fields without changing persisted `posts.v1` records.
- **Safe drafts:** posts may be created paused and activated later.
- **Fast common paths:** useful interval presets reduce unnecessary typing without
  removing custom schedules.
- **Destructive actions are explicit:** deletion has a read-only impact preview
  before the existing delete operation is invoked.

## Host UI note

The current Runtime API 1 `ManagementApiContract` exposes only an operation ID
and description; it does not provide a public form/input-schema contract.
The Skill now exposes its own host-neutral UX hints through
`recurring-posts.describe.v1`, including **Every N minutes (min. 15)** and the
underlying schedule payload field. This is enough for a GamerHQ integration to
build a good Skill-specific flow while the Skill's 15-minute server-side
validation remains authoritative. A future generic Skill Builder needs a public
management-form schema in the SDK rather than private host assumptions.
