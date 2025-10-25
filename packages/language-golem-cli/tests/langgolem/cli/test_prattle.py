# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from langgolem.cli import main


class TestPrattle:
    @staticmethod
    def test_no_input_file(runner):
        result = runner.invoke(main.langgolem, ["prattle"])

        assert result.stdout == ""
        assert result.stderr == "Audio input devices not supported.\n"
        assert result.exit_code == 1

    @staticmethod
    def test_input_file(runner, audio_file):
        result = runner.invoke(main.langgolem, ["prattle", "-i", str(audio_file)])

        assert result.stdout == "32768\n32768\n32768\n32768\n32768\n32768\n32768\n10624\n"
        assert result.stderr == ""
        assert result.exit_code == 0
