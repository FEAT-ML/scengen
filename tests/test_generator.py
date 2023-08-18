import pytest

from scengen.generator import validate_input_range


class Test:
    def test_validate_input_range__valid_int(self):
        input_range = 5
        validate_input_range(input_range)

    def test_validate_input_range__valid_list(self):
        input_range = [10, 20]
        validate_input_range(input_range)

    def test_validate_input_range__invalid_type(self):
        input_range = "invalid"
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_empty_list(self):
        input_range = []
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_empty_string(self):
        input_range = ""
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_float(self):
        input_range = 3.5
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_list_length(self):
        input_range = [10, 20, 30]
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_list_elements(self):
        input_range = [10, "invalid"]
        with pytest.raises(Exception):
            validate_input_range(input_range)

    def test_validate_input_range__invalid_list_order(self):
        input_range = [20, 10]
        with pytest.raises(Exception):
            validate_input_range(input_range)

