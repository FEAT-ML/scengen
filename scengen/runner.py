#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

from amirispy.scripts.subcommands import run
from amirispy.source.cli import GeneralOptions as AMIRISGeneralOptions

from scengen.cli import CreateOptions, GeneralOptions


def run_amiris(options: dict, scenario_name: str) -> None:
    """
    Compile scenario to protobuf using fameio.scripts.make_config, execute AMIRIS,
    and extract results using fameio.scripts.convert_results

    Args:
        options: dictionary of command line instructions
        scenario_name: name of scenario to run

    Returns:
        None
    """
    run.check_java_installation(raise_exception=True)
    origin_wd = Path.cwd()
    run.check_if_write_access(origin_wd)

    path_to_scenario: Path = Path(options[CreateOptions.DIRECTORY], scenario_name)
    options = map_options(options)

    paths = run.determine_all_paths(path_to_scenario, origin_wd, options)
    os.chdir(paths["SCENARIO_DIRECTORY"])
    run.compile_input(options, paths)
    os.chdir(origin_wd)
    run.call_amiris(paths)
    run.compile_output(options, paths)


def map_options(options: dict) -> dict:
    """Maps values from scengen `options` to option keys of amirispy"""
    options[run.RunOptions.JAR] = options[CreateOptions.JAR]
    options[run.RunOptions.OUTPUT] = options[CreateOptions.DIRECTORY]
    options[AMIRISGeneralOptions.LOG] = options[GeneralOptions.LOG]
    options[AMIRISGeneralOptions.LOGFILE] = options[GeneralOptions.LOGFILE]
    return options
