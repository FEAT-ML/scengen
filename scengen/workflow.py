#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0


def scengen() -> None:
    """Calls sub-commands with appropriate arguments as returned by the command line parser"""
    command, options = arg_handling_run()
    set_up_logger(options[GeneralOptions.LOG], options[GeneralOptions.LOGFILE])
    log_and_print("Starting scenario generator")

    # get number n of scenarios to create
    # while i < n
    # call generator
    # call runner
    # call evaluator

    log_and_print("Created X/X scenarios.")
