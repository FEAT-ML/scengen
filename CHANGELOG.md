<!-- SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: CC0-1.0 -->

## *Note: `scengen` has been renamed to `AMIRIS-Scengen` and is now hosted at GitLab, see https://gitlab.com/dlr-ve/esy/amiris/amiris-scengen*

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
