# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from langgolem.cli import main


def test_prattle(runner):
    result = runner.invoke(main.langgolem, ["prattle"])

    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exit_code == 0
