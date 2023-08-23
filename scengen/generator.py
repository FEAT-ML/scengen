# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import copy
import logging
import os
from pathlib import Path
import random
from typing import Union, List, NoReturn, Dict, Any, Tuple
import time

from fameio.source.loader import load_yaml

from scengen.cli import CreateOptions
from scengen.logs import log_and_raise_critical
from scengen.misc import write_yaml

RANGE_IDENTIFIER = "range"

REPLACEMENT_IDENTIFIER = "//"
KEY_THISAGENT = f"{REPLACEMENT_IDENTIFIER}THISAGENT"

ERR_INVALID_RANGE_INPUT = (
    "Received invalid range input in form '{}'. Please provide in format "
    "'range(minimum_integer, maximum_integer)'. Both integers must be >= 0."
)
ERR_FAILED_RESOLVE_ID = "Found replacement Identifier '{}' with no corresponding Agent in Contract '{}'"


def validate_input_range(input_range: Tuple[int, int]) -> NoReturn:
    """Raises Exception if input range is not positive int or list of [minimum, maximum]"""
    if isinstance(input_range, tuple) and len(input_range) == 2 and all(isinstance(i, int) for i in input_range):
        if any(i < 0 for i in input_range):
            log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range))
        if input_range[0] >= input_range[1]:
            log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range))
    else:
        log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range))


def digest_range(input_value: str) -> Tuple[int, int]:
    """Returns Tuple of minimum and maximum integer value digested from `input_value` in expected form"""
    numbers = extract_numbers_from_string(input_value)
    try:
        min_value, max_value = map(int, numbers.split(","))
    except ValueError:
        log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_value))
    return min_value, max_value


def extract_numbers_from_string(input_value: str) -> str:
    """Returns string in form 'int, int' from given `input_value` by removing RANGE_IDENTIFIER and '(' and ')'"""
    extracted_numbers = input_value.lower().replace(RANGE_IDENTIFIER, "").replace("(", "").replace(")", "")
    return extracted_numbers


def get_value_from_field(input_value: Union[List[Any], Any]) -> Any:
    """
    Returns value stored in `input_value` based on the user specification [fixed value, one out of List,
    random in range]
    """
    if RANGE_IDENTIFIER in input_value.lower():
        input_range = digest_range(input_value)
        validate_input_range(input_range)
        minimum, maximum = input_range
        value = random.randint(minimum, maximum)
        logging.debug(f"Chose random value '{value}' from '{input_value}'.")
    elif isinstance(input_value, list):
        value = random.choice(input_value)
        logging.debug(f"Chose random value '{value}' from list '{input_value}'.")
    else:
        logging.debug(f"Received exactly one input value '{input_value}'.")
        value = input_value
    return value


def replace_ids(contracts: List[dict], agent_id: str, ext_id: Union[dict, None]) -> None:
    """Replaces in-place `agent_id` and optional `ext_id` in given `contracts`"""
    replace_map = {KEY_THISAGENT: agent_id}
    if ext_id:
        for key, value in ext_id.items():
            if isinstance(value, int):
                replace_map[key] = value
            elif not value.startswith(REPLACEMENT_IDENTIFIER):
                replace_map[key] = REPLACEMENT_IDENTIFIER + value
            else:
                replace_map[key] = value

    for k, v in replace_map.items():
        replace_in_dict(contracts, k, v)


def replace_in_dict(contracts: List[dict], replace_identifier: str, replace_value: str) -> None:
    """Recursively searches for `replace_identifier` in contracts and replaces `replace_value` if not integer"""
    for contract in contracts:
        for key, value in contract.items():
            if isinstance(value, str) and replace_identifier in value:
                contract[key] = replace_value


def get_all_ids_from(scenario: dict) -> List[int]:
    """Returns list of unique Agent Ids in given `scenario`"""
    unique_ids = []
    for agent in scenario["Agents"]:
        append_unique_integer_id(agent["Id"], unique_ids)
    return unique_ids


def append_unique_integer_id(agent_id: Union[str, int], unique_ids: List[int]):
    """Appends `agent_id` to `unique_ids` if integer and unique"""
    if isinstance(agent_id, int) and agent_id not in unique_ids:
        unique_ids.append(agent_id)


def create_new_unique_id(unique_ids: List[int]) -> int:
    """Returns new unique integer by adding 1 to the highest Id in `unique_ids`. Adds new Id in-place to `unique_ids`"""
    new_id = max(unique_ids) + 1 if unique_ids else 1
    unique_ids.append(new_id)
    return new_id


def resolve_ids(scenario: dict) -> None:
    """Resolves in-place all placeholder ID references in Agents & Contracts to unique Ids"""
    active_ids = get_all_ids_from(scenario)
    replacement_map: Dict[str, int] = {}
    for agent in scenario["Agents"]:
        agent_id = agent["Id"]
        if REPLACEMENT_IDENTIFIER in str(agent_id):
            if agent_id in replacement_map.keys():
                agent["Id"] = replacement_map[agent_id]
            else:
                unique_id = create_new_unique_id(active_ids)
                agent["Id"] = replacement_map[agent_id] = unique_id
    for contract in scenario["Contracts"]:
        for key, value in contract.items():
            if REPLACEMENT_IDENTIFIER in str(value):
                try:
                    contract[key] = replacement_map[value]
                except KeyError:
                    log_and_raise_critical(ERR_FAILED_RESOLVE_ID.format(value, contract))


def generate_scenario(options: dict) -> None:
    """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    config = load_yaml(options[CreateOptions.CONFIG])
    cwd = os.getcwd()
    os.chdir(Path(options[CreateOptions.CONFIG]).parent)
    defaults = config["defaults"]

    trace_file = load_yaml(defaults["trace_file"])
    count = trace_file["total_count"]

    set_random_seed(defaults, options, trace_file)

    options["scenario_name"] = defaults["base_name"] + f"_{count}"

    base_template = load_yaml(config["base_template"])

    for agent in config["create"]:
        type_template = load_yaml(Path(agent["type_template"]))
        agent_type_template = type_template["Agents"]
        contract_type_template = type_template.get("Contracts")
        n_to_create = get_value_from_field(agent["count"])
        agent_name = agent["this_agent"]
        external_ids = agent.get("external_ids")

        for n in range(n_to_create):
            agent_to_append = copy.deepcopy(agent_type_template)

            agent_id = REPLACEMENT_IDENTIFIER + agent_name
            agent_id += str(n) if n_to_create > 1 else ""

            agent_to_append["Id"] = agent_id
            base_template["Agents"].append(agent_to_append)

            if contract_type_template:
                contract_to_append = copy.deepcopy(contract_type_template)
                replace_ids(contract_to_append, agent_id, external_ids)
                base_template["Contracts"].extend(contract_to_append)

    resolve_ids(base_template)
    os.chdir(cwd)
    options["scenario_path"] = Path(options[CreateOptions.DIRECTORY], options["scenario_name"] + ".yaml")
    write_yaml(base_template, options["scenario_path"])


def set_random_seed(defaults: dict, options: dict, trace_file: dict) -> None:
    """Sets random seed if not yet saved to `options['random_seed']`"""
    if not options.get("random_seed"):
        random_seed = get_random_seed(defaults)
        random.seed(random_seed)
        options["random_seed"] = trace_file["random_seed"] = random_seed


def get_random_seed(defaults: dict) -> int:
    """Returns random seed as integer, defined optionally in `defaults['seed']` or from system time in ns instead"""
    if defaults.get("seed"):
        random_seed = defaults["seed"]
    else:
        random_seed = time.time_ns()
    return random_seed
