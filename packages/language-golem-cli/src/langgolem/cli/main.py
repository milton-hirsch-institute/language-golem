# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

"""Command-line interface for Language Golem."""

import click
from langgolem.cli import prattle


@click.group
def langgolem():
    pass


langgolem.add_command(prattle.prattle)


if __name__ == "__main__":  # pragma: no cover
    langgolem()
