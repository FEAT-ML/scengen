<!-- SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: CC0-1.0 -->

# Tba - v0.1.3 (Tba.)
## Fixed:
*  directory `-d/--directory` is created when not present, [#36](https://github.com/FEAT-ML/scengen/issues/36)

# Adriatic abyssal plain - [v0.1.2](https://github.com/FEAT-ML/scengen/releases/tag/v0.1.2) (2023-09-07)
## Fixed:
* execution as installed package works as expected, [#34](https://github.com/FEAT-ML/scengen/issues/34)

# Abyssal plain - [v0.1.1](https://github.com/FEAT-ML/scengen/releases/tag/v0.1.1) (2023-08-24)
## Added: 
* `generation`: options (`choose()`, `pickfile()`, `range()`) can be also used in `base_template` directly (this is recommended, when number of agents is not to be varied.)
* `generation`: `range()` now supports integer and float values

## Fixed:
* `generation`: ensured randomization is working as expected by adding `total_count` from `trace_file.yaml` to random seed
* `generation`: works with no `create` section in `GeneratorConfig` as expected

# Abyssal fan - [v0.1](https://github.com/FEAT-ML/scengen/releases/tag/v0.1) (2023-08-24)
Beta release of core functionalities of `scengen` - the scenario generator for the open electricity market model AMIRIS
