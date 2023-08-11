#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging

from logs import log_and_print, set_up_logger
from scengen.cli import arg_handling_run, GeneralOptions, CreateOptions, Command
from scengen.runner import run_amiris


def scengen() -> None:
    """Calls sub-commands with appropriate arguments as returned by the command line parser"""
    command, options = arg_handling_run()
    set_up_logger(options[GeneralOptions.LOG], options[GeneralOptions.LOGFILE])
    log_and_print("Starting scenario generator")

    if command is Command.CREATE:
        log_and_print("Starting to create scenarios")
        n_to_generate = options[CreateOptions.NUMBER]
        i = 0
        while i < n_to_generate:
            logging.debug("Calling generator")
            # call generator
            scenario_name = "Test"  # to be defined by generator
            logging.debug("Calling runner")
            run_amiris(options, scenario_name)
            logging.debug("Calling evaluator")
            # call evaluator
            positive_evaluation = True
            if positive_evaluation:
                i += 1
                logging.info(f"Created {i}/{n_to_generate} scenarios.")
            else:
                logging.warning(f"Scenario did not pass evaluation. Restarting.")

        log_and_print(f"Created {i}/{n_to_generate} scenarios.")


if __name__ == "__main__":
    scengen()
