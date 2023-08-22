#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging

from logs import log_and_print, set_up_logger
from scengen.cli import arg_handling_run, GeneralOptions, CreateOptions, Command
from scengen.generator import generate_scenario
from scengen.misc import delete_all_files, increase_count_in_trace_file
from scengen.runner import execute_scenario
from scengen.evaluator import evaluate_scenario


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
            generate_scenario(options)

            if not options[CreateOptions.SKIP_ESTIMATION]:
                logging.debug("Calling estimator")
                # positive_estimation = estimate_scenario()
                # if not positive_estimation:
                #     logging.warning(f"Scenario did not pass estimation. Restarting.")
                #     delete_all_files(options)
                #     continue

            logging.debug("Calling runner")
            execute_scenario(options)

            if not options[CreateOptions.SKIP_EVALUATION]:
                logging.debug("Calling evaluator")
                positive_evaluation = evaluate_scenario(options)
            else:
                positive_evaluation = True

            if positive_evaluation:
                i += 1
                increase_count_in_trace_file(options)
                logging.info(f"Created {i}/{n_to_generate} scenarios.")
            else:
                delete_all_files(options)
                logging.warning(f"Scenario did not pass evaluation. Restarting.")

        log_and_print(f"Created {i}/{n_to_generate} scenarios.")


if __name__ == "__main__":
    scengen()
