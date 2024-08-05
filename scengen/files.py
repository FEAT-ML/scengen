# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import shutil
from pathlib import Path
import time

import yaml
from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions
from scengen.logs import log_and_raise_critical, log_error_and_raise

_ERR_NOT_A_FOLDER = "Given Path '{}' is not a directory."


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
    write_dict_to_disk(trace_file, trace_file_name)
    os.chdir(cwd)
    logging.debug(f"Increased trace file count to '{trace_file['total_count']}'")


def write_dict_to_disk(trace_file: dict, file_name: str) -> None:
    """Writes `trace_file` as `file_name` to disk"""
    with open(file_name, "w") as file:
        yaml.dump(trace_file, file, default_flow_style=False)


def save_seed_to_trace_file(options: dict, seed: int) -> None:
    """Saves seed to trace file"""
    config = load_yaml(options[CreateOptions.CONFIG])
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    trace_file_name = config["defaults"]["trace_file"]
    trace_file = load_yaml(trace_file_name)
    trace_file["seed"] = seed
    write_dict_to_disk(trace_file, trace_file_name)
    os.chdir(cwd)
    logging.debug(f"Stored seed '{seed}' to `trace_file`")


def write_yaml(output_file: dict, output_file_path: Path) -> None:
    """Writes given `output_file` to `output_file_path` (ending in .yaml)"""
    ensure_folder_exists(output_file_path.parent)
    check_if_valid_yaml_path(output_file_path)
    with open(output_file_path, "w") as stream:
        try:
            yaml.safe_dump(output_file, stream)
        except yaml.YAMLError:
            log_and_raise_critical(f"Failed writing YAML to '{output_file_path}'")


def check_if_valid_yaml_path(file_path: Path):
    """Raises Exception if provided `file_path` is not a valid YAML path"""
    if Path(file_path).suffix.lower() not in [".yaml", ".yml"]:
        log_and_raise_critical(f"Provide a valid Path to a YAML file. Received '{file_path}'")


def ensure_folder_exists(path: Path) -> None:
    """
    Returns Path to a directory and creates the folder if required.
    If given Path is an existing folder: does nothing, else creates new folder (including parent folders)

    Args:
        path: to check and create if not existing

    Returns:
        None

    Raises:
        ValueError: if path is an existing file
    """
    if path.is_file():
        log_error_and_raise(ValueError(_ERR_NOT_A_FOLDER.format(path)))
    if not path.is_dir():
        path.mkdir(parents=True)


def get_trace_file(config: dict, options: dict) -> dict:
    """Returns loaded `defaults["trace_file"]` or creates new trace file if not present"""
    defaults = config["defaults"]
    if defaults.get("trace_file"):
        trace_file_path = defaults["trace_file"]
        try:
            trace_file = load_yaml(trace_file_path)
        except FileNotFoundError:
            trace_file = setup_new_trace_file(config, defaults, options, trace_file_path)
            logging.info(f"Could not find `trace_file` in path '{trace_file_path}' as specified in GeneratorConfig. Created new one instead.")
    else:
        trace_file_name = f"trace_file_{time.strftime('%Y-%m-%d_%H%M%S')}.yaml"
        trace_file = setup_new_trace_file(config, defaults, options, trace_file_name)
        logging.warning(f"No mandatory `trace_file` found in given GeneratorConfig. Created new one at '{trace_file_name}' and added to GeneratorConfig instead.")
    return trace_file


def setup_new_trace_file(config: dict, defaults: dict, options: dict, file_name: str) -> dict:
    """Returns new trace_file which is added to config and saved to disk with `file_name`"""
    trace_file = {
        "total_count": 0,
        "seed": 0
    }

    defaults["trace_file"] = file_name
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    write_dict_to_disk(config, options[CreateOptions.CONFIG])
    ensure_folder_exists(Path(file_name).parent)
    write_dict_to_disk(trace_file, file_name)
    os.chdir(cwd)
    return trace_file
