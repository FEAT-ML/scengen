import time
from typing import List, Union, Tuple

import pytest

from scengen.generator import (
    _validate_input_range,
    _append_unique_integer_id,
    _create_new_unique_id,
    _replace_in_dict,
    _get_all_ids_from,
    _get_random_seed,
    _digest_range,
    _extract_numbers_from_string,
    _get_agent_id,
    _cast_numeric_strings,
)


class Test:
    @pytest.mark.parametrize("values", [(10, 20), (1, 2), (1, 11111111111), (0, 3)])
    def test_validate_input_range__valid(self, values: Tuple[int, int]):
        _validate_input_range(values, allow_negative=False)

    @pytest.mark.parametrize("values", [(-10, 0), (-2, 1), (-0, 11111111111)])
    def test_validate_input_range__valid(self, values: Tuple[int, int]):
        _validate_input_range(values, allow_negative=True)

    @pytest.mark.parametrize(
        "values",
        ["any string", [], "", 3.5, -1, 0, [-4, -1], [0, 10], [10, 20, 30], [10, 30], [10, "any string"], (-3, 10)],
    )
    def test_validate_input_range__invalid_type(self, values):
        with pytest.raises(Exception):
            _validate_input_range(values, allow_negative=False)

    @pytest.mark.parametrize(
        "unique_list, new_id, expected",
        [
            ([2, 3], 4, [2, 3, 4]),
            ([2, 3], 3, [2, 3]),
            ([], 3, [3]),
            ([2, 3], "replacement_id", [2, 3]),
        ],
    )
    def test_append_unique_integer_id(self, unique_list: List[int], new_id: Union[str, int], expected: List[int]):
        _append_unique_integer_id(new_id, unique_list)
        assert unique_list == expected

    @pytest.mark.parametrize(
        "unique_list, expected",
        [
            ([2, 3], 4),
            ([], 1),
            ([2, 1000, 3], 1001),
        ],
    )
    def test_create_new_unique_id(self, unique_list: List[int], expected: int):
        new_id = _create_new_unique_id(unique_list)
        assert new_id == expected

    @pytest.mark.parametrize(
        "contracts, replace_identifier, replace_v, expected",
        [
            ([{"Sender": 12, "Receiver": 12}], "//", 42, [{"Sender": 12, "Receiver": 12}]),
            ([{"Sender": 12, "Receiver": "//REPLACE_ME"}], "//", 42, [{"Sender": 12, "Receiver": 42}]),
        ],
    )
    def test_replace_in_dict(
        self, contracts: List[dict], replace_identifier: str, replace_v: str, expected: List[dict]
    ):
        _replace_in_dict(contracts, replace_identifier, replace_v)
        assert contracts == expected

    @pytest.mark.parametrize(
        "scenario, expected",
        [
            ({"Agents": [{"Type": "A", "Id": 2}, {"Type": "B", "Id": 4}, {"Type": "B", "Id": "PLACEHOLDER"}]}, [2, 4]),
            (
                {
                    "Agents": [
                        {"Type": "A", "Id": "PLACEHOLDER1"},
                        {"Type": "B", "Id": "PLACEHOLDER2"},
                        {"Type": "B", "Id": "PLACEHOLDER3"},
                    ]
                },
                [],
            ),
        ],
    )
    def test_get_all_ids_from(self, scenario: dict, expected: list[int]):
        assert _get_all_ids_from(scenario) == expected

    @pytest.mark.parametrize("defaults, expected", [({"seed": 42}, 42)])
    def test_get_random_seed__override_default(self, defaults, expected):
        seed = _get_random_seed(defaults)
        assert seed == expected

    @pytest.mark.parametrize(
        "defaults",
        [
            {"no_seed_here": "certainly_no_seed"},
        ],
    )
    def test_get_random_seed__default(self, defaults):
        seed = _get_random_seed(defaults)
        assert isinstance(seed, int) and 0 <= seed <= time.time_ns()

    @pytest.mark.parametrize("values, expected", [("range(0; 4)", (0, 4)), ("RaNGE(-10; 30)", (-10, 30))])
    def test_digest_range__valid_input(self, values, expected):
        assert _digest_range(values) == expected

    @pytest.mark.parametrize("values", [("rnge(0; 4)"), ("range[10; 30]")])
    def test_digest_range__invalid_input(self, values):
        with pytest.raises(Exception):
            _digest_range(values)

    @pytest.mark.parametrize("values, expected", [("range(0, 4)", "0, 4"), ("RaNgE(1, 23", "1, 23")])
    def test_extract_numbers_from_string(self, values, expected):
        assert _extract_numbers_from_string(values) == expected

    @pytest.mark.parametrize(
        "name, agent_n, total_n, expected",
        [
            ("MyAgent", 2, 3, "//MyAgent2"),
            ("MyAgent", 3, 3, "//MyAgent3"),
            ("MyAgent", 1, 1, "//MyAgent"),
        ],
    )
    def test_get_agent_id(self, name, agent_n, total_n, expected):
        assert _get_agent_id(name, agent_n, total_n) == expected

    @pytest.mark.parametrize(
        "values, expected",
        [
            (["3", "my_string", "4.0"], [3, "my_string", 4.0]),
            ([], []),
            (["path/5.csv"], ["path/5.csv"]),
        ],
    )
    def test_cast_numeric_strings(self, values, expected):
        assert _cast_numeric_strings(values) == expected
