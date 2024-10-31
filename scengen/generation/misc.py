import os
import re
from pathlib import Path
from typing import Union


def append_unique_integer_id(agent_id: Union[str, int], unique_ids: list[int]):
    """Appends `agent_id` to `unique_ids` if integer and unique"""
    if isinstance(agent_id, int) and agent_id not in unique_ids:
        unique_ids.append(agent_id)


def get_matching_ids_from(scenario: dict, ids_to_look_for: list[Union[str, int]]) -> list:
    """Returns resolved ids of matching `ids_to_look_for` from created agents in `scenario` and static integer ids"""
    resolved_ids = []
    for id_pattern in ids_to_look_for:
        if isinstance(id_pattern, int):
            resolved_ids.append(id_pattern)
        else:
            pattern = re.compile(rf'//{id_pattern}\d*')
            resolved_ids.extend([agent["Id"] for agent in scenario["Agents"] if pattern.match(str(agent["Id"]))])
    return resolved_ids


def get_all_ids_from(scenario: dict) -> list[int]:
    """Returns list of unique Agent Ids in given `scenario`"""
    unique_ids = []
    for agent in scenario["Agents"]:
        append_unique_integer_id(agent["Id"], unique_ids)
    return unique_ids


def create_new_unique_id(unique_ids: list[int]) -> int:
    """Returns new unique integer by adding 1 to the highest Id in `unique_ids`. Adds new Id in-place to `unique_ids`"""
    new_id = max(unique_ids) + 1 if unique_ids else 1
    unique_ids.append(new_id)
    return new_id


def cast_numeric_strings(values: list[str]) -> list[Union[int, float, str]]:
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


def get_relative_paths_in_dir(path_to_dir: Path, relative_path: str) -> list[str]:
    """Returns files in `path_to_dir` with suffix of `relative_path`"""
    files_in_dir = [
        str(Path(relative_path, f)) for f in os.listdir(path_to_dir) if os.path.isfile(os.path.join(path_to_dir, f))
    ]
    return files_in_dir


def extract_numbers_from_string(input_value: str, identifier: str) -> str:
    """Returns string in form 'value, value' from given `input_value` by removing `identifier` and '(' and ')'"""
    extracted_numbers = input_value.lower().replace(identifier, "").replace("(", "").replace(")", "")
    return extracted_numbers
