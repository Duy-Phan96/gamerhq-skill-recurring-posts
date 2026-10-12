# Release Process — Recurring Posts

This document defines the repository-local release process for
`gamerhq-skill-recurring-posts`.

It does not control GamerHQ Host releases, consumer deployment, production
infrastructure, or another repository's lifecycle.

## Release principles

1. This Skill releases independently.
2. `main` is the reviewed release branch.
3. Every release is tied to one immutable commit.
4. Semantic versioning applies to the Skill package.
5. Runtime API versioning is separate from Skill package versioning.
6. Public compatibility identities must remain stable across compatible releases.
7. A green Skill release does not imply a GamerHQ production deployment.

## Versioning

Use Semantic Versioning.

### Patch

Use a patch release for backward-compatible corrections and small additive
presentation/metadata improvements that do not materially expand the public
feature surface.

Examples:

- validation bug fix;
- corrected human-readable metadata;
- documentation-only compatibility correction.

### Minor

Use a minor release for backward-compatible public functionality.

Examples:

- new Management API;
- new host-neutral management behavior;
- new supported public SDK functionality;
- additive management status fields with meaningful new capability.

### Major

Use a major release only for an intentional breaking public compatibility change.

Examples:

- incompatible Management API payload change;
- storage identity break;
- changed scheduler job identity;
- removed public contract without compatibility path.

## Compatibility-critical identities

Review these before every release:

```text
Skill ID: recurring-posts
Distribution: gamerhq-skill-recurring-posts
Runtime API: 1
Storage key: posts.v1
Scheduler handler: recurring-post.execute.v1
Scheduler job key: post:<post-id>
Event: recurring-post.sent.v1
```

A compatible release should preserve them.

## Dependency policy

The public GamerHQ Skill Runtime/SDK is an external dependency.

Before changing the supported SDK range:

1. verify the required public contract exists in a reviewed upstream release or
   intentionally consumable immutable commit;
2. update `pyproject.toml` with the supported range;
3. update CI to pin the reviewed dependency used for validation;
4. run package/manifest conformance tests;
5. document the compatibility change in README, PROJECT_STATUS, ROADMAP and
   CHANGELOG when material.

Do not raise the supported SDK range merely because functionality exists on a
moving upstream development branch.

## Release preparation

Before starting a release:

- confirm the intended scope is complete;
- confirm there are no unrelated changes in the release branch;
- review open Issues associated with the release;
- review `PROJECT_STATUS.md` and `ROADMAP.md`;
- update package version in `pyproject.toml` and `SkillManifest`;
- update contract-version expectations in tests where required;
- update README / SKILL_DESIGN / CHANGELOG;
- review `RELEASE_CHECKLIST.md`.

## Required quality gates

The release candidate must pass:

- Python 3.12 CI;
- Python 3.14 CI;
- dependency check;
- offline tests;
- package metadata / manifest consistency;
- portable source audit / conformance checks where applicable.

Tests must remain token-free and production-independent.

## Release review

Review the final diff for:

- accidental public contract breakage;
- storage migration impact;
- scheduler/job identity changes;
- event behavior changes;
- capability escalation;
- new Host/private imports;
- unsupported SDK assumptions;
- stale documentation;
- unrelated feature work.

If another repository must change, stop at a handoff. Do not make that change
from this repository.

## Merge

Merge the reviewed PR into `main` only after required CI is green.

Record the resulting immutable merge/squash commit SHA.

The immutable commit is the source reference consumers may pin.

## Tagging

Create an annotated version tag from the exact reviewed release commit.

Recommended format:

```text
v1.4.0
```

The tag must point to the intended immutable release commit, not a moving branch.

Verify before publishing:

```bash
git show --no-patch --oneline <release-commit>
git tag --points-at <release-commit>
```

Do not move an existing published version tag.

## GitHub Release

Create a GitHub Release from the version tag.

Release notes should include:

- version;
- immutable commit;
- Runtime API compatibility;
- supported SDK range;
- user-visible changes;
- public contract impact;
- storage/migration impact;
- scheduler/event impact;
- capability/security impact;
- known limitations;
- upgrade/rollback note.

Do not copy the entire CHANGELOG when a concise release summary is sufficient.

## Consumer handoff

After this Skill release is published, consumers decide independently whether to
upgrade.

A handoff to a consumer may include:

```text
Skill version
Immutable commit
Runtime API
Supported SDK range
Public contract changes
Storage/migration impact
Capability impact
Acceptance guidance
```

Do not modify the consuming repository from this project.

## Rollback

A compatible rollback normally means pinning the previous reviewed Skill release
or immutable commit in the consumer's own repository.

Before release, identify the previous known-good release.

A rollback must not assume storage can be discarded. `posts.v1` compatibility
must be understood before moving backward across versions.

If a release introduces a storage migration in the future, document backward
compatibility explicitly before publication.

## Post-release repository actions

After publishing a release:

- mark the matching roadmap milestone/status appropriately;
- update `PROJECT_STATUS.md`;
- close completed Issues;
- remove merged feature branches where practical;
- ensure `CHANGELOG.md` has a fresh `Unreleased` section;
- record any follow-up work as Issues rather than hiding it in release notes.

## Release status vocabulary

Use these states consistently:

- **READY FOR REVIEW** — implementation complete, review/CI pending;
- **READY FOR RELEASE** — reviewed and green, publication pending;
- **RELEASED** — immutable release/tag has been published;
- **BLOCKED BY HANDOFF** — another repository must publish a required contract;
- **WAITING FOR PUBLIC CONTRACT** — required upstream public API is not yet consumable.

Do not call a version `RELEASED` merely because its code exists on `main`.

## Owner actions

Tagging and GitHub Release publication are explicit repository-owner actions.

This repository's automation may validate a release candidate, but release
publication should remain deliberate and reviewable.
