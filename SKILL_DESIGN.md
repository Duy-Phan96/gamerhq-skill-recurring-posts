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

- list/get/create/update/set-active/delete v1 contracts.

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

Runtime API 1 currently has no public Management API form schema for labels,
field types, constraints or help text. The host therefore cannot derive the
desired interval label from this portable package through the SDK today.
Host-side integration should render **Every N minutes (min. 15)** (or equivalent)
and must still rely on the Skill's server-side 15-minute validation.

The missing future SDK/host contract is a host-neutral management-form schema
that can declare an interval-minutes input and its minimum without importing
Skill-private classes or Discord UI objects.

## Delivery model

Known send failures may retry. A crash in the uncertain external-delivery window
favors avoiding duplicate catch-up messages rather than claiming exactly-once
Discord delivery.

## Security/privacy impact

Edit adds no capability and no new data class. Channel validation still goes through the public Discord port, audit writes remain administrative metadata only, and cross-guild access is not introduced.
