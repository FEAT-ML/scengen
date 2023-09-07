<!-- SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->

[![PyPI version](https://badge.fury.io/py/scengen.svg)](https://badge.fury.io/py/scengen)
[![PyPI license](https://img.shields.io/pypi/l/scengen.svg)](https://badge.fury.io/py/scengen)
[![PyTests](https://github.com/FEAT-ML/scenario-generator/actions/workflows/python-app.yml/badge.svg)](https://github.com/FEAT-ML/scenario-generator/actions/workflows/python-app.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<!-- [![coverage report](docu/coverage.svg)](https://github.com/FEAT-ML/scenario-generator)  to be enabled once badge is created and stored correctly, see issue #30-->

# scengen
`scengen` is a scenario generator for the open electricity market model [AMIRIS](https://dlr-ve.gitlab.io/esy/amiris/home/).

## Installation
The package is not yet deployed on PyPI. Therefore, clone this repository, navigate to this repository in your directory, and install `scengen` to your prefered Python environment with

    pip install .

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

| Option                        | Action                                                                                                                            |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `-n` or `--number`            | Specify number of scenarios to be generated                                                                                       |
| `-c` or `--config`            | Path to `configuration` YAML file defining specifications for creation of scenarios                                               |
| `-j` or `--jar`               | Path to `amiris-core_<version>-jar-with-dependencies.jar`                                                                         |
| `-d` or `--directory`         | Directory to parse scenarios from and write results to                                                                            |
| `-ses` or `--skip_estimation` | Speed-focused approach by omitting the AMIRIS scenario estimation at the expense of bypassing plausibility check (Default: False) |
| `-sev` or `--skip_evaluation` | Speed-focused approach by omitting the AMIRIS result evaluation at the expense of bypassing plausibility check (Default: False)   |

The procedure, handled by the `workflow.py`, is as follows:

1. A `scenario.yaml` is generated by the `generator.py` (see detailed explanation of the `configuration.yaml`)
2. The `estimator.py` checks the scenario for plausibility. See the section on `estimation` for further details.
3. AMIRIS is called by the `runner.py` to run the simulation of `scenario.yaml`
4. The `evaluator.py` checks if the results seem plausible. See the section on `evaluation` for further details. 
5. The next scenario generation is triggered if previous evaluation was negative, or the number of requested scenarios is not yet met

#### `generation`
You have four main options to define input to agents attributes:
1. use a **fixed** value, e.g. `DemandSeries: timeseries/demand/load.csv`
2. use a **random draw** of **dedicated options** (separated by `;`) with Keyword `choose`, e.g. `DemandSeries: choose("timeseries/demand/load1.csv"; timeseries/demand/load2.csv; 1000)`
3. use a **random file** from **directory** with Keyword `pickfile`, e.g. `DemandSeries: pickfile(timeseries/demand)`
4. use a **random draw** in **range** (separated by `;`) with Keyword `range`, e.g. `DemandSeries: range(1000; 1300)`

These can also be applied to all other fields in the `base_template` file.
See also the exemplary files in section `Relevant Files`.

#### `estimation`
The following checks are implemented:
* Checks if there are any installed capacities in the scenario

#### `evaluation`
The following checks are implemented:
* Number of scarcity hours in the calculated simulation falls within a defined share

#### Relevant Files

##### `configuration` YAML
This file is mandatory and defines the main inputs for the creation of new scenarios.
It has the following format with all paths relative to this particular file.

```yaml
defaults:  # defaults used for scenario generation
  # seed: 42 # optional seed used for random number generation otherwise current system time in ns is used
  trace_file: "./tracefile.yaml"  # file used to log created scenarios avoiding duplicates
  base_name: "Germany2019"  # first part of name created by generator; second part of name is unique identifier (number of all scenarios)

base_template: "./template.yaml"  # link to template file containing at least Schema & GeneralProperties

create:  # list of agents to create
  - type_template: "agent_templates/DemandTrader.yaml"
    count: 1  # use fixed value
    # count: range(1; 3)  # use a random draw between range (here: 1 as minimum and 3 as maximum)
    # count: choose(5; 6; 7)  # use a random draw of dedicated options (here: either 5, 6, or 7)
    this_agent: "demandTraderDE" # link to other dynamically created agents by name
    external_ids: 
      exchange: "energyExchangeDE" # dynamically linked to newly created agent referenced herein as "energyExchangeDE"
      forecast: 6 # fixed id used in base_template

  - type_template: "agent_templates/EnergyExchange.yaml" # file containing agent definition(s) and contract(s) with agents in same group or pre-defined agents
    count: 1  # min / max
    this_agent: "energyExchangeDE" # temporary name of this agent for auto-connecting to other agents
```

##### `type_template` YAML
This file consists of two parts.

First, it describes the Attributes of an Agent which shall be dynamically created in `Agents`.
The Agent ID is created by `scengen` directly. 

Optionally, linked `Contracts` are defined in the other section of the file.
With the reserved key `//THISAGENT`, you link to this particular Agent to be created, whereas all other tags with 
prefix `//` link to the particular agent in the `configuration` YAML under section `external_ids`.

```yaml
Agents:
  Type: DemandTrader
  Attributes:
    Loads:
      - ValueOfLostLoad: 10000.0
        DemandSeries: timeseries/demand/load.csv  # use fixed value
      - ValueOfLostLoad: 9999.0
        DemandSeries: choose("timeseries/demand/load1.csv"; timeseries/demand/load2.csv; 1000)  # use a random draw of dedicated options (here: one of the options separated by ';')
      - ValueOfLostLoad: 8888.0
        DemandSeries: pickfile(timeseries/demand)  # use random file from directory
      - ValueOfLostLoad: 7777.0
        DemandSeries: range(1000; 1300)  # use a random draw between range (here: 1000 as minimum and 1300 as maximum)
        
Contracts:
  - SenderId: //exchange  # external agent
    ReceiverId: //THISAGENT  # is referring to this particular agent
    ProductName: GateClosureInfo
    FirstDeliveryTime: -10
    DeliveryIntervalInSteps: 3600

  - SenderId: //THISAGENT
    ReceiverId: //exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    DeliveryIntervalInSteps: 3600

  - SenderId: //exchange
    ReceiverId: //THISAGENT
    ProductName: Awards
    FirstDeliveryTime: 4
    DeliveryIntervalInSteps: 3600
```

##### `trace_file` YAML
The `trace_file` is specified as relative path in the `generation` file. 
Its purpose is to keep track of all created scenario configurations, which ensures that no duplicates are generated.
The `total_count` gets increased by 1, if the generated scenario passed all stages in the workflow (estimation and evaluation).

Its format is as follows:

```yaml
total_count: 2  # number of all scenarios generated
seed: 1234  # random seed stored here if scengen is called
```

### Help
You reach the help menu at any point using `-h` or `--help` which gives you a list of all available options, e.g.:

`scengen --help`


## Cite 
If you use scengen for academic work, please cite:

Christoph Schimeczek, Kristina Nienhaus, Ulrich Frey, Evelyn Sperber, Seyedfarzad Sarfarazi, Felix Nitsch, Johannes Kochems & A. Achraf El Ghazi (2023). AMIRIS: Agent-based Market model for the Investigation of Renewable and Integrated energy Systems. Journal of Open Source Software. doi: [10.21105/joss.05041](https://doi.org/10.21105/joss.05041)

and 

Felix Nitsch, Ulrich Frey, Christoph Schimeczek (2023). scengen: A scenario generator for the open electricity market model AMIRIS. GitHub. https://github.com/FEAT-ML/scenario-generator 


## Contributing
Please see [CONTRIBUTING](CONTRIBUTING.md).

## Available Support
This is a purely scientific project by (at the moment) one research group. 
Thus, there is no paid technical support available.

If you experience any trouble with `scengen` or AMIRIS, you may contact the developers at the [openMod-Forum](https://forum.openmod.org/tag/amiris) or via [amiris@dlr.de](mailto:amiris@dlr.de).
Please report bugs and make feature requests by filing issues following the provided templates (see also [CONTRIBUTING](CONTRIBUTING.md)).
For substantial enhancements, we recommend that you contact us via [amiris@dlr.de](mailto:amiris@dlr.de) for working together on the code in common projects or towards common publications and thus further develop AMIRIS.
