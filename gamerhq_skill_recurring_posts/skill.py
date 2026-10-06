"""Portable Recurring Posts reference Skill.

The Skill owns post configuration and uses only public Skill Runtime contracts.
Discord.py, GamerHQ database helpers and host services are intentionally absent.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
import time
import uuid
from collections.abc import Mapping
from typing import Any

from skill_runtime import (
    EventContract,
    EventEnvelope,
    SkillCapability,
    SkillEvents,
    ManagementApiContract,
    ManagementCollectionOperations,
    ManagementCollectionSchema,
    ManagementField,
    ManagementSection,
    ManagementUiSchema,
    SkillHealth,
    SkillManagementApis,
    SkillManifest,
)
from skill_runtime.contracts.schedule import (
    DailySchedule,
    IntervalSchedule,
    WeeklySchedule,
    schedule_from_dict,
    schedule_to_dict,
)

SKILL_ID = "recurring-posts"
HANDLER_ID = "recurring-post.execute.v1"
SENT_EVENT_ID = "recurring-post.sent.v1"
STORAGE_KEY = "posts.v1"
MAX_POSTS = 20
MAX_NAME_CHARS = 80
MAX_CONTENT_CHARS = 2000
MIN_INTERVAL_SECONDS = 15 * 60
LIST_API = "recurring-posts.list.v1"
GET_API = "recurring-posts.get.v1"
CREATE_API = "recurring-posts.create.v1"
DESCRIBE_API = "recurring-posts.describe.v1"
VALIDATE_API = "recurring-posts.validate.v1"
UPDATE_API = "recurring-posts.update.v1"
SET_ACTIVE_API = "recurring-posts.set-active.v1"
DELETE_PREVIEW_API = "recurring-posts.delete-preview.v1"
DELETE_API = "recurring-posts.delete.v1"

MANAGEMENT_UI = ManagementUiSchema(
    version="1",
    read_contract=LIST_API,
    write_contract=CREATE_API,
    sections=(
        ManagementSection(
            id="recurring-posts",
            title="Recurring Posts",
            description="Create and manage scheduled Discord messages.",
            fields=(
                ManagementField(
                    key="posts",
                    label="Recurring Posts",
                    type="collection",
                    config_path="posts",
                    collection=ManagementCollectionSchema(
                        operations=ManagementCollectionOperations(
                            list_contract=LIST_API,
                            create_contract=CREATE_API,
                            get_contract=GET_API,
                            validate_contract=VALIDATE_API,
                            update_contract=UPDATE_API,
                            set_active_contract=SET_ACTIVE_API,
                            delete_preview_contract=DELETE_PREVIEW_API,
                            delete_contract=DELETE_API,
                        ),
                        item_fields=(
                            ManagementField(
                                key="name",
                                label="Name",
                                type="string",
                                config_path="name",
                                description="A short internal name for this recurring post.",
                                required=True,
                            ),
                            ManagementField(
                                key="channel",
                                label="Destination channel",
                                type="discord_channel",
                                config_path="channelId",
                                required=True,
                            ),
                            ManagementField(
                                key="content",
                                label="Message",
                                type="long_text",
                                config_path="content",
                                required=True,
                            ),
                            ManagementField(
                                key="schedule",
                                label="Schedule",
                                type="schedule",
                                config_path="schedule",
                                required=True,
                            ),
                            ManagementField(
                                key="active",
                                label="Active",
                                type="boolean",
                                config_path="active",
                            ),
                        ),
                        item_id_path="id",
                        item_id_payload_key="postId",
                        title_path="managementSummary.title",
                        status_path="status",
                        summary_path="managementSummary.compact",
                        max_items=MAX_POSTS,
                    ),
                ),
            ),
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class RecurringPost:
    id: str
    name: str
    channel_id: int
    content: str
    schedule: Mapping[str, Any]
    active: bool = True
    pending_slot: int | None = None
    last_sent_slot: int | None = None
    last_message_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "channelId": self.channel_id,
            "content": self.content,
            "schedule": dict(self.schedule),
            "active": self.active,
            "pendingSlot": self.pending_slot,
            "lastSentSlot": self.last_sent_slot,
            "lastMessageId": self.last_message_id,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RecurringPost":
        try:
            post = cls(
                id=str(value["id"]),
                name=str(value["name"]),
                channel_id=int(value["channelId"]),
                content=str(value["content"]),
                schedule=dict(value["schedule"]),
                active=bool(value.get("active", True)),
                pending_slot=_optional_int(value.get("pendingSlot")),
                last_sent_slot=_optional_int(value.get("lastSentSlot")),
                last_message_id=_optional_int(value.get("lastMessageId")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Stored Recurring Posts configuration is invalid.") from exc
        _validate_post(post)
        return post


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not a valid integer.")
    return int(value)


def _validated_schedule(value: Mapping[str, Any]) -> dict[str, Any]:
    schedule = schedule_from_dict(value)
    if not isinstance(schedule, (IntervalSchedule, DailySchedule, WeeklySchedule)):
        raise ValueError("Recurring Posts supports interval, daily or weekly schedules.")
    if isinstance(schedule, IntervalSchedule) and schedule.seconds < MIN_INTERVAL_SECONDS:
        raise ValueError(
            f"Recurring Posts interval must be at least {MIN_INTERVAL_SECONDS // 60} minutes."
        )
    return schedule_to_dict(schedule)


def _validate_post(post: RecurringPost) -> None:
    if not post.id or len(post.id) > 64:
        raise ValueError("Recurring Post id is invalid.")
    if not post.name.strip() or len(post.name) > MAX_NAME_CHARS:
        raise ValueError(f"Recurring Post name must be 1-{MAX_NAME_CHARS} characters.")
    if post.channel_id <= 0:
        raise ValueError("Recurring Post channel must be positive.")
    if not post.content.strip():
        raise ValueError("Recurring Post content is required.")
    if len(post.content) > MAX_CONTENT_CHARS:
        raise ValueError(
            f"Recurring Post content exceeds Discord's {MAX_CONTENT_CHARS} character limit."
        )
    _validated_schedule(post.schedule)


_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def _schedule_summary(schedule: Mapping[str, Any]) -> str:
    schedule_type = str(schedule.get("type", ""))
    if schedule_type == "interval":
        minutes = int(schedule["seconds"]) // 60
        return f"Every {minutes} minute{'s' if minutes != 1 else ''}"
    if schedule_type == "daily":
        return (
            f"Daily at {int(schedule['hour']):02d}:{int(schedule['minute']):02d} "
            f"({schedule['timezone']})"
        )
    if schedule_type == "weekly":
        weekday = int(schedule["weekday"])
        return (
            f"{_WEEKDAYS[weekday]} at {int(schedule['hour']):02d}:"
            f"{int(schedule['minute']):02d} ({schedule['timezone']})"
        )
    return schedule_type or "Unknown schedule"


def _post_quick_actions(post: RecurringPost) -> list[dict[str, Any]]:
    active_action = {
        "id": "pause" if post.active else "resume",
        "label": "Pause" if post.active else "Resume",
        "managementApi": SET_ACTIVE_API,
        "payload": {"postId": post.id, "active": not post.active},
        "destructive": False,
    }
    return [
        {
            "id": "edit",
            "label": "Edit",
            "managementApi": GET_API,
            "payload": {"postId": post.id},
            "destructive": False,
            "flow": "review-edit",
        },
        active_action,
        {
            "id": "delete",
            "label": "Delete",
            "managementApi": DELETE_PREVIEW_API,
            "payload": {"postId": post.id},
            "destructive": True,
            "flow": "preview-confirm-delete",
        },
    ]


def _post_management_view(post: RecurringPost) -> dict[str, Any]:
    schedule_summary = _schedule_summary(post.schedule)
    status = "active" if post.active else "paused"
    return {
        **post.to_dict(),
        "status": status,
        "scheduleSummary": schedule_summary,
        "managementSummary": {
            "title": post.name,
            "status": status,
            "channelId": post.channel_id,
            "schedule": schedule_summary,
            "compact": f"{'Active' if post.active else 'Paused'} · {schedule_summary}",
        },
        "quickActions": _post_quick_actions(post),
    }


def _ux_contract() -> dict[str, Any]:
    return {
        "limits": {
            "maxPosts": MAX_POSTS,
            "nameMaxChars": MAX_NAME_CHARS,
            "contentMaxChars": MAX_CONTENT_CHARS,
            "intervalMinMinutes": MIN_INTERVAL_SECONDS // 60,
        },
        "fields": {
            "name": {
                "label": "Name",
                "required": True,
                "maxLength": MAX_NAME_CHARS,
                "help": "A short internal name so you can recognize this recurring post later.",
            },
            "channelId": {
                "label": "Destination channel",
                "required": True,
                "help": "Choose the Discord channel where the message should be posted.",
            },
            "content": {
                "label": "Message",
                "required": True,
                "maxLength": MAX_CONTENT_CHARS,
            },
            "active": {
                "label": "Status",
                "required": False,
                "default": True,
                "options": [
                    {"value": True, "label": "Active"},
                    {"value": False, "label": "Paused"},
                ],
            },
        },
        "schedules": {
            "interval": {
                "label": "Interval",
                "presets": [
                    {"label": "Every 15 min", "schedule": {"type": "interval", "seconds": 15 * 60}},
                    {"label": "Every 30 min", "schedule": {"type": "interval", "seconds": 30 * 60}},
                    {"label": "Every 1 hour", "schedule": {"type": "interval", "seconds": 60 * 60}},
                    {"label": "Every 3 hours", "schedule": {"type": "interval", "seconds": 3 * 60 * 60}},
                    {"label": "Every 6 hours", "schedule": {"type": "interval", "seconds": 6 * 60 * 60}},
                    {"label": "Every 12 hours", "schedule": {"type": "interval", "seconds": 12 * 60 * 60}},
                ],
                "fields": {
                    "seconds": {
                        "label": f"Every N minutes (min. {MIN_INTERVAL_SECONDS // 60})",
                        "required": True,
                        "inputUnit": "minutes",
                        "minimumInput": MIN_INTERVAL_SECONDS // 60,
                        "payloadUnit": "seconds",
                    }
                },
            },
            "daily": {
                "label": "Daily",
                "fields": {
                    "hour": {"label": "Hour", "required": True, "min": 0, "max": 23},
                    "minute": {"label": "Minute", "required": True, "min": 0, "max": 59},
                    "timezone": {
                        "label": "Timezone",
                        "required": True,
                        "help": "Use an IANA timezone such as Europe/Berlin.",
                    },
                },
            },
            "weekly": {
                "label": "Weekly",
                "fields": {
                    "weekday": {
                        "label": "Day",
                        "required": True,
                        "options": [
                            {"value": index, "label": label}
                            for index, label in enumerate(_WEEKDAYS)
                        ],
                    },
                    "hour": {"label": "Hour", "required": True, "min": 0, "max": 23},
                    "minute": {"label": "Minute", "required": True, "min": 0, "max": 59},
                    "timezone": {
                        "label": "Timezone",
                        "required": True,
                        "help": "Use an IANA timezone such as Europe/Berlin.",
                    },
                },
            },
        },
        "recommendedFlow": ["review", "validate", "confirm"],
        "listPresentation": {
            "style": "compact-cards",
            "primaryField": "managementSummary.title",
            "secondaryFields": [
                "managementSummary.status",
                "managementSummary.channelId",
                "managementSummary.schedule",
            ],
            "actionsField": "quickActions",
        },
    }


class RecurringPostsSkill:
    manifest = SkillManifest(
        id=SKILL_ID,
        name="Recurring Posts",
        version="1.2.1",
        runtime_api_version="1",
        description="Post configured messages automatically on interval, daily or weekly schedules.",
        author="GamerHQ",
        permissions=(
            SkillCapability.DISCORD_CHANNELS_READ.value,
            SkillCapability.DISCORD_MESSAGES_SEND.value,
            SkillCapability.SCHEDULER_JOBS.value,
            SkillCapability.STORAGE_SKILL.value,
            SkillCapability.EVENTS_EMIT.value,
            SkillCapability.AUDIT_WRITE.value,
        ),
        events=SkillEvents(
            emits=(
                EventContract(
                    SENT_EVENT_ID,
                    "Emitted after a configured recurring post is confirmed sent.",
                ),
            ),
        ),
        management_apis=SkillManagementApis(
            exposes=(
                ManagementApiContract(LIST_API, "List configured recurring posts."),
                ManagementApiContract(GET_API, "Read one recurring post."),
                ManagementApiContract(CREATE_API, "Create a recurring post."),
                ManagementApiContract(
                    DESCRIBE_API,
                    "Read host-neutral UX hints and configuration constraints.",
                ),
                ManagementApiContract(
                    VALIDATE_API,
                    "Validate and preview a recurring post without persisting it.",
                ),
                ManagementApiContract(UPDATE_API, "Update an existing recurring post without changing its identity."),
                ManagementApiContract(SET_ACTIVE_API, "Pause or resume a recurring post."),
                ManagementApiContract(
                    DELETE_PREVIEW_API,
                    "Preview the impact of deleting a recurring post without changing state.",
                ),
                ManagementApiContract(DELETE_API, "Delete a recurring post."),
            ),
        ),
        management_ui=MANAGEMENT_UI,
    )

    def __init__(self):
        self._locks: dict[int, asyncio.Lock] = {}

    def _lock(self, guild_id: int) -> asyncio.Lock:
        return self._locks.setdefault(guild_id, asyncio.Lock())

    async def register(self, ctx) -> None:
        ctx.scheduler.register_handler(HANDLER_ID, self._execute)
        ctx.management.expose(LIST_API, self._manage_list)
        ctx.management.expose(GET_API, self._manage_get)
        ctx.management.expose(CREATE_API, self._manage_create)
        ctx.management.expose(DESCRIBE_API, self._manage_describe)
        ctx.management.expose(VALIDATE_API, self._manage_validate)
        ctx.management.expose(UPDATE_API, self._manage_update)
        ctx.management.expose(SET_ACTIVE_API, self._manage_set_active)
        ctx.management.expose(DELETE_PREVIEW_API, self._manage_delete_preview)
        ctx.management.expose(DELETE_API, self._manage_delete)


    async def _manage_list(self, ctx, payload) -> Mapping[str, Any]:
        posts = await self.list_posts(ctx)
        return {"posts": [_post_management_view(post) for post in posts]}

    async def _manage_get(self, ctx, payload) -> Mapping[str, Any]:
        post_id = str(payload.get("postId", "")).strip()
        if not post_id:
            raise ValueError("postId is required.")
        post = await self.get_post(ctx, post_id)
        return {"post": _post_management_view(post)}

    async def _manage_describe(self, ctx, payload) -> Mapping[str, Any]:
        return _ux_contract()

    async def _manage_validate(self, ctx, payload) -> Mapping[str, Any]:
        try:
            name = str(payload["name"])
            channel_id = int(payload["channelId"])
            content = str(payload["content"])
            schedule = payload["schedule"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Malformed recurring post preview request.") from exc
        if not isinstance(schedule, Mapping):
            raise ValueError("schedule must be an object.")

        active = payload.get("active", True)
        if not isinstance(active, bool):
            raise ValueError("active must be a boolean when provided.")

        post_id = str(payload.get("postId", "")).strip()
        if post_id:
            existing = await self.get_post(ctx, post_id)
            if "active" not in payload:
                active = existing.active

        await ctx.discord.get_channel(channel_id=channel_id)
        normalized = _validated_schedule(schedule)
        preview = RecurringPost(
            id=post_id or "preview",
            name=name.strip(),
            channel_id=channel_id,
            content=content.strip(),
            schedule=normalized,
            active=active,
        )
        _validate_post(preview)
        view = _post_management_view(preview)
        if not post_id:
            view.pop("id", None)
        view.pop("pendingSlot", None)
        view.pop("lastSentSlot", None)
        view.pop("lastMessageId", None)
        return {"valid": True, "preview": view}

    async def _manage_create(self, ctx, payload) -> Mapping[str, Any]:
        try:
            name = str(payload["name"])
            channel_id = int(payload["channelId"])
            content = str(payload["content"])
            schedule = payload["schedule"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Malformed recurring post request.") from exc
        if not isinstance(schedule, Mapping):
            raise ValueError("schedule must be an object.")
        active = payload.get("active", True)
        if not isinstance(active, bool):
            raise ValueError("active must be a boolean when provided.")
        post = await self.create_post(
            ctx,
            name=name,
            channel_id=channel_id,
            content=content,
            schedule=schedule,
            active=active,
        )
        return {"post": _post_management_view(post)}

    async def _manage_update(self, ctx, payload) -> Mapping[str, Any]:
        try:
            post_id = str(payload["postId"]).strip()
            name = str(payload["name"])
            channel_id = int(payload["channelId"])
            content = str(payload["content"])
            schedule = payload["schedule"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Malformed recurring post update request.") from exc
        if not post_id:
            raise ValueError("postId is required.")
        if not isinstance(schedule, Mapping):
            raise ValueError("schedule must be an object.")
        active = payload.get("active")
        if active is not None and not isinstance(active, bool):
            raise ValueError("active must be a boolean when provided.")
        post = await self.update_post(
            ctx,
            post_id=post_id,
            name=name,
            channel_id=channel_id,
            content=content,
            schedule=schedule,
            active=active,
        )
        return {"post": _post_management_view(post)}

    async def _manage_set_active(self, ctx, payload) -> Mapping[str, Any]:
        post_id = str(payload.get("postId", "")).strip()
        active = payload.get("active")
        if not post_id or not isinstance(active, bool):
            raise ValueError("postId and boolean active are required.")
        post = await self.set_active(ctx, post_id=post_id, active=active)
        return {"post": _post_management_view(post)}

    async def _manage_delete_preview(self, ctx, payload) -> Mapping[str, Any]:
        post_id = str(payload.get("postId", "")).strip()
        if not post_id:
            raise ValueError("postId is required.")
        post = await self.get_post(ctx, post_id)
        return {
            "post": _post_management_view(post),
            "warning": (
                "Deleting this recurring post removes its configuration and scheduler job. "
                "This action cannot be undone by the Skill."
            ),
            "impact": {
                "configurationRemoved": True,
                "schedulerJobRemoved": True,
                "previousDiscordMessagesDeleted": False,
            },
            "confirmation": {
                "required": True,
                "actionLabel": "Delete recurring post",
                "confirmText": post.name,
            },
        }

    async def _manage_delete(self, ctx, payload) -> Mapping[str, Any]:
        post_id = str(payload.get("postId", "")).strip()
        if not post_id:
            raise ValueError("postId is required.")
        await self.delete_post(ctx, post_id=post_id)
        return {"deleted": True, "postId": post_id}

    async def enable(self, ctx) -> None:
        await ctx.audit.write(action="enabled")

    async def disable(self, ctx) -> None:
        # Jobs deliberately remain persisted. The shared Scheduler's existing
        # disabled-Skill gate prevents execution and preserves safe re-enable.
        await ctx.audit.write(action="disabled")

    async def start(self, ctx) -> None:
        # No private loop: all future work is owned by scheduler.jobs.
        return None

    async def stop(self, ctx) -> None:
        return None

    async def health_check(self, ctx) -> SkillHealth:
        posts = await self.list_posts(ctx)
        active = sum(post.active for post in posts)
        return SkillHealth("PASS", f"{active} active recurring post(s), {len(posts)} configured.")

    async def _load(self, ctx) -> dict[str, RecurringPost]:
        raw = await ctx.storage.get(STORAGE_KEY)
        if raw is None:
            return {}
        if not isinstance(raw, Mapping):
            raise ValueError("Stored Recurring Posts configuration is invalid.")
        result: dict[str, RecurringPost] = {}
        for post_id, value in raw.items():
            if not isinstance(value, Mapping):
                raise ValueError("Stored Recurring Posts configuration is invalid.")
            post = RecurringPost.from_dict(value)
            if post.id != str(post_id):
                raise ValueError("Stored Recurring Posts identity is inconsistent.")
            result[post.id] = post
        return result

    async def _store(self, ctx, posts: Mapping[str, RecurringPost]) -> None:
        await ctx.storage.set(
            STORAGE_KEY,
            {post_id: post.to_dict() for post_id, post in sorted(posts.items())},
        )

    async def list_posts(self, ctx) -> tuple[RecurringPost, ...]:
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
        return tuple(sorted(posts.values(), key=lambda post: (post.name.casefold(), post.id)))

    async def get_post(self, ctx, post_id: str) -> RecurringPost:
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            try:
                return posts[post_id]
            except KeyError as exc:
                raise KeyError("Recurring Post does not exist.") from exc

    async def create_post(
        self,
        ctx,
        *,
        name: str,
        channel_id: int,
        content: str,
        schedule: Mapping[str, Any],
        active: bool = True,
    ) -> RecurringPost:
        await ctx.discord.get_channel(channel_id=channel_id)
        normalized = _validated_schedule(schedule)
        post = RecurringPost(
            id=uuid.uuid4().hex,
            name=name.strip(),
            channel_id=int(channel_id),
            content=content.strip(),
            schedule=normalized,
            active=bool(active),
        )
        _validate_post(post)

        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            if len(posts) >= MAX_POSTS:
                raise ValueError(f"Recurring Posts is limited to {MAX_POSTS} posts per server.")
            posts[post.id] = post
            await self._store(ctx, posts)
            try:
                if post.active:
                    await self._schedule(ctx, post)
            except Exception:
                posts.pop(post.id, None)
                await self._store(ctx, posts)
                raise

        await ctx.audit.write(
            action="post-created",
            target=post.id,
            metadata={"channelId": post.channel_id, "scheduleType": post.schedule["type"]},
        )
        return post

    async def update_post(
        self,
        ctx,
        *,
        post_id: str,
        name: str,
        channel_id: int,
        content: str,
        schedule: Mapping[str, Any],
        active: bool | None = None,
    ) -> RecurringPost:
        await ctx.discord.get_channel(channel_id=channel_id)
        normalized = _validated_schedule(schedule)

        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            if post_id not in posts:
                raise KeyError("Recurring Post does not exist.")
            previous = posts[post_id]
            updated = replace(
                previous,
                name=name.strip(),
                channel_id=int(channel_id),
                content=content.strip(),
                schedule=normalized,
                active=previous.active if active is None else active,
                pending_slot=None,
            )
            _validate_post(updated)
            posts[post_id] = updated
            await self._store(ctx, posts)
            try:
                if updated.active:
                    await self._schedule(ctx, updated)
                else:
                    await ctx.scheduler.remove_job(key=self._job_key(updated.id))
            except Exception:
                posts[post_id] = previous
                await self._store(ctx, posts)
                if previous.active:
                    await self._schedule(ctx, previous)
                else:
                    await ctx.scheduler.remove_job(key=self._job_key(previous.id))
                raise

        await ctx.audit.write(
            action="post-updated",
            target=updated.id,
            metadata={"channelId": updated.channel_id, "scheduleType": updated.schedule["type"]},
        )
        return updated

    async def set_active(self, ctx, *, post_id: str, active: bool) -> RecurringPost:
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            if post_id not in posts:
                raise KeyError("Recurring Post does not exist.")
            previous = posts[post_id]
            updated = replace(previous, active=bool(active), pending_slot=None)
            posts[post_id] = updated
            await self._store(ctx, posts)
            try:
                if updated.active:
                    await self._schedule(ctx, updated)
                else:
                    await ctx.scheduler.remove_job(key=self._job_key(updated.id))
            except Exception:
                posts[post_id] = previous
                await self._store(ctx, posts)
                raise

        await ctx.audit.write(
            action="post-resumed" if updated.active else "post-paused",
            target=updated.id,
        )
        return updated

    async def delete_post(self, ctx, *, post_id: str) -> None:
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            if post_id not in posts:
                raise KeyError("Recurring Post does not exist.")
            await ctx.scheduler.remove_job(key=self._job_key(post_id))
            posts.pop(post_id)
            await self._store(ctx, posts)
        await ctx.audit.write(action="post-deleted", target=post_id)

    async def _schedule(self, ctx, post: RecurringPost) -> None:
        await ctx.scheduler.upsert_job(
            key=self._job_key(post.id),
            handler_id=HANDLER_ID,
            schedule=post.schedule,
            payload={"postId": post.id},
        )

    @staticmethod
    def _job_key(post_id: str) -> str:
        return f"post:{post_id}"

    async def _execute(self, ctx, job) -> None:
        post_id = str(job.payload.get("postId", ""))
        if not post_id:
            return

        slot = int(job.next_run_at)
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            post = posts.get(post_id)
            if post is None or not post.active:
                await ctx.scheduler.remove_job(key=self._job_key(post_id))
                return
            if post.last_sent_slot == slot or post.pending_slot == slot:
                return
            post = replace(post, pending_slot=slot)
            posts[post_id] = post
            await self._store(ctx, posts)

        try:
            message_id = await ctx.discord.send_message(
                channel_id=post.channel_id,
                content=post.content,
            )
        except Exception:
            # A known send failure clears the reservation so the Scheduler may
            # retry. If the process dies after reservation but around delivery,
            # the reservation survives and favors no duplicate over catch-up.
            async with self._lock(ctx.guild_id):
                posts = await self._load(ctx)
                current = posts.get(post_id)
                if current is not None and current.pending_slot == slot:
                    posts[post_id] = replace(current, pending_slot=None)
                    await self._store(ctx, posts)
            raise

        sent_at = int(time.time())
        async with self._lock(ctx.guild_id):
            posts = await self._load(ctx)
            current = posts.get(post_id)
            if current is not None:
                posts[post_id] = replace(
                    current,
                    pending_slot=None,
                    last_sent_slot=slot,
                    last_message_id=int(message_id),
                )
                await self._store(ctx, posts)

        await ctx.events.emit(EventEnvelope(
            event_id=SENT_EVENT_ID,
            producer_skill_id=SKILL_ID,
            guild_id=ctx.guild_id,
            occurred_at=sent_at,
            payload={
                "postId": post_id,
                "channelId": post.channel_id,
                "messageId": int(message_id),
                "scheduledFor": slot,
            },
        ))
