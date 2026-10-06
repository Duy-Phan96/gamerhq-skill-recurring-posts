# Release Checklist — Recurring Posts Skill

Use this before tagging or pinning a release of `gamerhq-skill-recurring-posts`.

## Identity

- [ ] Skill ID remains `recurring-posts`.
- [ ] Entry-point name remains `recurring-posts`.
- [ ] Distribution remains `gamerhq-skill-recurring-posts`.
- [ ] Runtime API compatibility is reviewed.
- [ ] Skill version follows semantic versioning.

## Permissions

- [ ] `[tool.gamerhq].capabilities` exactly matches `SkillManifest.permissions`.
- [ ] Every requested capability is still required.
- [ ] No new host/private imports were introduced.

## Persistence

- [ ] `posts.v1` compatibility is preserved or migrated deterministically.
- [ ] `recurring-post.execute.v1` remains compatible with persisted jobs, or a migration plan exists.
- [ ] Existing job keys remain under `post:<post-id>`.
- [ ] Disable remains non-destructive.

## Contracts

- [ ] Management API IDs remain versioned and documented, including `recurring-posts.describe.v1`, `recurring-posts.validate.v1`, `recurring-posts.update.v1` and `recurring-posts.delete-preview.v1`.
- [ ] Management UI Schema V1 still references only declared public Management APIs.
- [ ] Collection item fields remain host-neutral and cover name, channel, content, schedule and active state.
- [ ] Event IDs remain versioned and documented.
- [ ] Breaking payload/behavior changes use a new contract version.

## Tests

- [ ] Static source audit passes.
- [ ] Package metadata/manifest consistency passes.
- [ ] Offline unit tests pass.
- [ ] Describe/validate UX APIs are read-only and produce no storage, Scheduler or audit side effects.
- [ ] UX metadata still exposes the 15-minute interval minimum and exact schedule payload fields.
- [ ] Interval presets are valid convenience schedules and do not impose a maximum.
- [ ] Delete preview is read-only and accurately states configuration/job/message impact.
- [ ] List items expose the correct Edit, Pause/Resume and Delete-preview actions without persisting derived UI metadata.
- [ ] Python 3.12 CI passes.
- [ ] Python 3.14 CI passes.
- [ ] No Discord token or production state is required by tests.

## Release

- [ ] SDK dependency is pinned to a reviewed compatible release/commit.
- [ ] Package source/release is immutable and reviewable.
- [ ] Changelog/release notes describe user-visible changes.
- [ ] GamerHQ deployment pins the intended Skill release/commit.
- [ ] Rollback target is known before production rollout.

## Live acceptance after reviewed deployment

- [ ] Existing configuration is visible.
- [ ] Existing scheduled job survives restart.
- [ ] Existing `posts.v1` data loads without migration.
- [ ] Review the create form constraints from `recurring-posts.describe.v1`.
- [ ] Validate a harmless draft and confirm no post/job is created.
- [ ] Create one harmless recurring post.
- [ ] Edit its name/message/schedule and confirm the post ID and `post:<post-id>` job key stay unchanged.
- [ ] Confirm the interval UI communicates the 15-minute minimum once the host UI contract/integration supports it.
- [ ] Pause and resume it.
- [ ] Preview deletion and verify no state changes before confirmation.
- [ ] Delete the test configuration.
- [ ] Disable/re-enable the Skill and confirm configuration remains.
- [ ] `/server manage → Skills` shows external package provenance.

Live acceptance is not a replacement for offline CI.
