from pathlib import Path

from scengen.cli import resolve_relative_paths


class Test:
    @staticmethod
    def test_resolve_relative_paths__resolve_absolute_path():
        args = {"path": Path(r"Y:\my\path.file")}
        resolved_args = resolve_relative_paths(args)
        assert resolved_args["path"].is_absolute()

    @staticmethod
    def test_resolve_relative_paths__resolve_relative_path():
        args = {"path": Path(r"\my\path.file")}
        resolved_args = resolve_relative_paths(args)
        assert resolved_args["path"].is_absolute()

    @staticmethod
    def test_resolve_relative_paths__non_path_arguments():
        args = {"value": 42}
        resolved_args = resolve_relative_paths(args)
        assert resolved_args["value"] == 42

    @staticmethod
    def test_resolve_relative_paths__none_argument():
        args = {"none_value": None}
        resolved_args = resolve_relative_paths(args)
        assert resolved_args["none_value"] is None
