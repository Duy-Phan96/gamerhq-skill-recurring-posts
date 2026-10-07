# GamerHQ Skill — Recurring Posts

Reference external Skill package for the GamerHQ Skill Runtime.

Skill ID: `recurring-posts`  
Version: `1.3.1`  
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
- `recurring-posts.test-send.v1`
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

The list response is also optimized for day-to-day management. Each post
contains a compact summary with title, status, channel ID and readable schedule,
plus host-neutral quick-action descriptors. Edit starts a review flow,
Pause/Resume maps to `set-active.v1`, and Delete routes through the preview
contract first.

A host may also call `recurring-posts.test-send.v1` to send one immediate
test message. It supports either a saved post (`postId`) or an unsaved draft
(`channelId` + `content`). Test sends do not create/update Scheduler jobs,
do not change `posts.v1`, do not update recurring delivery slots, and do not
emit `recurring-post.sent.v1`. Successful test sends are audited separately.

Before a destructive delete, a host should call
`recurring-posts.delete-preview.v1`. It returns the affected post, a warning,
the exact impact, and a suggested confirmation value. The preview is read-only
and does not remove configuration or Scheduler jobs.

## Persistence

Storage key: `posts.v1`

Scheduler handler: `recurring-post.execute.v1`

This Skill now lives in its own Git repository. Changing repository location must never change its Skill ID, storage namespace or scheduler identity.

## Development

This is the standalone repository for an external GamerHQ Skill. It is versioned
and released independently. A compatible consumer may choose to install or pin a
reviewed immutable release/commit through its own release process.

Run the GamerHQ SDK conformance/source-audit checks and the package's offline
tests before release.


## Developer workflow

Before changing behavior, review:

- `SKILL_DESIGN.md` — architecture and contract inventory;
- `AGENTS.md` — repository rules for developers and coding agents;
- `RELEASE_CHECKLIST.md` — release and deployment readiness.

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
- **Daily management stays compact:** list responses include a small
  `managementSummary` and `quickActions` block so the host can render cards
  with Edit, Pause/Resume, Send test and Delete without reconstructing Skill semantics.
- **Safe test delivery:** admins can verify a message once before activation
  without creating recurring state or pretending the test was a scheduled send.
- **Truthful delivery status:** management views distinguish Never sent,
  Delivery pending and Last send confirmed without pretending the scheduler slot
  is the actual Discord send timestamp.

## Generic Management UI Schema

Version 1.2.0 declares the existing Recurring Posts management surface through
the public Management UI Schema V1.

The Skill exposes one generic `collection` of recurring posts. Its schema maps
to the already-versioned Management APIs for list, create, read, validate,
update, pause/resume, delete preview and delete.

Item fields are declared as portable types:

- name → `string`
- destination channel → `discord_channel`
- message → `long_text`
- schedule → `schedule`
- active state → `boolean`

This lets a host or web client build the Recurring Posts UI without importing
private Skill models or writing a Skill-specific React page.

`recurring-posts.describe.v1` remains useful for richer schedule hints,
presets and limits. Server-side validation remains authoritative, including the
15-minute minimum interval.


### Collection item identity payload

Version 1.2.1 declares `postId` as the collection item identity payload key.
Generic hosts can therefore read an item ID from `id` and safely call
get/update/pause/delete contracts without Recurring Posts-specific frontend code.

Version 1.2.2 completes the generic collection binding by declaring:
- `describeContract = recurring-posts.describe.v1` for host-neutral UX and schedule hints;
- `itemReadPath = post` for normalizing single-item read responses.

Together with `itemIdPayloadKey = postId`, a generic host can discover, read,
edit, pause/resume and delete Recurring Posts without knowing Recurring Posts
payload conventions in frontend code.

Version 1.2.3 declares `scheduleHintsPath = schedules`. A generic host can now
call the declared describe contract, follow the schema-provided path, and render
the existing interval/daily/weekly hints and presets without hard-coding the
Recurring Posts response property name.


## Test sends

Version 1.3.0 adds `recurring-posts.test-send.v1`. The operation is intentionally
outside persisted scheduling semantics: it performs one explicit Discord send,
returns the resulting message ID, writes a `post-test-sent` audit record after a
confirmed send, and leaves recurring configuration/delivery state unchanged.

The current generic Management UI Schema V1 has no standardized arbitrary item-action
slot for test-send. Recurring Posts therefore advertises the action through its
existing host-neutral `describe.v1` metadata and per-item `quickActions` until the
SDK adds a generic action contract.


## Repository ownership

This repository owns only the Recurring Posts Skill: its implementation, public
Skill contracts, tests, documentation and independent release lifecycle.

It does not own GamerHQ Host, gamerhq-web, another Skill repository, production
infrastructure or deployment decisions. External projects are consumed only
through released/public contracts. If a missing Host/SDK/web capability blocks
work here, this project stops at a handoff instead of modifying that repository.

A successful release here means the Skill is independently releasable. It does
not mean any GamerHQ server should automatically update.


## Delivery status

Version 1.3.1 adds derived `deliveryStatus` metadata to list/get management
responses. It is intentionally non-persisted and uses only the existing delivery
state already stored in `posts.v1`.

States:

- `never-sent` — no confirmed Discord delivery exists;
- `pending` — a scheduler slot is reserved/in flight;
- `sent` — the most recent recorded delivery was confirmed by a Discord message ID.

The response exposes `pendingScheduledFor`, `lastConfirmedScheduledFor` and
`lastMessageId`. The field name says **scheduled for** deliberately: the existing
`lastSentSlot` is the scheduler slot, not a trustworthy wall-clock send time.
