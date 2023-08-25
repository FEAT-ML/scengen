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
from scengen.misc import write_yaml, save_seed_to_trace_file

SEPARATOR = ";"
RANGE_IDENTIFIER = "range"
CHOOSE_IDENTIFIER = "choose"
PICKFILE_IDENTIFIER = "pickfile"

REPLACEMENT_IDENTIFIER = "//"
KEY_THISAGENT = f"{REPLACEMENT_IDENTIFIER}THISAGENT"

ERR_INVALID_RANGE_INPUT = (
    "Received invalid range input in form '{}'. Please provide in format "
    "'range(minimum_integer, maximum_integer)'. Negative integers are considered {}"
)
ERR_COULD_NOT_MAP_RANGE_VALUES = "Could not map range values '{}' to minimum, maximum values."
ERR_FAILED_RESOLVE_ID = "Found replacement Identifier '{}' with no corresponding Agent in Contract '{}'"
DEBUG_NO_CREATE = "No agents to `create` found in Config '{}'"


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

    if "create" in config:
        for agent in config["create"]:
            type_template = load_yaml(Path(agent["type_template"]))
            agent_type_template = type_template["Agents"]
            contract_type_template = type_template.get("Contracts")
            n_to_create = round(get_value_from_field(agent["count"], options, allow_negative=False))
            agent_name = agent["this_agent"]
            external_ids = agent.get("external_ids")

            for n in range(n_to_create):
                agent_to_append = copy.deepcopy(agent_type_template)
                agent_to_append["Id"] = get_agent_id(agent_name, n, n_to_create)
                base_template["Agents"].append(agent_to_append)

                if contract_type_template:
                    contract_to_append = copy.deepcopy(contract_type_template)
                    replace_ids_in_contracts(contract_to_append, agent_to_append["Id"], external_ids)
                    base_template["Contracts"].extend(contract_to_append)
    else:
        logging.debug(DEBUG_NO_CREATE)

    resolve_identifiers(base_template, options)
    resolve_ids(base_template)
    os.chdir(cwd)
    options["scenario_path"] = Path(options[CreateOptions.DIRECTORY], options["scenario_name"] + ".yaml")
    write_yaml(base_template, options["scenario_path"])


def validate_input_range(input_range: Tuple[int, int], allow_negative: bool) -> NoReturn:
    """
    Raises Exception if input range is no int or float or list of [minimum, maximum], and
    values >= 0 (if `allow_negative` = False)
    """
    if (
        isinstance(input_range, tuple)
        and len(input_range) == 2
        and all(isinstance(i, (int, float)) for i in input_range)
    ):
        if not allow_negative:
            if any(i < 0 for i in input_range):
                log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range, allow_negative))
        if input_range[0] >= input_range[1]:
            log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range, allow_negative))
    else:
        log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range, allow_negative))


def digest_range(input_value: str) -> Tuple[int, int]:
    """Returns Tuple of minimum and maximum integer value digested from `input_value` in expected form"""
    numbers = extract_numbers_from_string(input_value)
    try:
        min_value, max_value = map(float, numbers.split(SEPARATOR))
    except ValueError:
        log_and_raise_critical(ERR_COULD_NOT_MAP_RANGE_VALUES.format(numbers))
    return min_value, max_value


def extract_numbers_from_string(input_value: str) -> str:
    """Returns string in form 'int, int' from given `input_value` by removing RANGE_IDENTIFIER and '(' and ')'"""
    extracted_numbers = input_value.lower().replace(RANGE_IDENTIFIER, "").replace("(", "").replace(")", "")
    return extracted_numbers


def digest_choose(input_value: str) -> List[Union[int, float, str]]:
    """Returns List of options digested from given `input_value` string"""
    given_options = (
        input_value.lower()
        .replace(CHOOSE_IDENTIFIER, "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "")
        .replace('"', "")
        .replace("'", "")
    )
    given_options = given_options.split(SEPARATOR)
    given_options = cast_numeric_strings(given_options)
    return given_options


def cast_numeric_strings(values: List[str]) -> List[Union[int, float, str]]:
    """Returns given List of `values` but numerics are casted in their correct type"""
    casted_values = []
    for value in values:
        try:
            casted_value = int(value)
        except ValueError:
            try:
                casted_value = float(value)
            except ValueError:
                casted_value = value
        casted_values.append(casted_value)
    return casted_values


def digest_pickfile(input_value: str, scenario_path: Path) -> List[str]:
    """Returns List of all files in given directory `input_value`"""
    relative_path = (
        input_value.lower()
        .replace(PICKFILE_IDENTIFIER, "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "")
        .replace('"', "")
        .replace("'", "")
    )
    path_to_dir = Path(scenario_path, relative_path)
    files_in_dir = get_relative_paths_in_dir(path_to_dir, relative_path)
    return files_in_dir


def get_relative_paths_in_dir(path_to_dir: Path, relative_path: str) -> List[str]:
    """Returns files in `path_to_dir` with suffix of `relative_path`"""
    files_in_dir = [
        str(Path(relative_path, f)) for f in os.listdir(path_to_dir) if os.path.isfile(os.path.join(path_to_dir, f))
    ]
    return files_in_dir


def get_value_from_field(input_value: Union[List[Any], Any], options: dict, allow_negative: bool = True) -> Any:
    """
    Returns value stored in `input_value` based on the user specification 'RANGE_IDENTIFIER', 'CHOOSE_IDENTIFIER',
    'PICKFILE_IDENTIFIER' or else just `input_value`.
    In option `RANGE_IDENTIFIER`, `allow_negative` is True as default but can limit allowed range to values >=0.
    In option `PICKFILE_IDENTIFIER`, `options[CreateOptions.DIRECTORY]` is used to get files with relative paths to scenario
    """
    if isinstance(input_value, str):
        if RANGE_IDENTIFIER in input_value.lower():
            input_range = digest_range(input_value)
            validate_input_range(input_range, allow_negative)
            minimum, maximum = input_range
            value = random.uniform(minimum, maximum)
            logging.debug(f"Chose random value '{value}' from '{input_value}'.")
        elif CHOOSE_IDENTIFIER in input_value.lower():
            to_choose = digest_choose(input_value)
            value = random.choice(to_choose)
            logging.debug(f"Chose random value '{value}' from list '{input_value}'.")
        elif PICKFILE_IDENTIFIER in input_value.lower():
            to_pick = digest_pickfile(input_value, options[CreateOptions.DIRECTORY])
            value = random.choice(to_pick)
            logging.debug(f"Chose random file '{value}' from path '{input_value}'.")
        else:
            value = input_value
            logging.debug(f"Received exactly one input value '{input_value}'.")
    else:
        value = input_value
        logging.debug(f"Received exactly one input value '{input_value}'.")
    return value


def replace_ids_in_contracts(contracts: List[dict], agent_id: str, ext_id: Union[dict, None]) -> None:
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


def resolve_identifiers(input_value: Any, options: dict) -> Any:
    """
    Iterates over (potentially nested) `input_value` and returns values from fields
    considering options in `get_value_from_field`
    """
    for key, value in input_value.items():
        if isinstance(value, dict):
            resolve_identifiers(value, options)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    resolve_identifiers(item, options)
                else:
                    input_value[key][index] = get_value_from_field(item, options)
        else:
            input_value[key] = get_value_from_field(value, options)


def get_agent_id(agent_name: str, agent_number: int, n_of_agents_to_create: int) -> str:
    """
    Returns `agent_id` with leading REPLACEMENT_IDENTIFIER for `agent_name` considering its `agent_number`
    and `n_of_agents_to_create`
    """
    agent_id = REPLACEMENT_IDENTIFIER + agent_name
    agent_id += str(agent_number) if n_of_agents_to_create > 1 else ""
    return agent_id


def set_random_seed(defaults: dict, options: dict, trace_file: dict) -> None:
    """Sets random seed if not yet saved to `options['random_seed']`"""
    if not options.get("random_seed"):
        random_seed = get_random_seed(defaults)
        random.seed(random_seed)
        options["random_seed"] = trace_file["random_seed"] = random_seed
        save_seed_to_trace_file(options, random_seed)


def get_random_seed(defaults: dict) -> int:
    """Returns random seed as integer, defined optionally in `defaults['seed']` or from system time in ns instead"""
    if defaults.get("seed"):
        random_seed = defaults["seed"]
    else:
        random_seed = time.time_ns()
    return random_seed
