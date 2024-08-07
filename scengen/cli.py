# SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
from enum import Enum, auto
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from scengen.logs import LogLevel

SCENGEN_PARSER = (
    "Command-line interface to scengen - the scenario generator for the open electricity market model AMIRIS"
)
SCENGEN_LOG_FILE_HELP = "Provide logging file (default: None)"
SCENGEN_LOG_LEVEL_HELP = f"Choose logging level (default: {LogLevel.ERROR.name})"
SCENGEN_COMMAND_HELP = "Choose one of the following commands:"

CREATE_HELP = "Creates scenarios for AMIRIS"
CREATE_N_DEFAULT = 10
CREATE_N_HELP = f"Specify number of scenarios to be generated (default: {CREATE_N_DEFAULT})"
CREATE_CONFIG_HELP = "Path to configuration YAML file defining specifications for creation of scenarios"
CREATE_JAR_HELP = "Path to 'amiris-core_<version>-jar-with-dependencies.jar'"
CREATE_DIR_HELP = "Directory to parse scenarios from and write results to"
CREATE_SKIP_ESTIMATION_HELP = (
    "Speed-focused approach by omitting the AMIRIS scenario estimation at the expense "
    "of bypassing plausibility check (default: False)"
)
CREATE_SKIP_EVALUATION_HELP = (
    "Speed-focused approach by omitting the AMIRIS result evaluation at the expense "
    "of bypassing plausibility check (default: False)"
)
CREATE_OUTPUT_OPTION_HELP = (
    "optional pass through of FAME-Io's output conversion options, see "
    "https://gitlab.com/fame-framework/fame-io/-/blob/main/README.md#read-fame-results"
)


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
    SKIP_ESTIMATION = auto()
    SKIP_EVALUATION = auto()
    OUTPUT_OPTIONS = auto()


Options = {
    Command.CREATE: CreateOptions,
}


def arg_handling_run(input_args: Optional[List[str]] = None) -> Tuple[Command, Dict[Enum, Any]]:
    """Handles command line arguments for `scengen` and returns `command` and its options `args`"""
    parent_parser = argparse.ArgumentParser(prog="scengen", description=SCENGEN_PARSER)
    parent_parser.add_argument("-lf", "--logfile", type=Path, required=False, help=SCENGEN_LOG_FILE_HELP)
    parent_parser.add_argument(
        "-l",
        "--log",
        default=LogLevel.ERROR.name,
        choices=[level.name.lower() for level in LogLevel],
        help=SCENGEN_LOG_LEVEL_HELP,
    )
    subparsers = parent_parser.add_subparsers(dest="command", required=True, help=SCENGEN_COMMAND_HELP)

    create_parser = subparsers.add_parser("create", help=CREATE_HELP)
    create_parser.add_argument("--number", "-n", type=int, default=CREATE_N_DEFAULT, help=CREATE_N_HELP)
    create_parser.add_argument("--config", "-c", type=Path, required=True, help=CREATE_CONFIG_HELP)
    create_parser.add_argument("--jar", "-j", type=Path, required=True, help=CREATE_JAR_HELP)
    create_parser.add_argument("--directory", "-d", type=Path, default=Path("./"), help=CREATE_DIR_HELP)
    create_parser.add_argument(
        "--skip_estimation", "-ses", default=False, action="store_true", help=CREATE_SKIP_ESTIMATION_HELP
    )
    create_parser.add_argument(
        "--skip_evaluation", "-sev", default=False, action="store_true", help=CREATE_SKIP_EVALUATION_HELP
    )
    create_parser.add_argument("--output-options", "-oo", type=str, default="", help=CREATE_OUTPUT_OPTION_HELP)

    args = vars(parent_parser.parse_args(input_args))
    command = Command[args.pop("command").upper()]

    args = resolve_relative_paths(args)

    return command, enumify(command, args)


def resolve_relative_paths(args: dict) -> dict:
    """Returns given `args` with relative paths resolved as absolute paths"""
    for option in args:
        if isinstance(args[option], Path):
            args[option] = args[option].resolve()
    return args


def enumify(command: Command, args: dict) -> Dict[Enum, Any]:
    """Matches `args` for given `command` to their respective Enum"""
    result = {}
    for option in GeneralOptions:
        result[option] = args.pop(option.name.lower())

    for option in Options[command]:
        result[option] = args.pop(option.name.lower())
    return result
