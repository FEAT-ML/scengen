import pytest

from scengen.generator import validate_input_range


class Test:
    @pytest.mark.parametrize("values", [5, [10, 20]])
    def test_validate_input_range__valid(self, values):
        validate_input_range(values)

    @pytest.mark.parametrize("values", ["any string", [], "", 3.5, [10, 20, 30], [30, 10], [10, "any string"]])
    def test_validate_input_range__invalid_type(self, values):
        with pytest.raises(Exception):
            validate_input_range(values)
