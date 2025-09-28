# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
from collections.abc import AsyncIterator
from typing import override

import pytest
from agents import realtime as rt
from agents.realtime import model_events
from fakeopenai.agents import model
from openai.types.realtime import conversation_item_deleted_event
from openai.types.realtime import realtime_audio_config as rt_audio_config
from openai.types.realtime import realtime_audio_config_input as rt_audio_config_input
from openai.types.realtime import realtime_audio_config_output as rt_audio_config_output
from openai.types.realtime import realtime_audio_formats as rt_audio_formats
from openai.types.realtime import (
    realtime_audio_input_turn_detection as rt_audio_input_turn_detection,
)
from openai.types.realtime import session_created_event


class FakeRealtimeModelListener(rt.RealtimeModelListener):
    def __init__(self):
        self.events: list[rt.RealtimeModelEvent] = []

    @override
    async def on_event(self, event: rt.RealtimeModelEvent):
        self.events.append(event)


@pytest.fixture
async def fake_model() -> AsyncIterator[model.FakeRealtimeModel]:
    fake_model = model.FakeRealtimeModel()
    try:
        yield fake_model
    finally:
        await fake_model.close()


def assert_session_created_event(event: model_events.RealtimeModelEvent):
    """Helper function to validate session.created event structure."""
    assert isinstance(event, model_events.RealtimeModelRawServerEvent)
    assert event.type == "raw_server_event"

    session_event = session_created_event.SessionCreatedEvent(**event.data)
    assert session_event.type == "session.created"
    assert session_event.event_id.startswith("event_")

    # Compare against expected session structure
    session = session_event.session
    assert session.type == "realtime"
    assert session.model == "gpt-realtime"
    assert session.output_modalities == ["audio"]
    assert session.instructions == "fake-golem-instructions"
    assert session.tools == []
    assert session.tool_choice == "auto"
    assert session.truncation == "auto"
    assert isinstance(session.audio, rt_audio_config.RealtimeAudioConfig)
    assert isinstance(session.audio.input, rt_audio_config_input.RealtimeAudioConfigInput)
    assert isinstance(session.audio.input.format, rt_audio_formats.AudioPCM)
    assert session.audio.input.format.rate == 24000
    assert session.audio.input.format.type == "audio/pcm"
    assert isinstance(session.audio.input.turn_detection, rt_audio_input_turn_detection.ServerVad)
    assert session.audio.input.turn_detection.type == "server_vad"
    assert isinstance(session.audio.output, rt_audio_config_output.RealtimeAudioConfigOutput)
    assert isinstance(session.audio.output.format, rt_audio_formats.AudioPCM)
    assert session.audio.output.format.rate == 24000
    assert session.audio.output.format.type == "audio/pcm"
    assert session.audio.output.voice == "alloy"


class TestConnect:
    @staticmethod
    async def test_not_connected(fake_model):
        config = rt.RealtimeModelConfig()
        listener = FakeRealtimeModelListener()
        fake_model.add_listener(listener)

        assert not fake_model.is_connected
        await fake_model.connect(config)
        assert fake_model.is_connected

        for _ in range(10):
            await asyncio.sleep(0)
        assert len(listener.events) == 1
        assert_session_created_event(listener.events[0])

    @staticmethod
    async def test_connected(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)

        with pytest.raises(AssertionError, match="Already connected"):
            await fake_model.connect(config)

        assert fake_model.is_connected


class TestAddListener:
    @staticmethod
    async def test_add_new_listener(fake_model):
        listener1 = FakeRealtimeModelListener()
        fake_model.add_listener(listener1)
        assert fake_model.listeners == (listener1,)

        listener2 = FakeRealtimeModelListener()
        fake_model.add_listener(listener2)
        assert fake_model.listeners == (listener1, listener2)

    @staticmethod
    async def test_add_duplicate_listener(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)
        fake_model.add_listener(listener)

        assert fake_model.listeners == (listener,)


class TestRemoveListener:
    @staticmethod
    async def test_remove_existing_listener(fake_model):
        listener1 = FakeRealtimeModelListener()
        listener2 = FakeRealtimeModelListener()

        fake_model.add_listener(listener1)
        fake_model.add_listener(listener2)

        fake_model.remove_listener(listener1)

        assert fake_model.listeners == (listener2,)

    @staticmethod
    async def test_remove_nonexistent_listener(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.remove_listener(listener)

        assert fake_model.listeners == ()


class TestSendEvent:
    @staticmethod
    async def test_not_connected(fake_model):
        event = rt.RealtimeModelSendInterrupt()

        with pytest.raises(AssertionError, match="Not connected"):
            await fake_model.send_event(event)

    @staticmethod
    async def test_not_implemented(fake_model):
        config = rt.RealtimeModelConfig()
        event = rt.RealtimeModelSendInterrupt()

        await fake_model.connect(config)

        with pytest.raises(NotImplementedError):
            await fake_model.send_event(event)


class TestClose:
    @staticmethod
    async def test_success(fake_model):
        await fake_model.close()
        assert not fake_model.is_connected
        await fake_model.close()
        assert not fake_model.is_connected

    @staticmethod
    async def test_reconnect(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)
        await fake_model.close()
        await fake_model.connect(config)
        assert fake_model.is_connected

    @staticmethod
    async def test_queue_cleanup(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        fake_model.return_message(test_event)
        fake_model.return_message(test_event)

        await fake_model.close()

        listener = FakeRealtimeModelListener()
        fake_model.add_listener(listener)
        await fake_model.connect(config)

        await asyncio.sleep(0)

        assert len(listener.events) == 0


class TestReturnMessage:
    @staticmethod
    async def test_multiple_listeners(fake_model):
        config = rt.RealtimeModelConfig()
        listener1 = FakeRealtimeModelListener()
        listener2 = FakeRealtimeModelListener()

        fake_model.add_listener(listener1)
        fake_model.add_listener(listener2)
        await fake_model.connect(config)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        fake_model.return_message(test_event)

        for _ in range(10):
            await asyncio.sleep(0)

        assert len(listener1.events) == 2  # session.created + test_event
        assert len(listener2.events) == 2  # session.created + test_event
        assert_session_created_event(listener1.events[0])
        assert listener1.events[1] == test_event
        assert_session_created_event(listener2.events[0])
        assert listener2.events[1] == test_event

    @staticmethod
    async def test_not_connected(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)

        test_event = model_events.RealtimeModelRawServerEvent(data={"type": "test"})
        with pytest.raises(AssertionError, match="Model is not connected"):
            fake_model.return_message(test_event)

        await asyncio.sleep(0.01)

        assert len(listener.events) == 0

    @staticmethod
    async def test_connect_after_adding_events(fake_model):
        config = rt.RealtimeModelConfig()
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        with pytest.raises(AssertionError, match="Model is not connected"):
            fake_model.return_message(test_event)

        await asyncio.sleep(0)
        assert listener.events == []

        await fake_model.connect(config)
        for _ in range(10):
            await asyncio.sleep(0)

        assert len(listener.events) == 1  # test_event + session.created
        assert_session_created_event(listener.events[0])


class TestReturnServerMessage:
    @staticmethod
    async def test_success(fake_model):
        config = rt.RealtimeModelConfig()
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)
        await fake_model.connect(config)

        server_event = conversation_item_deleted_event.ConversationItemDeletedEvent(
            event_id="test-id", item_id="test-item-id", type="conversation.item.deleted"
        )
        fake_model.return_server_message(server_event)

        await asyncio.sleep(0.01)

        assert len(listener.events) == 2  # session.created + test event
        assert_session_created_event(listener.events[0])
        received_event = listener.events[1]  # The test event is second
        assert isinstance(received_event, model_events.RealtimeModelRawServerEvent)
        assert received_event.type == "raw_server_event"

        parsed_event = conversation_item_deleted_event.ConversationItemDeletedEvent(
            **received_event.data
        )
        assert parsed_event == server_event


class TestRunning:
    @staticmethod
    @pytest.fixture
    def default_agent() -> rt.RealtimeAgent:
        return rt.RealtimeAgent(name="Fake Golem", instructions="You are a fake agent")

    @staticmethod
    @pytest.fixture
    def realtime_model() -> model.FakeRealtimeModel:
        return model.FakeRealtimeModel()

    @staticmethod
    @pytest.fixture
    def realtime_runner(default_agent, realtime_model) -> rt.RealtimeRunner:
        return rt.RealtimeRunner(default_agent, model=realtime_model)

    @staticmethod
    @pytest.fixture
    async def realtime_session(realtime_runner) -> AsyncIterator[rt.RealtimeSession]:
        async with await realtime_runner.run() as session:
            yield session

    @staticmethod
    async def test_create_session(realtime_model, realtime_session):
        assert realtime_session.model == realtime_model
        assert realtime_model.is_connected
        assert realtime_model.listeners == (realtime_session,)

    @staticmethod
    async def test_send_audio(realtime_session):
        with pytest.raises(NotImplementedError):
            await realtime_session.send_audio(b"realtime-audio")
