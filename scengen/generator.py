# SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import copy
import os
import random
import re
import time
from pathlib import Path
from typing import Union, List, Dict, Any, Tuple

from fameio.source.loader import load_yaml
from fameio.source.scenario import Contract
from fameio.source.tools import keys_to_lower, ensure_is_list

from scengen.cli import CreateOptions
from scengen.files import write_yaml, save_seed_to_trace_file, get_trace_file
from scengen.logs import log_and_raise_critical, log

numeric = Union[int, float]

SEPARATOR = ";"
RANGE_INT_IDENTIFIER = "range_int"
RANGE_FLOAT_IDENTIFIER = "range_float"
RANGE_IDENTIFIER_DEPRECATED = "range("
CHOOSE_IDENTIFIER = "choose"
PICKFILE_IDENTIFIER = "pickfile"

REPLACEMENT_IDENTIFIER = "//"
KEY_THIS_AGENT = f"{REPLACEMENT_IDENTIFIER}THIS_AGENT"

ERR_INVALID_RANGE_INPUT = (
    "Received invalid range input in form '{}'. Please provide in format "
    f"'{RANGE_INT_IDENTIFIER}(minimum_integer, maximum_integer)' or "
    f"'{RANGE_FLOAT_IDENTIFIER}(minimum_float, maximum_float)'. "
    "Negative integers are considered {}"
)
ERR_INVALID_RANGE_ORDER = "Received invalid range input in form '{}'. First value must be larger equal to second value."
ERR_DEPRECATED_RANGE_IDENTIFIER = "Found deprecated identifier in '{}'. Please use '{}' or '{}' instead."
WARN_ROUNDED_NUMBER_OF_AGENTS = ("Rounded `agent_count` to '{}'. Make sure you provide a single integer or "
                                 "'{}' instead of '{}'.")
ERR_NO_INTEGER = "Expected a single integer or '{}' but received '{}' for `agent_count` instead."
ERR_COULD_NOT_MAP_RANGE_VALUES = "Could not map range values '{}' to minimum, maximum values."
ERR_FAILED_RESOLVE_ID = ("Cannot match replacement Identifier '{}' from Contract '{}' to any existing Agent. "
                         f"Make sure to reference either '{KEY_THIS_AGENT}' or any dynamically created agent.")
DEBUG_NO_CREATE = "No agents to `create` found in Config '{}'"
DEBUG_NO_PATH_TO_BE_REPLACED_IN = "No path to be replaced for Attribute '{}: {}'."
ERR_MISSING_MATCH = "Found identifier(s) '{}' in `external_ids` but could not match with given agent(s) '{}'."
ERR_STATIC_CONTRACT = ("Expected dynamic, but found static contract template instead. Replace either `senderid` or "
                       "`receiverid` with a dynamic replacement_identifier in contract '{}'")


def generate_scenario(options: dict) -> None:
    """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
    log().debug("Generating scenario")
    config = load_yaml(options[CreateOptions.CONFIG])

    defaults = config["defaults"]
    trace_file = get_trace_file(config, options)
    count = trace_file["total_count"]
    _set_random_seed(defaults, options, trace_file)
    options["scenario_name"] = defaults["base_name"] + f"_{count}"
    scenario = load_yaml(Path(options[CreateOptions.CONFIG].parent, config["base_template"]))

    if "create" in config:
        _raise_if_dynamic_match_missing(config["create"])
        add_agents(config["create"], options, scenario)
        add_contracts(config["create"], options, scenario)
    else:
        log().debug(DEBUG_NO_CREATE)

    _resolve_identifiers(scenario, options)
    _resolve_ids(scenario)
    _update_series_paths(scenario, options, Path(config["base_template"]))

    options["scenario_path"] = Path(options[CreateOptions.DIRECTORY], options["scenario_name"] + ".yaml")
    write_yaml(scenario, options["scenario_path"])


def _set_random_seed(defaults: dict, options: dict, trace_file: dict) -> None:
    """Sets random seed if not yet saved to `options['random_seed']`"""
    if not options.get("random_seed"):
        random_seed = _get_random_seed(defaults)
        random.seed(random_seed + trace_file["total_count"])
        options["random_seed"] = trace_file["random_seed"] = random_seed
        save_seed_to_trace_file(options, random_seed)


def _get_random_seed(defaults: dict) -> int:
    """Returns random seed as integer, defined optionally in `defaults['seed']` or from system time in ns instead"""
    if defaults.get("seed"):
        random_seed = defaults["seed"]
    else:
        random_seed = time.time_ns()
    return random_seed


def _raise_if_dynamic_match_missing(create_config: List[Dict]) -> None:
    """Raises Error if any external id(s) cannot be matched to dynamically created agents - skips integer ids"""
    agent_aliases = [config["this_agent"] for config in create_config]
    for config in create_config:
        missing_ids = []
        for external_id_key, external_id_values in config.get("external_ids", {}).items():
            for entry in ensure_is_list(external_id_values):
                if entry not in agent_aliases and isinstance(entry, str):
                    missing_ids.append(entry)
        if missing_ids:
            log_and_raise_critical(ERR_MISSING_MATCH.format(missing_ids, agent_aliases))


def add_agents(agents_to_create: list, options: dict, scenario: dict) -> None:
    """Adds created agents to `scenario`"""
    for agent in agents_to_create:
        type_template = load_yaml(Path(options[CreateOptions.CONFIG].parent, agent["type_template"]))
        agent_type_template = type_template["Agent"]
        n_to_create = _get_number_of_agents_to_create(agent["count"], options)
        agent_name = agent["this_agent"]

        for n in range(n_to_create):
            agent_to_append = copy.deepcopy(agent_type_template)
            agent_to_append["Id"] = _get_agent_id(agent_name, n, n_to_create)
            scenario["Agents"].append(agent_to_append)


def _get_number_of_agents_to_create(agent_count: Union[List[Any], Any], options: dict) -> int:
    """
    Returns an integer number from field `agent_count`
    Accepts float values by rounding to integer, but raises warning to notify user about wrong type,
    for any other data type an Error is raised
    """
    value_from_field = _get_value_from_field(agent_count, options, allow_negative=False)
    if not isinstance(value_from_field, int):
        try:
            rounded_number = round(value_from_field)
            log().warning(WARN_ROUNDED_NUMBER_OF_AGENTS.format(rounded_number, RANGE_INT_IDENTIFIER, agent_count))
            value_from_field = rounded_number
        except TypeError:
            log_and_raise_critical(ERR_NO_INTEGER.format(RANGE_INT_IDENTIFIER, agent_count))
    return value_from_field


def _get_value_from_field(input_value: Union[List[Any], Any], options: dict, allow_negative: bool = True) -> Any:
    """
    Returns value stored in `input_value` based on the user specification 'RANGE_INT_IDENTIFIER',
    'RANGE_INT_IDENTIFIER', 'CHOOSE_IDENTIFIER', 'PICKFILE_IDENTIFIER' or else just `input_value`.
    In range options, `allow_negative` is True as default but can limit allowed range to values >=0.
    In option `PICKFILE_IDENTIFIER`, `options[CreateOptions.DIRECTORY]` is used to get files: paths relative to scenario
    """
    if isinstance(input_value, str):
        if RANGE_IDENTIFIER_DEPRECATED in input_value.lower():
            log_and_raise_critical(
                ERR_DEPRECATED_RANGE_IDENTIFIER.format(input_value, RANGE_INT_IDENTIFIER, RANGE_FLOAT_IDENTIFIER)
            )
        elif RANGE_INT_IDENTIFIER in input_value.lower():
            input_range = _digest_int_range(input_value)
            _validate_input_range(input_range, allow_negative)
            value = random.randint(*input_range)
            log().debug(f"Chose random value '{value}' from '{input_value}'.")
        elif RANGE_FLOAT_IDENTIFIER in input_value.lower():
            input_range = _digest_float_range(input_value)
            _validate_input_range(input_range, allow_negative)
            value = random.uniform(*input_range)
            log().debug(f"Chose random value '{value}' from '{input_value}'.")
        elif CHOOSE_IDENTIFIER in input_value.lower():
            to_choose = _digest_choose(input_value)
            value = random.choice(to_choose)
            log().debug(f"Chose random value '{value}' from list '{input_value}'.")
        elif PICKFILE_IDENTIFIER in input_value.lower():
            to_pick = _digest_pickfile(input_value, options[CreateOptions.DIRECTORY])
            value = random.choice(to_pick)
            log().debug(f"Chose random file '{value}' from path '{input_value}'.")
        else:
            value = input_value
            log().debug(f"Received exactly one input value '{input_value}'.")
    else:
        value = input_value
        log().debug(f"Received exactly one input value '{input_value}'.")
    return value


def _digest_int_range(input_value: str) -> Tuple[int, int]:
    """Returns Tuple of minimum and maximum integer value digested from `input_value` in expected form"""
    numbers = _extract_numbers_from_string(input_value, RANGE_INT_IDENTIFIER)
    try:
        min_value, max_value = map(int, numbers.split(SEPARATOR))
        return min_value, max_value
    except ValueError:
        log_and_raise_critical(ERR_COULD_NOT_MAP_RANGE_VALUES.format(numbers))


def _extract_numbers_from_string(input_value: str, identifier: str) -> str:
    """Returns string in form 'value, value' from given `input_value` by removing `identifier` and '(' and ')'"""
    extracted_numbers = input_value.lower().replace(identifier, "").replace("(", "").replace(")", "")
    return extracted_numbers


def _validate_input_range(input_range: Tuple[numeric, numeric], allow_negative: bool) -> None:
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
        if input_range[0] > input_range[1]:
            log_and_raise_critical(ERR_INVALID_RANGE_ORDER.format(input_range, allow_negative))
    else:
        log_and_raise_critical(ERR_INVALID_RANGE_INPUT.format(input_range, allow_negative))


def _digest_float_range(input_value: str) -> Tuple[float, float]:
    """Returns Tuple of minimum and maximum float value digested from `input_value` in expected form"""
    numbers = _extract_numbers_from_string(input_value, RANGE_FLOAT_IDENTIFIER)
    try:
        min_value, max_value = map(float, numbers.split(SEPARATOR))
        return min_value, max_value
    except ValueError:
        log_and_raise_critical(ERR_COULD_NOT_MAP_RANGE_VALUES.format(numbers))


def _digest_choose(input_value: str) -> List[Union[int, float, str]]:
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
    given_options = _cast_numeric_strings(given_options)
    return given_options


def _cast_numeric_strings(values: List[str]) -> List[Union[int, float, str]]:
    """Returns given List of `values` but numerics are cast in their correct type"""
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


def _digest_pickfile(input_value: str, scenario_path: Path) -> List[str]:
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
    files_in_dir = _get_relative_paths_in_dir(path_to_dir, relative_path)
    return files_in_dir


def _get_relative_paths_in_dir(path_to_dir: Path, relative_path: str) -> List[str]:
    """Returns files in `path_to_dir` with suffix of `relative_path`"""
    files_in_dir = [
        str(Path(relative_path, f)) for f in os.listdir(path_to_dir) if os.path.isfile(os.path.join(path_to_dir, f))
    ]
    return files_in_dir


def _get_agent_id(agent_name: str, agent_number: int, n_of_agents_to_create: int) -> str:
    """
    Returns `agent_id` with leading REPLACEMENT_IDENTIFIER for `agent_name` considering its `agent_number`
    and `n_of_agents_to_create`
    """
    agent_id = REPLACEMENT_IDENTIFIER + agent_name
    agent_id += str(agent_number) if n_of_agents_to_create > 1 else ""
    return agent_id


def add_contracts(agents_to_create: list, options: dict, scenario: dict) -> None:
    """
    Iterates over agents and adds contracts dynamically to `scenario`.
    Note: Ensure that all dynamic agents are already added to the scenario
    """
    for agent in agents_to_create:
        type_template = load_yaml(Path(options[CreateOptions.CONFIG].parent, agent["type_template"]))
        if not type_template.get("Contracts"):
            continue
        id_map = {KEY_THIS_AGENT: _get_matching_ids_from(scenario, ensure_is_list(agent["this_agent"]))}
        for id_key, id_values in agent.get("external_ids", {}).items():
            id_map[REPLACEMENT_IDENTIFIER + id_key] = _get_matching_ids_from(scenario, ensure_is_list(id_values))
        for contract in type_template.get("Contracts"):
            contract = Contract.from_dict(contract)
            _raise_if_static_contract(contract)
            contracts_to_append = _create_contracts(contract, id_map)
            scenario["Contracts"].extend(contracts_to_append)


def _get_matching_ids_from(scenario: Dict, ids_to_look_for: List[Union[str, int]]) -> List:
    """Returns resolved ids of matching `ids_to_look_for` from created agents in `scenario` and static integer ids"""
    resolved_ids = []
    for id_pattern in ids_to_look_for:
        if isinstance(id_pattern, int):
            resolved_ids.append(id_pattern)
        else:
            pattern = re.compile(rf'//{id_pattern}\d*')
            resolved_ids.extend([agent["Id"] for agent in scenario["Agents"] if pattern.match(str(agent["Id"]))])
    return resolved_ids


def _raise_if_static_contract(contract: Contract) -> None:
    """Raises Error if `contract` is static, e.g. has neither dynamic `sender_id` nor `receiver_id`"""
    sender = str(contract.sender_id)
    receiver = str(contract.receiver_id)
    identifier_missing = REPLACEMENT_IDENTIFIER not in sender and REPLACEMENT_IDENTIFIER not in receiver
    if identifier_missing:
        log_and_raise_critical(ERR_STATIC_CONTRACT.format(contract))


def _create_contracts(contract: Contract, id_map: Dict) -> List[Dict]:
    """Returns list of dynamically created `contracts` based on template `contract` and `id_map`"""
    created_contracts = []
    sender_default = str(contract.sender_id)
    receiver_default = str(contract.receiver_id)
    for sender_override in id_map.get(sender_default, [sender_default]):
        for receiver_override in id_map.get(receiver_default, [receiver_default]):
            contract_to_append = copy.deepcopy(contract.to_dict())
            if REPLACEMENT_IDENTIFIER in sender_default:
                # noinspection PyProtectedMember
                contract_to_append[Contract._KEY_SENDER] = sender_override
            if REPLACEMENT_IDENTIFIER in receiver_default:
                # noinspection PyProtectedMember
                contract_to_append[Contract._KEY_RECEIVER] = receiver_override
            created_contracts.append(contract_to_append)
    return created_contracts


def _resolve_identifiers(input_value: Any, options: dict) -> Any:
    """
    Iterates over (potentially nested) `input_value` and returns values from fields
    considering options in `get_value_from_field`
    """
    for key, value in input_value.items():
        if isinstance(value, dict):
            _resolve_identifiers(value, options)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    _resolve_identifiers(item, options)
                else:
                    input_value[key][index] = _get_value_from_field(item, options)
        else:
            input_value[key] = _get_value_from_field(value, options)


def _resolve_ids(scenario: dict) -> None:
    """Resolves in-place all placeholder ID references in Agents & Contracts to unique Ids"""
    active_ids = _get_all_ids_from(scenario)
    replacement_map: Dict[str, int] = {}
    for agent in scenario["Agents"]:
        agent_id = agent["Id"]
        if REPLACEMENT_IDENTIFIER in str(agent_id):
            if agent_id in replacement_map.keys():
                agent["Id"] = replacement_map[agent_id]
            else:
                unique_id = _create_new_unique_id(active_ids)
                agent["Id"] = replacement_map[agent_id] = unique_id
    for contract in scenario["Contracts"]:
        for key, value in contract.items():
            if REPLACEMENT_IDENTIFIER in str(value):
                try:
                    contract[key] = replacement_map[value]
                except KeyError:
                    log_and_raise_critical(ERR_FAILED_RESOLVE_ID.format(value, contract))


def _get_all_ids_from(scenario: dict) -> List[int]:
    """Returns list of unique Agent Ids in given `scenario`"""
    unique_ids = []
    for agent in scenario["Agents"]:
        _append_unique_integer_id(agent["Id"], unique_ids)
    return unique_ids


def _append_unique_integer_id(agent_id: Union[str, int], unique_ids: List[int]):
    """Appends `agent_id` to `unique_ids` if integer and unique"""
    if isinstance(agent_id, int) and agent_id not in unique_ids:
        unique_ids.append(agent_id)


def _create_new_unique_id(unique_ids: List[int]) -> int:
    """Returns new unique integer by adding 1 to the highest Id in `unique_ids`. Adds new Id in-place to `unique_ids`"""
    new_id = max(unique_ids) + 1 if unique_ids else 1
    unique_ids.append(new_id)
    return new_id


def _update_series_paths(scenario: dict, options: dict, template_dir: Path) -> None:
    """
    Appends relative paths directing to `template_dir` for CSV files defined in `scenario`s `Agents`
    and (optional) `StringSets`
    """
    config_dir = Path(options[CreateOptions.CONFIG]).parent
    output_dir = Path(options[CreateOptions.DIRECTORY])
    path_to_append = Path(os.path.relpath(config_dir, start=output_dir), template_dir.parent)
    for agent in scenario["Agents"]:
        agent = keys_to_lower(agent)
        _replace_timeseries_path_in(agent.get("Attributes".lower(), {}), path_to_append)


def _replace_timeseries_path_in(attributes: dict, template_path: Path) -> None:
    """Recursively modify timeseries path in-place in given `attributes` to link to `template_path`"""
    for attribute_name, attribute_value in attributes.items():
        if isinstance(attribute_value, str):
            if attribute_value.lower().endswith(".csv"):
                attributes[attribute_name] = Path(template_path, attribute_value).__str__()
        elif isinstance(attribute_value, dict):
            _replace_timeseries_path_in(attribute_value, template_path)
        elif isinstance(attribute_value, list):
            for item in attribute_value:
                _replace_timeseries_path_in(item, template_path)
        else:
            log().debug(DEBUG_NO_PATH_TO_BE_REPLACED_IN.format(attribute_name, attribute_value))
