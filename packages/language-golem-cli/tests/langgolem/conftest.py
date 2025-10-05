# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0
import datetime
from collections.abc import AsyncIterator
from collections.abc import Iterator

import fakesd
import pytest
from agents import realtime as rt
from fakeopenai.agents import model as fake_model
from langgolem.util import misc
from tyminator import clock


@pytest.fixture
def fake_clock(monkeypatch) -> clock.Clock:
    instance = clock.Clock(datetime.datetime(2011, 6, 12), datetime.timedelta(milliseconds=100))
    monkeypatch.setattr(misc, "time", instance.time_function)
    return instance


@pytest.fixture
def fake_sd() -> Iterator[fakesd.DeviceManager]:
    with fakesd.setup() as device_manager:
        yield device_manager


@pytest.fixture
def realtime_model() -> fake_model.FakeRealtimeModel:
    return fake_model.FakeRealtimeModel()


@pytest.fixture
def starting_agent() -> rt.RealtimeAgent:
    return rt.RealtimeAgent(name="starting-agent", instructions="starting-agent-instructions")


@pytest.fixture
def realtime_runner(realtime_model, starting_agent) -> rt.RealtimeRunner:
    return rt.RealtimeRunner(starting_agent, model=realtime_model)


@pytest.fixture
async def realtime_session(realtime_runner) -> AsyncIterator[rt.RealtimeSession]:
    async with await realtime_runner.run() as session:
        yield session
