# Skill Design — Recurring Posts

## Identity

- Skill ID: `recurring-posts`
- Package: `gamerhq-skill-recurring-posts`
- Version: `1.3.2`
- Runtime API: `1`

## Repository boundary

This repository owns the Recurring Posts domain implementation and its public
Skill contracts. It does not own the GamerHQ Host, public Runtime/SDK
implementation, gamerhq-web, other Skills or production deployment.

Read-only inspection of released/public upstream contracts is allowed for
compatibility. Missing upstream behavior is handled through a handoff rather than
a cross-repository implementation.

## Purpose

Schedule recurring Discord messages without a Skill-owned background scheduler.

## Capabilities

- `discord.channels.read`: validate configured channel IDs.
- `discord.messages.send`: deliver configured posts.
- `scheduler.jobs`: persist future execution.
- `storage.skill`: persist configuration/delivery state.
- `events.emit`: emit confirmed-send events.
- `audit.write`: record administrative changes.

## Storage

- `posts.v1`: versioned map of recurring post records.

## Scheduler

- Handler: `recurring-post.execute.v1`
- Job key: `post:<post-id>`

## Event

- `recurring-post.sent.v1`

## Management APIs

- list/get/create/describe/validate/test-send/update/set-active/delete-preview/delete v1 contracts.

## UX design principles

The Skill optimizes for a review-first administrative flow:

1. Constraints are discoverable before data entry.
2. Drafts can be validated without persistence or Scheduler side effects.
3. Human-readable schedule/status summaries are derived for Management API
   responses but are never written into `posts.v1`.
4. Create can save a post paused, allowing an administrator to prepare content
   before activation.
5. Edit preserves identity and avoids destructive delete/recreate workflows.
6. Errors remain host-neutral and server-side validation remains authoritative.
7. Common interval choices are exposed as presets, but presets never replace the
   underlying generic schedule contract.
8. Destructive deletion is preceded by a read-only impact preview.
9. The list contract returns UI-ready summaries and actions so hosts do not need
   to infer Skill behavior from raw storage-shaped fields.
10. A one-shot test send is explicitly separated from persisted Scheduler
    delivery and recurring send events.
11. Delivery status must reflect only facts represented by persisted delivery
    state; scheduler slots are never mislabeled as actual send timestamps.
12. Schedule previews must distinguish calculated occurrence previews from
    authoritative persisted Scheduler state.

`recurring-posts.describe.v1` is read-only and returns small JSON-like UX hints:
limits, field labels/help, schedule payload fields, weekday choices and the
15-minute interval minimum.

`recurring-posts.validate.v1` is also read-only. It validates the selected
channel and schedule and returns a normalized preview with `status` and
`scheduleSummary`. It does not write storage, audit, Scheduler jobs or events.

## Management list

`recurring-posts.list.v1` keeps its existing post data and adds derived,
non-persisted management metadata:

- `managementSummary`: title, active/paused status, channel ID and readable schedule;
- `quickActions`: Edit, Pause/Resume and Delete descriptors;
- Delete always points to `delete-preview.v1`, not directly to the destructive operation.

`describe.v1` also declares a compact-card list presentation hint. These hints
remain host-neutral JSON and do not contain Discord.py UI objects.

## Test send

`recurring-posts.test-send.v1` sends one immediate message through the public
Discord port. Requests use exactly one of:

- saved mode: `{"postId": "..."}`
- draft mode: `{"channelId": 123, "content": "..."}`

The operation validates the destination and Discord message-length rules. It does
not create/remove/update Scheduler jobs, does not mutate `posts.v1`, does not
touch `pendingSlot`, `lastSentSlot` or `lastMessageId`, and does not emit
`recurring-post.sent.v1`. On a confirmed send it writes the administrative
audit action `post-test-sent`.

There is no automatic retry. As with any external side effect, a process failure
around delivery cannot provide an exactly-once guarantee; callers should not
blindly retry an uncertain result.

Management UI Schema V1 currently has no standardized arbitrary collection-item
action field. The Skill therefore exposes test-send through `describe.v1` and
`quickActions` without extending or coupling to private host UI contracts.

## Schedule presets

`recurring-posts.describe.v1` includes interval presets for 15 minutes,
30 minutes, 1 hour, 3 hours, 6 hours and 12 hours. They are convenience values
only. Custom interval schedules remain supported, and the Skill never invents a
maximum interval.

## Delete safety

`recurring-posts.delete-preview.v1` is a read-only destructive-action preview.
It returns the post, a user-facing warning, whether configuration and the
Scheduler job will be removed, and clarifies that existing Discord messages are
not deleted.

The existing `recurring-posts.delete.v1` contract remains unchanged for
backward compatibility. Hosts should present preview/confirm UX before invoking
it; the Skill does not silently change the semantics of the existing delete
contract.

## Edit contract

`recurring-posts.update.v1` performs an in-place edit. It preserves the
configured post ID and the scheduler key `post:<post-id>`. The edit may change
name, destination channel, content, schedule and optionally active state.
Scheduler changes use idempotent upsert/remove operations; the Skill does not
delete and recreate the post.

Storage remains `posts.v1`; version 1.1.0 adds no persisted fields and requires
no migration. Existing delivery state remains compatible. `pendingSlot` is
cleared when configuration changes so an old in-flight reservation is not
carried into a changed schedule.

## Configuration UI contract gap

Runtime API 1 currently has no standardized cross-Skill Management API form
schema. Recurring Posts therefore exposes Skill-specific host-neutral UX
metadata through `recurring-posts.describe.v1` instead of importing host UI
objects. This solves the immediate Skill UX need while keeping the package
portable.

Management UI Schema V1 now covers the generic form/collection surface used by
this Skill. A future generic arbitrary collection-item action contract would
improve portable rendering of actions such as test-send; that is an upstream
public-contract concern and must be handled by handoff rather than by changing
Host/SDK internals from this repository.

## Delivery status UX

Management views derive a non-persisted `deliveryStatus` object from the existing
`pendingSlot`, `lastSentSlot` and `lastMessageId` fields.

- `never-sent`: no confirmed message ID exists.
- `pending`: a slot is reserved/in flight; previous confirmed delivery metadata
  remains visible when present.
- `sent`: a confirmed Discord message ID exists and no delivery is currently pending.

The API names the slot `lastConfirmedScheduledFor`, not `lastSentAt`, because
`lastSentSlot` records scheduler intent rather than the exact external-delivery
wall-clock time. No new history table or timestamp is invented.

## Delivery model

Known send failures may retry. A crash in the uncertain external-delivery window
favors avoiding duplicate catch-up messages rather than claiming exactly-once
Discord delivery.

## Security/privacy impact

Edit/test-send adds no capability and no new persisted data class. Channel validation still goes through the public Discord port, audit writes remain administrative metadata only, and cross-guild access is not introduced.


## Schedule occurrence preview

`recurring-posts.validate.v1` derives a next-occurrence preview using the public
schedule contract's `next_run_at(...)` helper after the draft is normalized.

This preview is useful during create/edit review, but it is intentionally marked:

- `basis: calculated-from-now`
- `authoritative: false`

For interval schedules, that means "one interval from validation time", not the
actual persisted job's next execution. For daily/weekly schedules it represents
the next occurrence from the same reference time, still without claiming access
to scheduler persistence.

The public scoped Scheduler API currently has no read-only job lookup. Therefore
this Skill must not fabricate an authoritative "Next run" for existing jobs.
That missing capability belongs to the Runtime/SDK owner and is handled by
handoff.
