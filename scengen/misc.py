# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import shutil
from pathlib import Path

from scengen.cli import CreateOptions
from scengen.runner import NAME_SCENARIO_YAML


def delete_all_files(options: dict, scenario_name: str):
    """Removes all created files of `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    shutil.rmtree(Path(options[CreateOptions.DIRECTORY], scenario_name, Path(NAME_SCENARIO_YAML).stem))
