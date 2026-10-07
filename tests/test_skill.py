import unittest
from types import SimpleNamespace

from gamerhq_skill_recurring_posts import (
    CREATE_API,
    DESCRIBE_API,
    DELETE_API,
    DELETE_PREVIEW_API,
    GET_API,
    HANDLER_ID,
    LIST_API,
    MANAGEMENT_UI,
    MIN_INTERVAL_SECONDS,
    SET_ACTIVE_API,
    TEST_SEND_API,
    UPDATE_API,
    VALIDATE_API,
    RecurringPostsSkill,
)


class FakeStorage:
    def __init__(self):
        self.values = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value):
        self.values[key] = value

    async def delete(self, key):
        self.values.pop(key, None)


class FakeScheduler:
    def __init__(self):
        self.jobs = {}
        self.removed = []
        self.upserts = []
        self.fail_upsert = False
        self.fail_remove = False

    async def upsert_job(self, *, key, handler_id, schedule, payload):
        if self.fail_upsert:
            raise RuntimeError("synthetic scheduler upsert failure")
        self.upserts.append(key)
        self.jobs[key] = {
            "handler_id": handler_id,
            "schedule": dict(schedule),
            "payload": dict(payload),
        }

    async def remove_job(self, *, key):
        if self.fail_remove:
            raise RuntimeError("synthetic scheduler remove failure")
        self.removed.append(key)
        self.jobs.pop(key, None)


class FakeDiscord:
    def __init__(self):
        self.channels = {10: SimpleNamespace(id=10, name="announcements", kind="text")}
        self.sent = []
        self.fail = False

    async def get_channel(self, *, channel_id):
        if channel_id not in self.channels:
            raise KeyError("missing")
        return self.channels[channel_id]

    async def send_message(self, *, channel_id, content=None, embed=None, allowed_mentions=None):
        if self.fail:
            raise RuntimeError("synthetic")
        self.sent.append((channel_id, content))
        return 9000 + len(self.sent)


class FakeAudit:
    def __init__(self):
        self.calls = []

    async def write(self, **kwargs):
        self.calls.append(kwargs)


class FakeEvents:
    def __init__(self):
        self.events = []

    async def emit(self, event):
        self.events.append(event)
        return SimpleNamespace(delivered=0, failed_consumers=())


class FakeRegistrationScheduler:
    def __init__(self):
        self.handlers = {}

    def register_handler(self, handler_id, handler):
        self.handlers[handler_id] = handler


class FakeManagementRegistration:
    def __init__(self):
        self.handlers = {}

    def expose(self, contract_id, handler):
        self.handlers[contract_id] = handler


class RecurringPostsSkillTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.skill = RecurringPostsSkill()
        self.storage = FakeStorage()
        self.scheduler = FakeScheduler()
        self.discord = FakeDiscord()
        self.audit = FakeAudit()
        self.events = FakeEvents()
        self.ctx = SimpleNamespace(
            guild_id=1,
            skill_id="recurring-posts",
            storage=self.storage,
            scheduler=self.scheduler,
            discord=self.discord,
            audit=self.audit,
            events=self.events,
        )

    async def create(self, **overrides):
        values = dict(
            name="Rules reminder",
            channel_id=10,
            content="Please remember the rules.",
            schedule={"type": "interval", "seconds": MIN_INTERVAL_SECONDS},
        )
        values.update(overrides)
        return await self.skill.create_post(self.ctx, **values)

    def test_manifest_declares_generic_collection_management_schema(self):
        schema = self.skill.manifest.management_ui
        self.assertIs(schema, MANAGEMENT_UI)
        self.assertEqual(schema.version, "1")
        self.assertEqual(schema.read_contract, LIST_API)
        self.assertEqual(schema.write_contract, CREATE_API)

        self.assertEqual(len(schema.sections), 1)
        collection_field = schema.sections[0].fields[0]
        self.assertEqual(collection_field.type, "collection")
        self.assertEqual(collection_field.config_path, "posts")

        collection = collection_field.collection
        self.assertIsNotNone(collection)
        self.assertEqual(collection.operations.list_contract, LIST_API)
        self.assertEqual(collection.operations.create_contract, CREATE_API)
        self.assertEqual(collection.operations.get_contract, GET_API)
        self.assertEqual(collection.operations.describe_contract, DESCRIBE_API)
        self.assertEqual(collection.operations.validate_contract, VALIDATE_API)
        self.assertEqual(collection.operations.update_contract, UPDATE_API)
        self.assertEqual(collection.operations.set_active_contract, SET_ACTIVE_API)
        self.assertEqual(collection.item_id_payload_key, "postId")
        self.assertEqual(collection.item_read_path, "post")
        self.assertEqual(collection.schedule_hints_path, "schedules")
        self.assertEqual(collection.operations.delete_preview_contract, DELETE_PREVIEW_API)
        self.assertEqual(collection.operations.delete_contract, DELETE_API)
        self.assertEqual(collection.max_items, 20)
        self.assertEqual(collection.title_path, "managementSummary.title")
        self.assertEqual(collection.summary_path, "managementSummary.compact")

        fields = {field.config_path: field for field in collection.item_fields}
        self.assertEqual(fields["name"].type, "string")
        self.assertEqual(fields["channelId"].type, "discord_channel")
        self.assertEqual(fields["content"].type, "long_text")
        self.assertEqual(fields["schedule"].type, "schedule")
        self.assertEqual(fields["active"].type, "boolean")

    async def test_registration_binds_scheduler_and_management_contracts(self):
        scheduler = FakeRegistrationScheduler()
        management = FakeManagementRegistration()
        await self.skill.register(
            SimpleNamespace(scheduler=scheduler, management=management)
        )
        self.assertEqual(tuple(scheduler.handlers), (HANDLER_ID,))
        self.assertEqual(
            set(management.handlers),
            {LIST_API, GET_API, CREATE_API, DESCRIBE_API, VALIDATE_API, TEST_SEND_API, UPDATE_API, SET_ACTIVE_API, DELETE_PREVIEW_API, DELETE_API},
        )

    async def test_describe_exposes_host_neutral_ux_constraints(self):
        result = await self.skill._manage_describe(self.ctx, {})

        self.assertEqual(result["limits"]["intervalMinMinutes"], 15)
        self.assertEqual(result["limits"]["maxPosts"], 20)
        self.assertEqual(
            result["schedules"]["interval"]["fields"]["seconds"]["label"],
            "Every N minutes (min. 15)",
        )
        self.assertEqual(result["recommendedFlow"], ["review", "validate", "confirm"])
        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertEqual(self.scheduler.jobs, {})
        self.assertEqual(self.audit.calls, [])

    async def test_describe_exposes_test_send_action(self):
        result = await self.skill._manage_describe(self.ctx, {})
        action = result["actions"]["testSend"]

        self.assertEqual(action["managementApi"], TEST_SEND_API)
        self.assertEqual(action["label"], "Send test")
        self.assertEqual(action["savedPayload"], {"postId": "<post-id>"})
        self.assertEqual(
            action["draftPayload"],
            {"channelId": "<channel-id>", "content": "<message>"},
        )

    async def test_test_send_saved_post_does_not_change_recurring_state(self):
        post = await self.create(active=False)
        stored_before = self.storage.values["posts.v1"].copy()
        jobs_before = dict(self.scheduler.jobs)
        events_before = list(self.events.events)
        audit_count_before = len(self.audit.calls)

        result = await self.skill._manage_test_send(
            self.ctx,
            {"postId": post.id},
        )

        self.assertTrue(result["sent"])
        self.assertEqual(result["source"], "saved")
        self.assertEqual(result["postId"], post.id)
        self.assertEqual(result["channelId"], 10)
        self.assertEqual(result["messageId"], 9001)
        self.assertEqual(self.discord.sent, [(10, "Please remember the rules.")])
        self.assertEqual(self.storage.values["posts.v1"], stored_before)
        self.assertEqual(self.scheduler.jobs, jobs_before)
        self.assertEqual(self.events.events, events_before)
        self.assertEqual(len(self.audit.calls), audit_count_before + 1)
        self.assertEqual(self.audit.calls[-1]["action"], "post-test-sent")

    async def test_test_send_draft_is_one_shot_and_does_not_persist(self):
        result = await self.skill._manage_test_send(
            self.ctx,
            {"channelId": 10, "content": "Draft preview message."},
        )

        self.assertEqual(
            result,
            {
                "sent": True,
                "source": "draft",
                "channelId": 10,
                "messageId": 9001,
            },
        )
        self.assertEqual(self.discord.sent, [(10, "Draft preview message.")])
        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertEqual(self.scheduler.jobs, {})
        self.assertEqual(self.events.events, [])
        self.assertEqual(self.audit.calls[-1]["metadata"]["source"], "draft")

    async def test_test_send_rejects_ambiguous_or_invalid_payloads(self):
        post = await self.create(active=False)
        sent_before = list(self.discord.sent)

        with self.assertRaisesRegex(ValueError, "either postId or draft"):
            await self.skill._manage_test_send(
                self.ctx,
                {"postId": post.id, "channelId": 10, "content": "Ambiguous"},
            )
        with self.assertRaisesRegex(ValueError, "requires postId or draft"):
            await self.skill._manage_test_send(self.ctx, {})
        with self.assertRaisesRegex(ValueError, "2000 character limit"):
            await self.skill._manage_test_send(
                self.ctx,
                {"channelId": 10, "content": "x" * 2001},
            )

        self.assertEqual(self.discord.sent, sent_before)

    async def test_test_send_missing_post_or_channel_fails_closed(self):
        with self.assertRaisesRegex(KeyError, "does not exist"):
            await self.skill._manage_test_send(self.ctx, {"postId": "missing"})

        with self.assertRaises(KeyError):
            await self.skill._manage_test_send(
                self.ctx,
                {"channelId": 999, "content": "No destination."},
            )

        self.assertEqual(self.discord.sent, [])
        self.assertEqual(self.events.events, [])

    async def test_test_send_delivery_failure_does_not_audit_success(self):
        self.discord.fail = True

        with self.assertRaisesRegex(RuntimeError, "synthetic"):
            await self.skill._manage_test_send(
                self.ctx,
                {"channelId": 10, "content": "Fail safely."},
            )

        self.assertEqual(self.audit.calls, [])
        self.assertEqual(self.events.events, [])
        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertEqual(self.scheduler.jobs, {})

    async def test_validate_returns_preview_without_persisting_or_scheduling(self):
        result = await self.skill._manage_validate(
            self.ctx,
            {
                "name": "Rules reminder",
                "channelId": 10,
                "content": "Please remember the rules.",
                "schedule": {"type": "interval", "seconds": 30 * 60},
                "active": False,
            },
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["preview"]["status"], "paused")
        self.assertEqual(result["preview"]["scheduleSummary"], "Every 30 minutes")
        self.assertNotIn("id", result["preview"])
        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertEqual(self.scheduler.jobs, {})
        self.assertEqual(self.audit.calls, [])

    async def test_validate_reuses_existing_active_state_for_edit_preview(self):
        post = await self.create(active=False)

        result = await self.skill._manage_validate(
            self.ctx,
            {
                "postId": post.id,
                "name": "Edited reminder",
                "channelId": 10,
                "content": "Edited content.",
                "schedule": {
                    "type": "weekly",
                    "weekday": 0,
                    "hour": 9,
                    "minute": 5,
                    "timezone": "Europe/Berlin",
                },
            },
        )

        self.assertEqual(result["preview"]["id"], post.id)
        self.assertEqual(result["preview"]["status"], "paused")
        self.assertEqual(
            result["preview"]["scheduleSummary"],
            "Monday at 09:05 (Europe/Berlin)",
        )

    async def test_validate_enforces_interval_minimum_without_side_effects(self):
        with self.assertRaisesRegex(ValueError, "at least 15 minutes"):
            await self.skill._manage_validate(
                self.ctx,
                {
                    "name": "Too frequent",
                    "channelId": 10,
                    "content": "No.",
                    "schedule": {"type": "interval", "seconds": 14 * 60},
                },
            )

        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertEqual(self.scheduler.jobs, {})
        self.assertEqual(self.audit.calls, [])

    async def test_create_can_start_paused_and_returns_readable_status(self):
        result = await self.skill._manage_create(
            self.ctx,
            {
                "name": "Draft post",
                "channelId": 10,
                "content": "Not live yet.",
                "schedule": {"type": "interval", "seconds": MIN_INTERVAL_SECONDS},
                "active": False,
            },
        )

        self.assertFalse(result["post"]["active"])
        self.assertEqual(result["post"]["status"], "paused")
        self.assertEqual(result["post"]["scheduleSummary"], "Every 15 minutes")
        self.assertEqual(self.scheduler.jobs, {})

    async def test_describe_exposes_quick_interval_presets(self):
        result = await self.skill._manage_describe(self.ctx, {})
        presets = result["schedules"]["interval"]["presets"]

        self.assertEqual(
            [preset["label"] for preset in presets],
            [
                "Every 15 min",
                "Every 30 min",
                "Every 1 hour",
                "Every 3 hours",
                "Every 6 hours",
                "Every 12 hours",
            ],
        )
        self.assertEqual(presets[0]["schedule"]["seconds"], MIN_INTERVAL_SECONDS)
        self.assertEqual(presets[-1]["schedule"]["seconds"], 12 * 60 * 60)

    async def test_delete_preview_is_read_only_and_explains_impact(self):
        post = await self.create()
        jobs_before = dict(self.scheduler.jobs)
        audit_before = list(self.audit.calls)

        result = await self.skill._manage_delete_preview(
            self.ctx,
            {"postId": post.id},
        )

        self.assertEqual(result["post"]["id"], post.id)
        self.assertEqual(result["confirmation"]["confirmText"], post.name)
        self.assertTrue(result["confirmation"]["required"])
        self.assertTrue(result["impact"]["configurationRemoved"])
        self.assertTrue(result["impact"]["schedulerJobRemoved"])
        self.assertFalse(result["impact"]["previousDiscordMessagesDeleted"])
        self.assertIn("cannot be undone", result["warning"])
        self.assertEqual(await self.skill.get_post(self.ctx, post.id), post)
        self.assertEqual(self.scheduler.jobs, jobs_before)
        self.assertEqual(self.audit.calls, audit_before)

    async def test_management_view_reports_never_sent_without_guessing_timestamp(self):
        post = await self.create(active=False)

        item = (await self.skill._manage_get(self.ctx, {"postId": post.id}))["post"]

        self.assertEqual(item["deliveryStatus"]["state"], "never-sent")
        self.assertEqual(item["deliveryStatus"]["label"], "Never sent")
        self.assertFalse(item["deliveryStatus"]["hasConfirmedDelivery"])
        self.assertIsNone(item["deliveryStatus"]["lastConfirmedScheduledFor"])
        self.assertIsNone(item["deliveryStatus"]["lastMessageId"])
        self.assertEqual(item["managementSummary"]["delivery"], "Never sent")
        self.assertNotIn("deliveryStatus", self.storage.values["posts.v1"][post.id])

    async def test_management_view_reports_confirmed_delivery_from_existing_state(self):
        post = await self.create()
        job = SimpleNamespace(payload={"postId": post.id}, next_run_at=12345)

        await self.skill._execute(self.ctx, job)
        item = (await self.skill._manage_get(self.ctx, {"postId": post.id}))["post"]

        self.assertEqual(item["deliveryStatus"]["state"], "sent")
        self.assertEqual(item["deliveryStatus"]["label"], "Last send confirmed")
        self.assertTrue(item["deliveryStatus"]["hasConfirmedDelivery"])
        self.assertEqual(item["deliveryStatus"]["lastConfirmedScheduledFor"], 12345)
        self.assertEqual(item["deliveryStatus"]["lastMessageId"], 9001)
        self.assertIsNone(item["deliveryStatus"]["pendingScheduledFor"])
        self.assertEqual(item["managementSummary"]["delivery"], "Last send confirmed")

    async def test_management_view_prioritizes_pending_delivery_without_losing_last_confirmation(self):
        self.storage.values["posts.v1"] = {
            "post-1": {
                "id": "post-1",
                "name": "Pending reminder",
                "channelId": 10,
                "content": "Pending.",
                "schedule": {"type": "interval", "seconds": MIN_INTERVAL_SECONDS},
                "active": True,
                "pendingSlot": 222,
                "lastSentSlot": 111,
                "lastMessageId": 9001,
            }
        }

        item = (await self.skill._manage_get(self.ctx, {"postId": "post-1"}))["post"]

        self.assertEqual(item["deliveryStatus"]["state"], "pending")
        self.assertEqual(item["deliveryStatus"]["label"], "Delivery pending")
        self.assertEqual(item["deliveryStatus"]["pendingScheduledFor"], 222)
        self.assertEqual(item["deliveryStatus"]["lastConfirmedScheduledFor"], 111)
        self.assertEqual(item["deliveryStatus"]["lastMessageId"], 9001)
        self.assertTrue(item["deliveryStatus"]["hasConfirmedDelivery"])

    async def test_list_presentation_declares_delivery_summary_field(self):
        result = await self.skill._manage_describe(self.ctx, {})

        self.assertIn(
            "managementSummary.delivery",
            result["listPresentation"]["secondaryFields"],
        )

    async def test_list_returns_compact_management_summary_and_quick_actions(self):
        post = await self.create()

        result = await self.skill._manage_list(self.ctx, {})
        item = result["posts"][0]

        self.assertEqual(item["managementSummary"]["title"], post.name)
        self.assertEqual(item["managementSummary"]["status"], "active")
        self.assertEqual(item["managementSummary"]["channelId"], 10)
        self.assertEqual(item["managementSummary"]["schedule"], "Every 15 minutes")
        self.assertEqual(item["managementSummary"]["compact"], "Active · Every 15 minutes")

        actions = {action["id"]: action for action in item["quickActions"]}
        self.assertEqual(actions["edit"]["managementApi"], GET_API)
        self.assertEqual(actions["pause"]["managementApi"], SET_ACTIVE_API)
        self.assertEqual(
            actions["pause"]["payload"],
            {"postId": post.id, "active": False},
        )
        self.assertEqual(actions["test-send"]["managementApi"], TEST_SEND_API)
        self.assertEqual(actions["test-send"]["payload"], {"postId": post.id})
        self.assertFalse(actions["test-send"]["destructive"])
        self.assertTrue(actions["delete"]["destructive"])
        self.assertEqual(actions["delete"]["managementApi"], DELETE_PREVIEW_API)

    async def test_paused_list_item_offers_resume_instead_of_pause(self):
        post = await self.create(active=False)

        item = (await self.skill._manage_list(self.ctx, {}))["posts"][0]
        actions = {action["id"]: action for action in item["quickActions"]}

        self.assertEqual(item["managementSummary"]["compact"], "Paused · Every 15 minutes")
        self.assertIn("resume", actions)
        self.assertNotIn("pause", actions)
        self.assertEqual(
            actions["resume"]["payload"],
            {"postId": post.id, "active": True},
        )

    async def test_describe_declares_compact_card_list_presentation(self):
        result = await self.skill._manage_describe(self.ctx, {})

        presentation = result["listPresentation"]
        self.assertEqual(presentation["style"], "compact-cards")
        self.assertEqual(presentation["primaryField"], "managementSummary.title")
        self.assertEqual(presentation["actionsField"], "quickActions")

    async def test_management_contracts_drive_crud_without_private_host_access(self):
        created = await self.skill._manage_create(
            self.ctx,
            {
                "name": "Rules reminder",
                "channelId": 10,
                "content": "Please remember the rules.",
                "schedule": {"type": "interval", "seconds": MIN_INTERVAL_SECONDS},
            },
        )
        post_id = created["post"]["id"]

        listed = await self.skill._manage_list(self.ctx, {})
        self.assertEqual(len(listed["posts"]), 1)

        fetched = await self.skill._manage_get(self.ctx, {"postId": post_id})
        self.assertEqual(fetched["post"]["content"], "Please remember the rules.")

        updated = await self.skill._manage_update(
            self.ctx,
            {
                "postId": post_id,
                "name": "Updated reminder",
                "channelId": 10,
                "content": "Updated rules reminder.",
                "schedule": {"type": "interval", "seconds": 30 * 60},
            },
        )
        self.assertEqual(updated["post"]["id"], post_id)
        self.assertEqual(updated["post"]["content"], "Updated rules reminder.")

        paused = await self.skill._manage_set_active(
            self.ctx,
            {"postId": post_id, "active": False},
        )
        self.assertFalse(paused["post"]["active"])

        deleted = await self.skill._manage_delete(
            self.ctx,
            {"postId": post_id},
        )
        self.assertTrue(deleted["deleted"])
        self.assertEqual((await self.skill._manage_list(self.ctx, {}))["posts"], [])

    async def test_create_persists_configuration_and_upserts_scheduler_job(self):
        post = await self.create()
        stored = await self.skill.get_post(self.ctx, post.id)
        self.assertEqual(stored.content, "Please remember the rules.")
        job = self.scheduler.jobs[f"post:{post.id}"]
        self.assertEqual(job["handler_id"], HANDLER_ID)
        self.assertEqual(job["payload"], {"postId": post.id})
        self.assertEqual(job["schedule"]["seconds"], MIN_INTERVAL_SECONDS)

    async def test_interval_below_skill_antispam_minimum_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least 15 minutes"):
            await self.create(schedule={"type": "interval", "seconds": 60})
        self.assertEqual(self.scheduler.jobs, {})
        self.assertEqual(await self.skill.list_posts(self.ctx), ())


    async def test_update_preserves_post_and_scheduler_identity(self):
        post = await self.create()
        original_job_key = f"post:{post.id}"

        updated = await self.skill.update_post(
            self.ctx,
            post_id=post.id,
            name="Edited reminder",
            channel_id=10,
            content="Edited content.",
            schedule={"type": "interval", "seconds": 30 * 60},
        )

        self.assertEqual(updated.id, post.id)
        self.assertEqual(set(self.scheduler.jobs), {original_job_key})
        self.assertEqual(self.scheduler.jobs[original_job_key]["payload"], {"postId": post.id})
        self.assertEqual(self.scheduler.jobs[original_job_key]["schedule"]["seconds"], 30 * 60)
        self.assertEqual(len(await self.skill.list_posts(self.ctx)), 1)

    async def test_update_can_change_schedule_type_without_recreating_post(self):
        post = await self.create()

        updated = await self.skill.update_post(
            self.ctx,
            post_id=post.id,
            name=post.name,
            channel_id=post.channel_id,
            content=post.content,
            schedule={"type": "daily", "hour": 8, "minute": 15, "timezone": "Europe/Berlin"},
        )

        self.assertEqual(updated.id, post.id)
        self.assertEqual(updated.schedule["type"], "daily")
        self.assertIn(f"post:{post.id}", self.scheduler.jobs)
        self.assertEqual(self.scheduler.jobs[f"post:{post.id}"]["schedule"]["type"], "daily")

    async def test_update_can_pause_and_resume_through_management_contract(self):
        post = await self.create()

        paused = await self.skill._manage_update(
            self.ctx,
            {
                "postId": post.id,
                "name": post.name,
                "channelId": post.channel_id,
                "content": post.content,
                "schedule": post.schedule,
                "active": False,
            },
        )
        self.assertFalse(paused["post"]["active"])
        self.assertNotIn(f"post:{post.id}", self.scheduler.jobs)

        resumed = await self.skill._manage_update(
            self.ctx,
            {
                "postId": post.id,
                "name": post.name,
                "channelId": post.channel_id,
                "content": post.content,
                "schedule": post.schedule,
                "active": True,
            },
        )
        self.assertTrue(resumed["post"]["active"])
        self.assertIn(f"post:{post.id}", self.scheduler.jobs)

    async def test_update_rejects_interval_below_minimum_without_mutating_post(self):
        post = await self.create()

        with self.assertRaisesRegex(ValueError, "at least 15 minutes"):
            await self.skill.update_post(
                self.ctx,
                post_id=post.id,
                name="Invalid edit",
                channel_id=10,
                content="Should not persist.",
                schedule={"type": "interval", "seconds": 14 * 60},
            )

        stored = await self.skill.get_post(self.ctx, post.id)
        self.assertEqual(stored.name, post.name)
        self.assertEqual(stored.content, post.content)
        self.assertEqual(self.scheduler.jobs[f"post:{post.id}"]["schedule"]["seconds"], MIN_INTERVAL_SECONDS)

    async def test_update_scheduler_failure_rolls_back_storage_and_job(self):
        post = await self.create()
        self.scheduler.fail_upsert = True

        with self.assertRaisesRegex(RuntimeError, "scheduler upsert failure"):
            await self.skill.update_post(
                self.ctx,
                post_id=post.id,
                name="Edited",
                channel_id=10,
                content="Edited.",
                schedule={"type": "interval", "seconds": 30 * 60},
            )

        stored = await self.skill.get_post(self.ctx, post.id)
        self.assertEqual(stored.name, post.name)
        self.assertEqual(stored.schedule["seconds"], MIN_INTERVAL_SECONDS)
        self.assertEqual(self.scheduler.jobs[f"post:{post.id}"]["schedule"]["seconds"], MIN_INTERVAL_SECONDS)

    async def test_existing_posts_v1_record_remains_loadable(self):
        self.storage.values["posts.v1"] = {
            "legacy-id": {
                "id": "legacy-id",
                "name": "Legacy",
                "channelId": 10,
                "content": "Existing configuration.",
                "schedule": {"type": "interval", "seconds": MIN_INTERVAL_SECONDS},
                "active": True,
                "pendingSlot": None,
                "lastSentSlot": 111,
                "lastMessageId": 222,
            }
        }

        post = await self.skill.get_post(self.ctx, "legacy-id")
        self.assertEqual(post.id, "legacy-id")
        self.assertEqual(post.last_sent_slot, 111)
        self.assertEqual(post.last_message_id, 222)

    async def test_daily_and_weekly_schedules_are_supported(self):
        daily = await self.create(
            name="Daily",
            schedule={"type": "daily", "hour": 9, "minute": 30, "timezone": "Europe/Berlin"},
        )
        weekly = await self.create(
            name="Weekly",
            schedule={
                "type": "weekly",
                "weekday": 0,
                "hour": 10,
                "minute": 0,
                "timezone": "Europe/Berlin",
            },
        )
        self.assertEqual(self.scheduler.jobs[f"post:{daily.id}"]["schedule"]["type"], "daily")
        self.assertEqual(self.scheduler.jobs[f"post:{weekly.id}"]["schedule"]["type"], "weekly")

    async def test_pause_removes_job_but_keeps_configuration(self):
        post = await self.create()
        paused = await self.skill.set_active(self.ctx, post_id=post.id, active=False)
        self.assertFalse(paused.active)
        self.assertNotIn(f"post:{post.id}", self.scheduler.jobs)
        self.assertEqual((await self.skill.get_post(self.ctx, post.id)).content, post.content)

    async def test_resume_recreates_job_without_duplicate_configuration(self):
        post = await self.create()
        await self.skill.set_active(self.ctx, post_id=post.id, active=False)
        await self.skill.set_active(self.ctx, post_id=post.id, active=True)
        self.assertIn(f"post:{post.id}", self.scheduler.jobs)
        self.assertEqual(len(await self.skill.list_posts(self.ctx)), 1)

    async def test_delete_removes_job_and_configuration(self):
        post = await self.create()
        await self.skill.delete_post(self.ctx, post_id=post.id)
        self.assertEqual(await self.skill.list_posts(self.ctx), ())
        self.assertNotIn(f"post:{post.id}", self.scheduler.jobs)

    async def test_execution_sends_once_for_same_scheduler_slot(self):
        post = await self.create()
        job = SimpleNamespace(payload={"postId": post.id}, next_run_at=12345)

        await self.skill._execute(self.ctx, job)
        await self.skill._execute(self.ctx, job)

        self.assertEqual(self.discord.sent, [(10, "Please remember the rules.")])
        stored = await self.skill.get_post(self.ctx, post.id)
        self.assertEqual(stored.last_sent_slot, 12345)
        self.assertEqual(stored.last_message_id, 9001)
        self.assertEqual(len(self.events.events), 1)

    async def test_known_send_failure_clears_pending_reservation_for_retry(self):
        post = await self.create()
        job = SimpleNamespace(payload={"postId": post.id}, next_run_at=12345)
        self.discord.fail = True

        with self.assertRaises(RuntimeError):
            await self.skill._execute(self.ctx, job)

        stored = await self.skill.get_post(self.ctx, post.id)
        self.assertIsNone(stored.pending_slot)
        self.assertIsNone(stored.last_sent_slot)

        self.discord.fail = False
        await self.skill._execute(self.ctx, job)
        self.assertEqual(len(self.discord.sent), 1)

    async def test_missing_or_paused_post_does_not_send(self):
        await self.skill._execute(
            self.ctx,
            SimpleNamespace(payload={"postId": "missing"}, next_run_at=12345),
        )
        self.assertEqual(self.discord.sent, [])

        post = await self.create()
        await self.skill.set_active(self.ctx, post_id=post.id, active=False)
        await self.skill._execute(
            self.ctx,
            SimpleNamespace(payload={"postId": post.id}, next_run_at=12346),
        )
        self.assertEqual(self.discord.sent, [])


if __name__ == "__main__":
    unittest.main()
