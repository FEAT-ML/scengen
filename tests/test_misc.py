from pathlib import Path

import pytest

from scengen.files import check_if_valid_yaml_path


class Test:
    @pytest.mark.parametrize("path", ["path/to/file.yaml", "file.YaMl", "./file.yMl", "yaml.yml"])
    def test_check_if_valid_yaml_path__valid(self, path):
        check_if_valid_yaml_path(Path(path))

    @pytest.mark.parametrize("path", ["path/to/file", "file.csv", "./file.yaaaMl", "yaml.txt", "", ".", None])
    def test_check_if_valid_yaml_path__invalid(self, path):
        with pytest.raises(Exception):
            check_if_valid_yaml_path(Path(path))
