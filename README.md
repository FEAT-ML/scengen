<!-- SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyTests](https://github.com/FEAT-ML/scenario-generator/actions/workflows/python-app.yml/badge.svg)](https://github.com/FEAT-ML/scenario-generator/actions/workflows/python-app.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8382789.svg)](https://doi.org/10.5281/zenodo.8382789)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<!-- [![coverage report](docu/coverage.svg)](https://github.com/FEAT-ML/scenario-generator)  to be enabled once badge is created and stored correctly, see issue #30-->

# scengen
`scengen` is a scenario generator for the open electricity market model [AMIRIS](https://dlr-ve.gitlab.io/esy/amiris/home/).

## Setup

### Installation (available with v1.0)

    pip install scengen

You may also use `pipx`. For detailed information please refer to the
official `pipx` [documentation](https://github.com/pypa/pipx).

    pipx install scengen

### Suggested Folder Structure
We suggest the following folder structure for an easy application of `scengen`.

* `amiris/`: folder containing your amiris binary JAR file and the `fameSetup.yaml`
* `generatorConfig/`: folder storing the scengen specific `GeneratorConfig.yaml` and the `tracefile.yaml` 
* `templates/`: folder with all static files for your scenario analysis, e.g. `timeseries/`, `contracts/`, the `scenario_template.yaml` (including the `schema.yaml`), and optional agent-specific `template_{}.yaml` files
* `scenarios/`: folder with generated scenario YAML files and their simulation output in subfolders

```
your_working_dir/
├─ amiris/
│  ├─ amiris_binary.jar
│  └─ fameSetup.yaml
├─ generatorConfig/
│  ├─ GeneratorConfig.yaml
│  └─ tracefile.yaml
├─ templates/
│  ├─ contracts/
│  ├─ timeseries/
│  ├─ my_dynamic_agent_template.yaml
│  ├─ schema.yaml
│  └─ scenario_template.yaml
└─ scenarios/
   ├─ generated_1/
   └─ generated_1.yaml
```

### Further Requirements
In order to execute `scengen` correctly, you also require a Java Development Kit (JDK).
JDK must be installed and accessible via your console in which you run `scengen`.

To test, run `java -version` which should show your JDK version (required: 11 or above).
If `java` command is not found or relates to a Java Runtime Environment (JRE), please download and install JDK (e.g. from [Adoptium](https://adoptium.net/de/temurin/releases/?version=11)).

## Usage
Currently, there is one command available:

- `scengen create`: Creates scenarios for AMIRIS

### `scengen create`
Creates AMIRIS scenarios based on user defined input, estimates their plausibility, executes them by calling AMIRIS, and evaluates their final performance.

| Option                        | Action                                                                                                                                                                                                                                         |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-n` or `--number`            | Specify number of scenarios to be generated                                                                                                                                                                                                    |
| `-c` or `--config`            | Path to `configuration` YAML file defining specifications for creation of scenarios                                                                                                                                                            |
| `-j` or `--jar`               | Path to `amiris-core_<version>-jar-with-dependencies.jar`                                                                                                                                                                                      |
| `-d` or `--directory`         | Directory to parse scenarios from and write results to                                                                                                                                                                                         |
| `-ses` or `--skip_estimation` | Speed-focused approach by omitting the AMIRIS scenario estimation at the expense of bypassing plausibility checks (Default: False)                                                                                                             |
| `-sev` or `--skip_evaluation` | Speed-focused approach by omitting the AMIRIS result evaluation at the expense of bypassing plausibility checks (Default: False)                                                                                                               |
| `-oo` or `--output-options`   | Optional arguments to override default output [conversion arguments of fameio](https://gitlab.com/fame-framework/fame-io/-/blob/main/README.md#read-fame-results) (e.g. `-oo "-l critical"` only forwards critical `fameio` logs to scengen)   |
| `-nc` or `--no-checks`        | Skip checks for Java installation and correct version to increase speed                                                                                                                                                                        |

The procedure, handled by `workflow.py`, is as follows:

1. A `scenario.yaml` is generated by `generator.py` (see detailed explanation of the `configuration.yaml`).
2. `estimator.py` checks the scenario for plausibility - see section `estimation` for further details.
3. AMIRIS is called by `runner.py` to run the simulation of `scenario.yaml`.
4. `evaluator.py` checks if the results seem plausible - see section `evaluation` for further details. 
5. The next scenario generation is triggered if the total number of (positively evaluated) scenarios does not yet met the number of requested scenarios.

#### `generation`
You have four main options to define input to agents attributes:
1. use a **fixed** value, e.g. `DemandSeries: timeseries/demand/load.csv`
2. use a **random draw** of **dedicated options** (separated by `;`) with keyword `choose`, e.g. `DemandSeries: choose("timeseries/demand/load1.csv"; timeseries/demand/load2.csv; 1000)`
3. use a **random file** from a **directory** with keyword `pickfile`, e.g. `DemandSeries: pickfile(timeseries/demand)`
4. use a **random draw** in a **range** (exactly two values separated by `;`) with keyword `range_int` (integer) or `range_float` (floats), e.g. `DemandSeries: range_int(1000; 1300)`

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
It has the following format with all paths **relative** to this particular file.

```yaml
defaults:  # defaults used for scenario generation
  # seed: 42 # optional seed used for random number generation otherwise current system time in ns is used
  trace_file: "./tracefile.yaml"  # mandatory file used to log created scenarios avoiding duplicates
  base_name: "Germany2019"  # first part of name created by generator; second part of name is unique identifier (number of all scenarios)

base_template: "./template.yaml"  # link to template file containing at least Schema & GeneralProperties sections

create:  # list of agents to create
  - type_template: "agent_templates/DemandTrader.yaml"
    count: 3  # creates a fixed number of agents with the same template (here: 3)
    # count: range_int(1; 3)  # create a random numer of agents between given minimum and maximum (here: 1 as minimum and 3 as maximum)
    # count: choose(5; 6; 7)  # create a random number of agents by choosing one of the given options (here: either 5, 6, or 7)
    this_agent: "demandTraderDE" # other agents can link to those created by this template by using this name
    external_ids:  # provide either identifier, static agent id as single entry or as list in order to replace the identifiers (here: keys) in the type_template's contracts 
      exchange: ["energyExchangeDE", 1] # replaces "//exchange" in type_template by linking to newly created agent(s) referenced herein as "energyExchangeDE" plus a static agent with id 1
      forecast: 6 # fixed id to replace "//forecast" in type_template

  - type_template: "agent_templates/EnergyExchange.yaml" # file containing the agent definition and contract(s) with agents in same group or pre-defined agents
    count: 1  # min / max
    this_agent: "energyExchangeDE" # other agents can link to that created by this template by using this name
```

##### `type_template` YAML
This file consists of two parts, namely `Agent` and `Contracts`.

The section `Agent` describes the Attributes of one particular Agent type which shall be dynamically created and added to the `base_template`.
The Agent ID is created by `scengen` directly. 

Optionally, linked `Contracts` are defined in the other section of the file.
With the reserved key `//THIS_AGENT`, you link to this particular Agent to be created, whereas all other tags with 
prefix `//` link to the particular agent in the `configuration` YAML under section `external_ids`.
If any "static" contract template is found (meaning that neither `SenderId` nor `ReceiverId` consists of a `replacement` identifier, an Error is raised.
Please specify any such contract in the `base_template` as described in the section on the `configuration` YAML.


```yaml
Agent:
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
        DemandSeries: range_int(1000; 1300)  # use a random draw of integers in range (here: 1000 as minimum and 1300 as maximum)
      - ValueOfLostLoad: 7777.0
        DemandSeries: range_float(3.14; 42.42)  # use a random draw of floats in range (here: 3.14 as minimum and 42.42 as maximum)
        
Contracts:
  - SenderId: //exchange  # external agent
    ReceiverId: //THIS_AGENT  # is referring to this particular agent
    ProductName: GateClosureInfo
    FirstDeliveryTime: -10
    DeliveryIntervalInSteps: 3600

  - SenderId: //THIS_AGENT
    ReceiverId: //exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    DeliveryIntervalInSteps: 3600

  - SenderId: //exchange
    ReceiverId: //THIS_AGENT
    ProductName: Awards
    FirstDeliveryTime: 4
    DeliveryIntervalInSteps: 3600
```

##### `trace_file` YAML
The mandatory `trace_file` is specified as relative path in the `generation` file. 
Its purpose is to keep track of all created scenario configurations, which ensures that no duplicates are generated.
The `total_count` gets increased by 1, if the generated scenario passed all stages in the workflow (estimation and evaluation).

If no such file is defined in the `GeneratorConfig`, a Warning is raised and a new file with file name 
`trace_file_'%Y-%m-%d_%H%M%S'.yaml` is written to disk.
If the file cannot be found in the specified path, a new `trace_file` is created using the specified file path.

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

Felix Nitsch, Ulrich Frey, Christoph Schimeczek (2023). scengen - A Scenario Generator for the Open Electricity Market Model AMIRIS. Zenodo. doi: [10.5281/zenodo.8382790](https://doi.org/10.5281/zenodo.8382790)

## Contributing
Please see [CONTRIBUTING](CONTRIBUTING.md).

## Available Support
This is a purely scientific project by (at the moment) one research group. 
Thus, there is no paid technical support available.

If you experience any trouble with `scengen` or AMIRIS, you may contact the developers at the [openMod-Forum](https://forum.openmod.org/tag/amiris) or via [amiris@dlr.de](mailto:amiris@dlr.de).
Please report bugs and make feature requests by filing issues following the provided templates (see also [CONTRIBUTING](CONTRIBUTING.md)).
For substantial enhancements, we recommend that you contact us via [amiris@dlr.de](mailto:amiris@dlr.de) for working together on the code in common projects or towards common publications and thus further develop AMIRIS.
