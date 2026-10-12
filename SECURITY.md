# Security Policy

Security reports for Recurring Posts should protect Discord communities, host
operators, and users from unnecessary disclosure.

## Supported code

Security fixes are prioritized for the current `main` line and the most recent
published Skill release.

Older versions may receive guidance or a recommended upgrade path rather than a
backport unless there is a strong compatibility reason.

## Reporting a vulnerability

Do not publish sensitive vulnerability details, credentials, private community
data, or exploitable reproduction material in a public Issue.

Preferred process:

1. use GitHub's private vulnerability-reporting / Security Advisory flow when it
   is available for this repository;
2. if a private GitHub reporting flow is not available, open a minimal public
   Issue stating that you need a private security-reporting channel;
3. do not include the exploit, tokens, private IDs, production data, or other
   sensitive details in that public Issue.

A useful private report should include:

- affected Skill version or immutable commit;
- affected Runtime/SDK version when relevant;
- impact and realistic attack preconditions;
- minimal reproduction steps using synthetic data;
- whether the issue affects confidentiality, integrity, availability, capability
  boundaries, guild isolation, or scheduler/storage behavior;
- any known safe workaround.

## Security boundaries

Recurring Posts is a portable Skill and must operate only through public
`skill_runtime` contracts.

Portable Skill code must not directly access:

- Discord.py client internals;
- GamerHQ Host services or database modules;
- raw bot tokens;
- production environment files;
- another Skill's private implementation;
- another guild's or Skill's scheduler/storage namespace.

The host remains authoritative for capability enforcement and guild scoping.

## Required capabilities

The current Skill declares:

- `discord.channels.read`
- `discord.messages.send`
- `scheduler.jobs`
- `storage.skill`
- `events.emit`
- `audit.write`

New capabilities require explicit architectural and security justification.

## Data handled by the Skill

Recurring Posts stores Skill-owned configuration and delivery state under
`posts.v1`, including:

- post IDs and internal names;
- Discord destination channel IDs;
- configured message content;
- schedule configuration;
- active/paused state;
- scheduler delivery reservation / confirmation metadata;
- last confirmed Discord message ID.

This repository must not include real production `posts.v1` content in tests,
examples, Issues, logs, or documentation.

## Secrets

Recurring Posts currently does not require its own external provider secrets.

Never commit:

- Discord bot tokens;
- API keys;
- passwords;
- real `.env` contents;
- private credentials;
- production database files;
- backups;
- private logs or transcripts.

Use synthetic values in tests and documentation.

## Discord message safety

Message destinations are validated through the public guild-scoped Discord port.

The Skill must preserve:

- the Discord content-length limit;
- guild scoping;
- capability checks;
- host-mediated access.

A Skill must not obtain or cache raw Discord client objects to bypass these
controls.

## Scheduler safety

Recurring Posts uses the shared public Scheduler and must not create a competing
private persistent loop.

Security-relevant invariants include:

- stable job identity `post:<post-id>`;
- scheduler operations remain scoped to the current Skill/guild;
- persisted delivery state is used to reduce duplicate visible sends;
- external delivery is not falsely described as exactly-once;
- paused/disabled state must not silently delete configuration.

Scheduler payloads, leases, claim tokens, or Host database details must not be
exposed through Skill management responses unless a public contract explicitly
defines a safe representation.

## Management API safety

Management contracts are trusted administration surfaces, but they must still:

- validate required input;
- preserve guild/Skill scoping;
- avoid returning secrets or Host-private objects;
- keep destructive actions explicit;
- avoid changing state in read-only preview/describe operations.

Delete remains preceded by a read-only impact preview in the intended UX flow.

## Test Send

`recurring-posts.test-send.v1` creates a real Discord message when invoked by a
consumer.

It must not:

- create or modify a recurring Scheduler job;
- update recurring delivery slots;
- emit the scheduled-delivery event;
- report successful audit state before Discord confirms the send.

Consumers should treat Test Send as an explicit externally visible action.

## Dependency security

The public GamerHQ Skill Runtime/SDK is a security boundary.

Dependency changes should:

- use a reviewed compatible release or immutable commit;
- preserve reproducible CI;
- avoid moving development branches as production dependencies;
- document capability or public-contract changes;
- run package conformance/source-portability tests.

## Vulnerability classes of particular interest

Please report issues involving:

- cross-guild access;
- cross-Skill storage or scheduler access;
- unauthorized Discord message delivery;
- capability bypass;
- destructive state loss;
- duplicate-send amplification;
- injection of Host-private objects or executable UI/code;
- secret or private-data exposure;
- dependency confusion or unsafe package loading;
- malformed persisted state causing unsafe behavior.

## Disclosure and remediation

Security fixes should be scoped to the owning repository.

If a vulnerability is actually caused by a public Runtime/SDK or Host contract,
this repository should document the dependency and create a handoff to the
repository that owns that contract rather than patching private Host internals
here.

After a fix is reviewed:

- add regression coverage;
- document compatibility/migration impact;
- publish a fixed Skill release when appropriate;
- identify the safe upgrade path;
- avoid disclosing unnecessary private community data in release notes.

## Production boundary

This repository does not operate the GamerHQ production server.

A security fix merged here is not live in any consumer until that consumer
independently upgrades to the reviewed Skill release.
