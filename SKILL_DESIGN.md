# Skill Design — Recurring Posts

## Identity

- Skill ID: `recurring-posts`
- Package: `gamerhq-skill-recurring-posts`
- Version: `1.1.0`
- Runtime API: `1`

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

- list/get/create/describe/validate/update/set-active/delete-preview/delete v1 contracts.

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

The missing future SDK/host contract is a host-neutral management-form schema
that can declare an interval-minutes input and its minimum without importing
Skill-private classes or Discord UI objects.

## Delivery model

Known send failures may retry. A crash in the uncertain external-delivery window
favors avoiding duplicate catch-up messages rather than claiming exactly-once
Discord delivery.

## Security/privacy impact

Edit adds no capability and no new data class. Channel validation still goes through the public Discord port, audit writes remain administrative metadata only, and cross-guild access is not introduced.
