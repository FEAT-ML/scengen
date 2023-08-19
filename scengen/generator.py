# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from pathlib import Path
import random
from typing import Union, List, NoReturn

from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions
from scengen.logs import log_and_raise_critical


ERR_INVALID_INPUT_N_AGENTS_TO_CREATE = (
    "Number of agents to create: Please specify either a positive int value or a "
    "List of [minimum, maximum]. Received `{}` instead."
)


def validate_input_range(input_range: Union[List[int], int]) -> NoReturn:
    """Raises Exception if input range is not positive int or list of [minimum, maximum]"""
    if isinstance(input_range, int):
        if input_range < 1:
            log_and_raise_critical(ERR_INVALID_INPUT_N_AGENTS_TO_CREATE.format(input_range))
    elif isinstance(input_range, list) and len(input_range) == 2 and all(isinstance(i, int) for i in input_range):
        if any(i < 1 for i in input_range):
            log_and_raise_critical(ERR_INVALID_INPUT_N_AGENTS_TO_CREATE.format(input_range))
        if input_range[0] >= input_range[1]:
            log_and_raise_critical(ERR_INVALID_INPUT_N_AGENTS_TO_CREATE.format(input_range))
    else:
        log_and_raise_critical(ERR_INVALID_INPUT_N_AGENTS_TO_CREATE.format(input_range))


def n_agents_to_create(input_range: Union[List[int], int], random_seed: int) -> int:
    """
    Defines number of agents to create based on `input_range`.
    If `input_range` is an int -> this int is returned
    If `input_range` is a list of [minimum, maximum] -> a random int based on `random_seed` is returned
    All other cases log a critical error and raise an Exception.

    Args:
        input_range: either an int or a list of [minimum, maximum]
        random_seed: random seed for drawing random numbers

    Returns:
        Number of agents to create
    Raises:
        Exception if input_range is invalid
    """
    validate_input_range(input_range)

    if isinstance(input_range, int):
        logging.debug(f"Received exactly one input value `{input_range}`.")
        n_to_create = input_range
    else:
        minimum, maximum = input_range
        random.seed(random_seed)
        n_to_create = random.randint(minimum, maximum)

    return n_to_create


def generate_scenario(options: dict) -> None:
    """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    config = load_yaml(options[CreateOptions.CONFIG])
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    defaults = config["defaults"]
    random_seed = defaults["seed"]
    trace_file = load_yaml(defaults["trace_file"])
    count = trace_file["total_count"]
    options["scenario_name"] = defaults["base_name"] + f"_{count}"

    base_template = load_yaml(config["base_template"])

    for agent in config["create"]:
        type_template = load_yaml(
            agent["type_template"]
        )  # change to "safeload" so that aliases are tolerated (e.g. contract anchors)
        n_to_create = n_agents_to_create(agent["count"], random_seed)
        ids = agent["ids"]

        for n in range(n_to_create):
            # create agent
            # append to base_template
            pass
    os.chdir(cwd)
