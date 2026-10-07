# Recurring Posts Skill repository instructions

This package is a portable GamerHQ Skill.

Follow the canonical GamerHQ Skill Developer Guide, Authoring Contract and
Review Checklist.

Hard rules:

- Keep Skill ID `recurring-posts` stable.
- Do not import Discord.py or GamerHQ bot/cogs/services/database/hosts/config.
- Use only public `skill_runtime` contracts.
- Keep configuration behind versioned Management APIs.
- Use Skill Storage and the shared Scheduler.
- Keep tests offline and token-free.
- Preserve `posts.v1`, scheduler job keys and handler IDs across compatible releases.

## Repository ownership and handoffs

This repository owns only the Recurring Posts Skill.

- Publish and version this Skill independently.
- Do not modify GamerHQ Host, gamerhq-web or another Skill repository from this project.
- If a missing Host/SDK capability blocks work, finish the local work, document the blocker and produce a handoff prompt for the target repository.
- Consume only released/public contracts from other repositories.
- GamerHQ may later choose to pin a reviewed immutable Skill release in its own repository.
