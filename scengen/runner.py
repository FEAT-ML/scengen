#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from pathlib import Path

from amirispy.scripts.subcommands import run as amiris
from amirispy.source.cli import GeneralOptions as AMIRISGeneralOptions

from scengen.cli import CreateOptions, GeneralOptions


def call_amiris(options: dict, scenario_name: str) -> None:
    """Calls AMIRIS after mapping `options` and `scenario_name` using amirispy functionality"""
    options = map_options(options, scenario_name)
    amiris.run_amiris(options)
    delete_pb_files()


def map_options(options: dict, scenario_name: str) -> dict:
    """Maps values from scengen `options` and `scenario_name` to option keys of amirispy"""
    options[amiris.RunOptions.JAR] = options[CreateOptions.JAR]
    options[amiris.RunOptions.OUTPUT] = Path(options[CreateOptions.DIRECTORY], "results")
    options[AMIRISGeneralOptions.LOG] = options[GeneralOptions.LOG]
    options[AMIRISGeneralOptions.LOGFILE] = options[GeneralOptions.LOGFILE]
    options[amiris.RunOptions.SCENARIO] = Path(options[CreateOptions.DIRECTORY], scenario_name)
    return options


def delete_pb_files() -> None:
    """Deletes input and output Protobuf files created by fameio in current working dir"""
    for file in ["input.pb", "output.pb"]:
        try:
            os.remove(Path(os.getcwd(), file))
        except FileNotFoundError:
            logging.debug(f"Could not delete file `{file}` in current working dir.")
