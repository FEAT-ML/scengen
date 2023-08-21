from typing import List, Union

import pytest

from scengen.generator import (
    validate_input_range,
    append_unique_integer_id,
    create_new_unique_id,
    replace_in_dict,
    get_all_ids_from,
)


class Test:
    @pytest.mark.parametrize("values", [5, [10, 20]])
    def test_validate_input_range__valid(self, values):
        validate_input_range(values)

    @pytest.mark.parametrize(
        "values", ["any string", [], "", 3.5, -1, 0, [-4, -1], [0, 10], [10, 20, 30], [30, 10], [10, "any string"]]
    )
    def test_validate_input_range__invalid_type(self, values):
        with pytest.raises(Exception):
            validate_input_range(values)

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
        append_unique_integer_id(new_id, unique_list)
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
        new_id = create_new_unique_id(unique_list)
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
        replace_in_dict(contracts, replace_identifier, replace_v)
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
        assert get_all_ids_from(scenario) == expected
