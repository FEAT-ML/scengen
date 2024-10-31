import time
from typing import List, Union, Tuple, Dict

import pytest
from fameio.source.scenario import Contract

from scengen.generation.digest import _validate_input_range, _digest_int_range, _digest_float_range, _get_agent_id, \
    RANGE_INT_IDENTIFIER, RANGE_FLOAT_IDENTIFIER
from scengen.generation.misc import _append_unique_integer_id, _create_new_unique_id, _get_all_ids_from, \
    _extract_numbers_from_string, _cast_numeric_strings
from scengen.generation.generator import Generator


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
        "contract, id_map, expected",
        [
            (Contract(12, 12, "A", 1, 0,), {"//THIS_AGENT": [123]}, [Contract(12, 12, "A", 1, 0,).to_dict()]),
            (Contract(12, "//THIS_AGENT", "A", 1, 0,), {"//THIS_AGENT": [123]}, [Contract(12, 123, "A", 1, 0,).to_dict()]),
            (Contract(12, "//THIS_AGENT", "A", 1, 0,), {"//THIS_AGENT": [123, 234]}, [Contract(12, 123, "A", 1, 0,).to_dict(), Contract(12, 234, "A", 1, 0,).to_dict()]),
            (Contract("//dynamic", "//THIS_AGENT", "A", 1, 0,), {"//THIS_AGENT": [123, 234], "//dynamic": [1]}, [Contract(1, 123, "A", 1, 0,).to_dict(), Contract(1, 234, "A", 1, 0,).to_dict()]),
            (Contract("//dynamic", "//THIS_AGENT", "A", 1, 0,), {"//THIS_AGENT": [123, 234], "//dynamicc": [10], "//dynamic": [1]}, [Contract(1, 123, "A", 1, 0,).to_dict(), Contract(1, 234, "A", 1, 0,).to_dict()]),
            (Contract("//dynamic", "//THIS_AGENT", "A", 1, 0,), {"//THIS_AGENT": [123, 234], "//dynamic": [1, 11]}, [Contract(1, 123, "A", 1, 0,).to_dict(), Contract(1, 234, "A", 1, 0,).to_dict(), Contract(11, 123, "A", 1, 0,).to_dict(), Contract(11, 234, "A", 1, 0,).to_dict()]),
        ],
    )
    def test_create_contracts(self, contract: Contract, id_map: dict, expected: List[Dict]):
        result = Generator._create_contracts(contract, id_map)
        assert result == expected

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

    @pytest.mark.parametrize("values, expected", [("range_int(0; 4)", (0, 4)), ("RaNGE_inT(-10; 30)", (-10, 30))])
    def test_digest_int_range__valid_input(self, values, expected):
        assert _digest_int_range(values) == expected

    @pytest.mark.parametrize("values, expected", [("range_float(0; 4.2)", (0, 4.2)), ("RaNGE_float(-10.999; 30.1)", (-10.999, 30.1))])
    def test_digest_float_range__valid_input(self, values, expected):
        assert _digest_float_range(values) == expected

    @pytest.mark.parametrize("values", ["rnge_int(0; 4)", "range_int[10; 30]"])
    def test_digest_int_range__invalid_input(self, values):
        with pytest.raises(Exception):
            _digest_int_range(values)

    @pytest.mark.parametrize("values", ["rnge_float(0.1; 4.2)", "range_float[10.2; 30.4]"])
    def test_digest_float_range__invalid_input(self, values):
        with pytest.raises(Exception):
            _digest_float_range(values)

    @pytest.mark.parametrize("values, expected", [("range_int(0, 4)", "0, 4"), ("RaNgE_int(1, 23", "1, 23")])
    def test_extract_ints_from_string(self, values, expected):
        assert _extract_numbers_from_string(values, RANGE_INT_IDENTIFIER) == expected

    @pytest.mark.parametrize("values, expected", [("range_float(0, 4.0)", "0, 4.0"), ("RaNgE_FlOAT(1.2, 23.2", "1.2, 23.2")])
    def test_extract_floats_from_string(self, values, expected):
        assert _extract_numbers_from_string(values, RANGE_FLOAT_IDENTIFIER) == expected

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
