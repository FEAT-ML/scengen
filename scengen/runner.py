# SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path

from amirispy.scripts.subcommands import run as amiris
from amirispy.source.cli import GeneralOptions as AMIRISGeneralOptions

from scengen.cli import CreateOptions, GeneralOptions
from scengen.logs import log

NAME_SCENARIO_YAML = "scenario.yaml"


def execute_scenario(options: dict) -> None:
    """Calls AMIRIS after mapping `options` using amirispy functionality"""
    log().debug("Executing scenario")
    options = map_options(options)
    amiris.run_amiris(options)
    delete_pb_files()


def map_options(options: dict) -> dict:
    """Maps values from scengen `options` to option keys of amirispy"""
    options[amiris.RunOptions.JAR] = options[CreateOptions.JAR]
    options[amiris.RunOptions.OUTPUT] = Path(options[CreateOptions.DIRECTORY], options['scenario_path'].stem)
    options[AMIRISGeneralOptions.LOG] = options[GeneralOptions.LOG]
    options[AMIRISGeneralOptions.LOGFILE] = options[GeneralOptions.LOGFILE]
    options[amiris.RunOptions.SCENARIO] = options["scenario_path"]
    options[amiris.RunOptions.OUTPUT_OPTIONS] = options[CreateOptions.OUTPUT_OPTIONS]
    options[amiris.RunOptions.NO_CHECKS] = options[CreateOptions.NO_CHECKS]
    return options


def delete_pb_files() -> None:
    """Deletes input and output Protobuf files created by fameio in current working dir"""
    for file in ["input.pb", "output.pb"]:
        try:
            os.remove(Path(os.getcwd(), file))
        except FileNotFoundError:
            log().debug(f"Could not delete file `{file}` in current working dir.")
