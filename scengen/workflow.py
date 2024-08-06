#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional, List

from scengen.logs import scengen_logger, log
from scengen.cli import arg_handling_run, GeneralOptions, CreateOptions, Command
from scengen.estimator import estimate_scenario
from scengen.generator import generate_scenario
from scengen.files import delete_all_files, increase_count_in_trace_file
from scengen.runner import execute_scenario
from scengen.evaluator import evaluate_scenario


def scengen_cli(args: Optional[List[str]] = None) -> None:
    """Calls sub-commands with appropriate arguments as returned by the command line parser"""
    command, options = arg_handling_run(args)
    scengen_logger(options[GeneralOptions.LOG], options[GeneralOptions.LOGFILE])

    if command is Command.CREATE:
        log().info("Starting to create scenarios")
        requested_scenario_count = options[CreateOptions.NUMBER]
        useful_scenario_count = 0
        while useful_scenario_count < requested_scenario_count:
            generate_scenario(options)

            positive_estimation = True if options[CreateOptions.SKIP_ESTIMATION] else estimate_scenario(options)
            if not positive_estimation:
                log().warning(f"Scenario did not pass estimation. Creating another scenario.")
                delete_all_files(options)
                continue

            execute_scenario(options)

            positive_evaluation = True if options[CreateOptions.SKIP_EVALUATION] else evaluate_scenario(options)
            if positive_evaluation:
                useful_scenario_count += 1
                increase_count_in_trace_file(options)
                log().info(f"Created {useful_scenario_count}/{requested_scenario_count} scenarios.")
            else:
                log().warning(f"Scenario did not pass evaluation. Restarting.")
                delete_all_files(options)

        log().info(f"Created scenario {useful_scenario_count} of {requested_scenario_count}.")


if __name__ == "__main__":
    scengen_cli()
