# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions


def generate_scenario(options: dict, scenario_name: str) -> None:
    """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    config = load_yaml(options[CreateOptions.CONFIG])
    pass
