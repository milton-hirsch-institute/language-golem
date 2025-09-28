# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import click
from langgolem.cli import main


class TestMain:
    @staticmethod
    def test_sub_command(runner):
        @click.command("sub-command")
        def sub_command():
            click.echo("sub-command ran")

        main.langgolem.add_command(sub_command)

        result = runner.invoke(main.langgolem, ["sub-command"])

        assert result.stdout == "sub-command ran\n"
        assert result.stderr == ""
        assert result.exit_code == 0

    @staticmethod
    def test_default_behavior(runner):
        result = runner.invoke(main.langgolem)

        assert result.stdout == ""
        assert result.stderr.startswith("Usage: langgolem [OPTIONS] COMMAND [ARGS]")
        assert result.exit_code == 2
