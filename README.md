<!-- SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->

[![PyPI version](https://badge.fury.io/py/scengen.svg)](https://badge.fury.io/py/scengen)
[![PyPI license](https://img.shields.io/pypi/l/scengen.svg)](https://badge.fury.io/py/scengen)

# scengen
`scengen` is a scenario generator for the open electricity market model [AMIRIS](https://dlr-ve.gitlab.io/esy/amiris/home/).

## Installation

    pip install scengen

You may also use `pipx`. For detailed information please refer to the official `pipx` [documentation](https://github.com/pypa/pipx).

    pipx install scengen


### Further Requirements
In order to execute `scengen` correctly, you also require a Java Development Kit (JDK).
JDK must be installed and accessible via your console in which you run `scengen`. 

To test, run `java --version` which should show your JDK version (required: 8 or above).
If `java` command is not found or relates to a Java Runtime Environment (JRE), please download and install JDK (e.g. from [Adoptium](https://adoptium.net/de/temurin/releases/?version=11))


## Usage
Currently, there is one command available:

- `scengen create`: Creates scenarios for AMIRIS

### `scengen create`
Creates AMIRIS scenarios based on user defined input, estimates their plausibility, executes them by calling AMIRIS, and evaluates their final performance.  

| Option                | Action                                                    |
|-----------------------|-----------------------------------------------------------|
| `-n` or `--number`    | Specify number of scenarios to be generated               |
| `-j` or `--jar`       | Path to `amiris-core_<version>-jar-with-dependencies.jar` |
| `-d` or `--directory` | Directory to parse scenarios from and write results to    |


### Help
You reach the help menu at any point using `-h` or `--help` which gives you a list of all available options, e.g.:

`scengen --help`


## Cite 
If you use scengen for academic work, please cite:

Christoph Schimeczek, Kristina Nienhaus, Ulrich Frey, Evelyn Sperber, Seyedfarzad Sarfarazi, Felix Nitsch, Johannes Kochems & A. Achraf El Ghazi (2023). AMIRIS: Agent-based Market model for the Investigation of Renewable and Integrated energy Systems. Journal of Open Source Software. doi: [10.21105/joss.05041](https://doi.org/10.21105/joss.05041)

and 

Felix Nitsch, Ulrich Frey, Christoph Schimeczek (2023). scengen: A Scenario generator for creating scenarios for the open electricity market model AMIRIS. GitHub. https://github.com/FEAT-ML/scenario-generator 


## Contributing
Please see [CONTRIBUTING](CONTRIBUTING.md).

## Available Support
This is a purely scientific project by (at the moment) one research group. 
Thus, there is no paid technical support available.

If you experience any trouble with `scengen` or AMIRIS, you may contact the developers at the [openMod-Forum](https://forum.openmod.org/tag/amiris) or via [amiris@dlr.de](mailto:amiris@dlr.de).
Please report bugs and make feature requests by filing issues following the provided templates (see also [CONTRIBUTING](CONTRIBUTING.md)).
For substantial enhancements, we recommend that you contact us via [amiris@dlr.de](mailto:amiris@dlr.de) for working together on the code in common projects or towards common publications and thus further develop AMIRIS.
