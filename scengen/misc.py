# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import shutil
from pathlib import Path

import yaml
from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions
from scengen.logs import log_and_raise_critical
from scengen.runner import NAME_SCENARIO_YAML


def delete_all_files(options: dict):
    """Removes all created files of scenario stored in `CreateOptions.DIRECTORY`"""
    dir_to_remove = Path(options[CreateOptions.DIRECTORY], options["scenario_name"])
    shutil.rmtree(dir_to_remove, ignore_errors=True)
    os.remove(options["scenario_path"])
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


def write_yaml(output_file: dict, output_file_path: Path) -> None:
    """Writes given `output_file` to `output_file_path` (ending in .yaml)"""
    check_if_valid_yaml_path(output_file_path)
    with open(output_file_path, "w") as stream:
        try:
            yaml.safe_dump(output_file, stream)
        except yaml.YAMLError:
            log_and_raise_critical(f"Failed writing YAML to '{output_file_path}'")


def check_if_valid_yaml_path(file_path):
    """Raises Exception if provided `file_path` is not a valid YAML path"""
    if Path(file_path).suffix.lower() not in [".yaml", ".yml"]:
        log_and_raise_critical(f"Provide a valid Path to a YAML file. Received '{file_path}'")
