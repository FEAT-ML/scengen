<!-- SPDX-FileCopyrightText: 2024 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->
# Upgrading

## 1.0.0
### Paths
#### Results Output File Path
Results of `scengen` are now written to subfolders using the scenario name.
In case you conduct automated post-processing, you may have to adapt the parsing of results accordingly.

#### Relative Series Paths to Scenario Template
All file paths in the scenario `template` are now written relative to this very file.
This allows efficient use and clean separation of input data with generated scenario data.
You may adapt your file structure according to the "Suggested Folder Structure" documented in the `README.md`.

#### Trace File Location
Like all other file paths in the `GeneratorConfig`, the `trace_file` path is now interpreted relative to the location of the `GeneratorConfig`.
You may adapt your file structure according to the "Suggested Folder Structure" as documented in the `README.md`.

### Specific Range Options
The `range` option from previous version was replaced with dedicated `range_int` and `range_float` options.
In case you have applied the `range` option check each occurrence and replace it with the new "_integer" or "_float" options. 

### Renaming 
#### Renaming of Section "Agents" to "Agent" in TypeTemplate
In the `TypeTemplate`, the section `Agents` is now named `Agent` which better represents that only **one** agent type is expected.
Rename this section accordingly.

#### Renaming Replacement Identifier
For better readability, the replacement identifier has been renamed from replacement identifier from `//THISAGENT` to `//THIS_AGENT`.
Rename the occurrences in the Contracts in the TypeTemplates accordingly.

### Updated dependencies
Ensure your AMIRIS-Py dependency is within the new version `amirispy>=2.2,<3` and update accordingly.

### New Generator Sub Package
In case you use individual methods from the `generator.py` in your own pipeline or third-party script, you have to adapt your imports to the new package structure as `generator` is now an own dedicated package.
