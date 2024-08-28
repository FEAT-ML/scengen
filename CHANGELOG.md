<!-- SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: CC0-1.0 -->

# [v1.0.0](https://github.com/FEAT-ML/scengen/releases/tag/v1.0.0) Tba. - Channel 
## Changed:
* **Breaking**: Results are written to subfolders using the scenario name, [#49](https://github.com/FEAT-ML/scengen/issues/49)
* **Breaking**: Series paths are now written relative to scenario `template` file which facilitates clear separation between static input data and generated scenarios, [#54](https://github.com/FEAT-ML/scengen/issues/54)
* **Breaking**: Replaced general `range` option with specific `range_int` and `range_float` options, [#56](https://github.com/FEAT-ML/scengen/issues/56)
* **Breaking**: Renamed section `Agents` to `Agent` in `TypeTemplate` to clarify that one agent type per template is expected, [#58](https://github.com/FEAT-ML/scengen/issues/58)
* **Breaking**: Renamed replacement identifier from `//THISAGENT` to `//THIS_AGENT` for better readability, [#60](https://github.com/FEAT-ML/scengen/issues/60)
* **Breaking**: Update minimum version of dependency `amirispy>=2.2,<3`, [#54](https://github.com/FEAT-ML/scengen/issues/54)
* **Breaking**: `trace_file` is read relatively from the location of the `GeneratorConfig` like all other file paths
* **Breaking**: Changed attribute type of `external_ids` from dict to list, [#59](https://github.com/FEAT-ML/scengen/issues/59)
* Update to new logging implementation allowing more flexible and consistent use of logging, [#55](https://github.com/FEAT-ML/scengen/issues/55)
* `setup.py` to `pyproject.toml`, [#51](https://github.com/FEAT-ML/scengen/issues/51)

## Fixed:
* Fix references to other dynamically created agents in contracts, [#59](https://github.com/FEAT-ML/scengen/issues/59)
* Fix `-o/--output-options` documentation on how to use `fameio` output options, [#54](https://github.com/FEAT-ML/scengen/issues/54)

## Added:
* Raise Warning if not at least one replacement identifier (`//THIS_AGENT`) is found in contracts defined in `type_template`, [#59](https://github.com/FEAT-ML/scengen/issues/59)
* Raise Error if agent identifier in `external_ids` can not be matched to any dynamically created agent, [#59](https://github.com/FEAT-ML/scengen/issues/59)
* New `trace_file` is generated and written to disk if not defined in `GeneratorConfig` or if not found in provided path, [#53](https://github.com/FEAT-ML/scengen/issues/53)

# [v0.2.0](https://github.com/FEAT-ML/scengen/releases/tag/v0.2.0) 2024-04-09 - Barrier bar
## Changed:
* **Breaking**: upgraded dependency to `amirispy>=2.0`, [#47](https://github.com/FEAT-ML/scengen/issues/47)

## Fixed:
* directory `-d/--directory` is created when not present, [#36](https://github.com/FEAT-ML/scengen/issues/36)
* relative paths in CLI are resolved correctly, [#38](https://github.com/FEAT-ML/scengen/issues/38)

## Added:
* Option to pass through FAME-Io output conversion options using `-oo/--output-options`, [#47](https://github.com/FEAT-ML/scengen/issues/47)

# [v0.1.2](https://github.com/FEAT-ML/scengen/releases/tag/v0.1.2) 2023-09-07 - Adriatic abyssal plain
## Fixed:
* execution as installed package works as expected, [#34](https://github.com/FEAT-ML/scengen/issues/34)

# [v0.1.1](https://github.com/FEAT-ML/scengen/releases/tag/v0.1.1) 2023-08-24 - Abyssal plain
## Added: 
* `generation`: options (`choose()`, `pickfile()`, `range()`) can be also used in `base_template` directly (this is recommended, when number of agents is not to be varied.)
* `generation`: `range()` now supports integer and float values

## Fixed:
* `generation`: ensured randomization is working as expected by adding `total_count` from `trace_file.yaml` to random seed
* `generation`: works with no `create` section in `GeneratorConfig` as expected

# [v0.1](https://github.com/FEAT-ML/scengen/releases/tag/v0.1) 2023-08-24 - Abyssal fan
Beta release of core functionalities of `scengen` - the scenario generator for the open electricity market model AMIRIS
