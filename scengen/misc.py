# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import shutil
from pathlib import Path
from typing import Union

import yaml
import ruamel.yaml
from fameio.source.loader import load_yaml
from ruamel.yaml import CommentedMap

from scengen.cli import CreateOptions
from scengen.runner import NAME_SCENARIO_YAML


def delete_all_files(options: dict):
    """Removes all created files of scenario stored in `CreateOptions.DIRECTORY`"""
    dir_to_remove = Path(options[CreateOptions.DIRECTORY], options["scenario_name"], Path(NAME_SCENARIO_YAML).stem)
    shutil.rmtree(dir_to_remove)
    logging.debug(f"Removed all files in '{dir_to_remove}'")


def increase_count_in_trace_file(options: dict) -> None:
    """Increases count in trace file defined in `CreateOptions.CONFIG` by 1"""
    config = load_yaml(options[CreateOptions.CONFIG])
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    trace_file_name = config["defaults"]["trace_file"]
    trace_file = load_yaml(trace_file_name)
    trace_file["total_count"] += 1
    with open(trace_file_name, "w") as file:
        yaml.dump(trace_file, file, default_flow_style=False)
    os.chdir(cwd)
    logging.debug(f"Increased trace file count to '{trace_file['total_count']}'")


def load_yaml_raw(file_path: Union[str, Path]) -> CommentedMap:
    """Returns YAML file from `file_path` loaded by ruamel.yaml preserving file formatting and aliases"""
    ryaml = ruamel.yaml.YAML()
    return ryaml.load(Path(file_path))
