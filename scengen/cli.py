# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
from enum import Enum, auto
from pathlib import Path
from typing import Tuple, Dict, Any

from scengen.logs import LogLevels

SCENGEN_PARSER = (
    "Command-line interface to scengen - the scenario generator for the open electricity market model AMIRIS"
)
SCENGEN_LOG_FILE_HELP = "Provide logging file (default: None)"
SCENGEN_LOG_LEVEL_HELP = f"Choose logging level (default: {LogLevels.ERROR.name})"
SCENGEN_COMMAND_HELP = "Choose one of the following commands:"

CREATE_HELP = "Creates scenarios for AMIRIS"
CREATE_N_DEFAULT = 10
CREATE_N_HELP = f"Specify number of scenarios to be generated (default: {CREATE_N_DEFAULT})"
CREATE_CONFIG_HELP = "Path to configuration YAML file defining specifications for creation of scenarios"
CREATE_JAR_HELP = "Path to 'amiris-core_<version>-jar-with-dependencies.jar'"
CREATE_DIR_HELP = "Directory to parse scenarios from and write results to"


class GeneralOptions(Enum):
    """Specifies general options for scengen"""

    LOG = auto()
    LOGFILE = auto()


class Command(Enum):
    """Specifies command to execute"""

    CREATE = auto()


class CreateOptions(Enum):
    """Options for command `create`"""

    NUMBER = auto()
    CONFIG = auto()
    JAR = auto()
    DIRECTORY = auto()


Options = {
    Command.CREATE: CreateOptions,
}


def arg_handling_run() -> Tuple[Command, Dict[Enum, Any]]:
    """Handles command line arguments for `scengen` and returns `command` and its options `args`"""
    parent_parser = argparse.ArgumentParser(prog="scengen", description=SCENGEN_PARSER)
    parent_parser.add_argument("-lf", "--logfile", type=Path, required=False, help=SCENGEN_LOG_FILE_HELP)
    parent_parser.add_argument(
        "-l",
        "--log",
        default=LogLevels.ERROR.name,
        choices=[level.name.lower() for level in LogLevels],
        help=SCENGEN_LOG_LEVEL_HELP,
    )
    subparsers = parent_parser.add_subparsers(dest="command", required=True, help=SCENGEN_COMMAND_HELP)

    create_parser = subparsers.add_parser("create", help=CREATE_HELP)
    create_parser.add_argument("--number", "-n", type=int, default=CREATE_N_DEFAULT, help=CREATE_N_HELP)
    create_parser.add_argument("--config", "-c", type=Path, required=True, help=CREATE_CONFIG_HELP)
    create_parser.add_argument("--jar", "-j", type=Path, required=True, help=CREATE_JAR_HELP)
    create_parser.add_argument("--directory", "-d", type=Path, default=Path("./"), help=CREATE_DIR_HELP)

    args = vars(parent_parser.parse_args())
    command = Command[args.pop("command").upper()]

    return command, enumify(command, args)


def enumify(command: Command, args: dict) -> Dict[Enum, Any]:
    """Matches `args` for given `command` to their respective Enum"""
    result = {}
    for option in GeneralOptions:
        result[option] = args.pop(option.name.lower())

    for option in Options[command]:
        result[option] = args.pop(option.name.lower())
    return result
