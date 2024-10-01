import os
import random
from pathlib import Path
from typing import Union, List, Any, Dict, Tuple

from fameio.source.tools import keys_to_lower

from scengen.cli import CreateOptions
from scengen.generator.misc import _get_all_ids_from, _create_new_unique_id, _cast_numeric_strings, \
    _get_relative_paths_in_dir, _extract_numbers_from_string
from scengen.logs import log, log_and_raise_critical

numeric = Union[int, float]


class GeneratorConstants:
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
    f"'{GeneratorConstants.RANGE_INT_IDENTIFIER}(minimum_integer, maximum_integer)' or "
    f"'{GeneratorConstants.RANGE_FLOAT_IDENTIFIER}(minimum_float, maximum_float)'. "
    "Negative integers are considered {}"
)
ERR_INVALID_RANGE_ORDER = "Received invalid range input in form '{}'. First value must be larger equal to second value."
ERR_MISSING_MATCH = "Found identifier(s) '{}' in `external_ids` but could not match with given agent(s) '{}'."
ERR_STATIC_CONTRACT = ("Expected dynamic, but found static contract template instead. Replace either `senderid` or "
                       "`receiverid` with a dynamic replacement_identifier in contract '{}'")
WARN_ROUNDED_NUMBER_OF_AGENTS = ("Rounded `agent_count` to '{}'. Make sure you provide a single integer or "
                                 "'{}' instead of '{}'.")
ERR_DEPRECATED_RANGE_IDENTIFIER = "Found deprecated identifier in '{}'. Please use '{}' or '{}' instead."
ERR_NO_INTEGER = "Expected a single integer or '{}' but received '{}' for `agent_count` instead."
DEBUG_NO_PATH_TO_BE_REPLACED_IN = "No path to be replaced for Attribute '{}: {}'."
ERR_COULD_NOT_MAP_RANGE_VALUES = "Could not map range values '{}' to minimum, maximum values."
ERR_FAILED_RESOLVE_ID = ("Cannot match replacement Identifier '{}' from Contract '{}' to any existing Agent. "
                         f"Make sure to reference either '{GeneratorConstants.KEY_THIS_AGENT}' "
                         f"or any dynamically created agent.")


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
            log().warning(WARN_ROUNDED_NUMBER_OF_AGENTS.format(rounded_number, GeneratorConstants.RANGE_INT_IDENTIFIER, agent_count))
            value_from_field = rounded_number
        except TypeError:
            log_and_raise_critical(ERR_NO_INTEGER.format(GeneratorConstants.RANGE_INT_IDENTIFIER, agent_count))
    return value_from_field


def _get_value_from_field(input_value: Union[List[Any], Any], options: dict, allow_negative: bool = True) -> Any:
    """
    Returns value stored in `input_value` based on the user specification 'RANGE_INT_IDENTIFIER',
    'RANGE_INT_IDENTIFIER', 'CHOOSE_IDENTIFIER', 'PICKFILE_IDENTIFIER' or else just `input_value`.
    In range options, `allow_negative` is True as default but can limit allowed range to values >=0.
    In option `PICKFILE_IDENTIFIER`, `options[CreateOptions.DIRECTORY]` is used to get files: paths relative to scenario
    """
    if isinstance(input_value, str):
        if GeneratorConstants.RANGE_IDENTIFIER_DEPRECATED in input_value.lower():
            log_and_raise_critical(
                ERR_DEPRECATED_RANGE_IDENTIFIER.format(input_value, GeneratorConstants.RANGE_INT_IDENTIFIER, GeneratorConstants.RANGE_FLOAT_IDENTIFIER)
            )
        elif GeneratorConstants.RANGE_INT_IDENTIFIER in input_value.lower():
            input_range = _digest_int_range(input_value)
            _validate_input_range(input_range, allow_negative)
            value = random.randint(*input_range)
            log().debug(f"Chose random value '{value}' from '{input_value}'.")
        elif GeneratorConstants.RANGE_FLOAT_IDENTIFIER in input_value.lower():
            input_range = _digest_float_range(input_value)
            _validate_input_range(input_range, allow_negative)
            value = random.uniform(*input_range)
            log().debug(f"Chose random value '{value}' from '{input_value}'.")
        elif GeneratorConstants.CHOOSE_IDENTIFIER in input_value.lower():
            to_choose = _digest_choose(input_value)
            value = random.choice(to_choose)
            log().debug(f"Chose random value '{value}' from list '{input_value}'.")
        elif GeneratorConstants.PICKFILE_IDENTIFIER in input_value.lower():
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


def _get_agent_id(agent_name: str, agent_number: int, n_of_agents_to_create: int) -> str:
    """
    Returns `agent_id` with leading REPLACEMENT_IDENTIFIER for `agent_name` considering its `agent_number`
    and `n_of_agents_to_create`
    """
    agent_id = GeneratorConstants.REPLACEMENT_IDENTIFIER + agent_name
    agent_id += str(agent_number) if n_of_agents_to_create > 1 else ""
    return agent_id


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


def _digest_int_range(input_value: str) -> Tuple[int, int]:
    """Returns Tuple of minimum and maximum integer value digested from `input_value` in expected form"""
    numbers = _extract_numbers_from_string(input_value, GeneratorConstants.RANGE_INT_IDENTIFIER)
    try:
        min_value, max_value = map(int, numbers.split(GeneratorConstants.SEPARATOR))
        return min_value, max_value
    except ValueError:
        log_and_raise_critical(ERR_COULD_NOT_MAP_RANGE_VALUES.format(numbers))


def _digest_float_range(input_value: str) -> Tuple[float, float]:
    """Returns Tuple of minimum and maximum float value digested from `input_value` in expected form"""
    numbers = _extract_numbers_from_string(input_value, GeneratorConstants.RANGE_FLOAT_IDENTIFIER)
    try:
        min_value, max_value = map(float, numbers.split(GeneratorConstants.SEPARATOR))
        return min_value, max_value
    except ValueError:
        log_and_raise_critical(ERR_COULD_NOT_MAP_RANGE_VALUES.format(numbers))


def _digest_choose(input_value: str) -> List[Union[int, float, str]]:
    """Returns List of options digested from given `input_value` string"""
    given_options = (
        input_value.lower()
        .replace(GeneratorConstants.CHOOSE_IDENTIFIER, "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "")
        .replace('"', "")
        .replace("'", "")
    )
    given_options = given_options.split(GeneratorConstants.SEPARATOR)
    given_options = _cast_numeric_strings(given_options)
    return given_options


def _digest_pickfile(input_value: str, scenario_path: Path) -> List[str]:
    """Returns List of all files in given directory `input_value`"""
    relative_path = (
        input_value.lower()
        .replace(GeneratorConstants.PICKFILE_IDENTIFIER, "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "")
        .replace('"', "")
        .replace("'", "")
    )
    path_to_dir = Path(scenario_path, relative_path)
    files_in_dir = _get_relative_paths_in_dir(path_to_dir, relative_path)
    return files_in_dir


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
        if GeneratorConstants.REPLACEMENT_IDENTIFIER in str(agent_id):
            if agent_id in replacement_map.keys():
                agent["Id"] = replacement_map[agent_id]
            else:
                unique_id = _create_new_unique_id(active_ids)
                agent["Id"] = replacement_map[agent_id] = unique_id
    for contract in scenario["Contracts"]:
        for key, value in contract.items():
            if GeneratorConstants.REPLACEMENT_IDENTIFIER in str(value):
                try:
                    contract[key] = replacement_map[value]
                except KeyError:
                    log_and_raise_critical(ERR_FAILED_RESOLVE_ID.format(value, contract))
