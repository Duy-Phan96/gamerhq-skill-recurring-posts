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
- `recurring-posts.update.v1`
- `recurring-posts.set-active.v1`
- `recurring-posts.delete.v1`

The host UI must use these management contracts. It must not import this
package's private models or implementation.

`recurring-posts.update.v1` updates an existing post in place. The request keeps
the same `postId` and accepts `name`, `channelId`, `content`, `schedule`, and
optional boolean `active`. Compatible edits preserve the scheduler identity
`post:<post-id>` and use scheduler upsert rather than delete + recreate.

Interval schedules are validated server-side with a minimum of 15 minutes.

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

## Host UI note

The current Runtime API 1 `ManagementApiContract` exposes only an operation ID
and description; it does not provide a public form/input-schema contract.
Therefore this Skill cannot portably define the rendered Discord field label
for interval minutes. A host UI should display **Every N minutes (min. 15)** (or
equivalent) when integrating the Skill, while the Skill's 15-minute server-side
validation remains authoritative. A future generic Skill Builder needs a public
management-form schema in the SDK rather than private host assumptions.
