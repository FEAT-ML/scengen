# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path

from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions


def generate_scenario(options: dict) -> None:
    """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    config = load_yaml(options[CreateOptions.CONFIG])
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    defaults = config["defaults"]
    random_seed = defaults["seed"]
    trace_file = load_yaml(defaults["trace_file"])
    count = trace_file["total_count"]
    options["scenario_name"] = defaults["base_name"] + f"_{count}"
    os.chdir(cwd)
    pass
