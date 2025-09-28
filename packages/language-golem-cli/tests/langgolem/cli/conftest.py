# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import pytest
from click import testing


@pytest.fixture
def runner() -> testing.CliRunner:
    return testing.CliRunner()
