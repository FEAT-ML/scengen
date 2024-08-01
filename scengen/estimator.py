# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Tuple

from fameio.source.loader import load_yaml

from scengen.logs import log_and_raise_critical


class Amiris:
    capacitiy_name = "InstalledPowerInMW"
    energy_carrier_name = "EnergyCarrier"
    fuel_type_name = "FuelType"
    prototype_name = "Prototype"
    technology_name_for_storage = "Storage"
    identifier_for_storage = "Device"
    capacitiy_name_for_storage = "InstalledPowerInMW"


def get_installed_capacity(scenario: dict) -> dict:
    """Returns `dict` of technologies each with list of {agent_id: installed capacity} from given `scenario`"""
    installed_power_by_type = dict()
    for agent in scenario["Agents"]:
        if "Attributes" in agent:
            if Amiris.capacitiy_name in agent["Attributes"]:
                capacity, technology = extract_conventional(agent)
                installed_power_by_type.setdefault(technology, []).append({agent["Id"]: capacity})
            if Amiris.identifier_for_storage in agent["Attributes"]:
                capacity, technology = extract_storage(agent)
                installed_power_by_type.setdefault(technology, []).append({agent["Id"]: capacity})
            if "Plants" in agent["Attributes"]:
                for plant in agent["Attributes"]["Plants"]:
                    capacity = plant["NetCapacityInMW"]
                    technology = agent["Attributes"]["Prototype"]["FuelType"]
                    if "Id" in plant:
                        plant_id = int(plant["Id"])
                        installed_power_by_type.setdefault(technology, []).append({plant_id: capacity})
                    elif capacity > 0:
                        logging.warning("Missing `Id` for powerplant with power of {}".format(capacity))
    return installed_power_by_type


def extract_storage(agent: dict) -> Tuple[float, str]:
    """Return capacity and technology of storage `agent`"""
    capacity = agent["Attributes"][Amiris.identifier_for_storage][Amiris.capacitiy_name_for_storage]
    technology = Amiris.technology_name_for_storage
    return capacity, technology


def extract_conventional(agent: dict) -> Tuple[float, str]:
    """Return capacity and technology of conventional `agent`"""
    capacity = agent["Attributes"][Amiris.capacitiy_name]
    if Amiris.energy_carrier_name in agent["Attributes"]:
        technology = agent["Attributes"][Amiris.energy_carrier_name]
    elif Amiris.fuel_type_name in agent["Attributes"][Amiris.prototype_name]:
        technology = agent["Attributes"][Amiris.prototype_name][Amiris.fuel_type_name]
    else:
        log_and_raise_critical("Found no eligible technology for agent '{}' with id '{}'".format(agent, agent["Id"]))
    return capacity, technology


def accumulate_capacities(capacities: dict) -> float:
    """Returns accumulates `installed_capacities` in MW as float"""
    installed_capacities = 0
    for _, technology in capacities.items():
        for item in technology:
            for _, MW in item.items():
                installed_capacities += MW
    return installed_capacities


def generation_capacity_available(scenario: dict) -> bool:
    """Returns True if there are any installed capacities in given `scenario`"""
    capacities = get_installed_capacity(scenario)
    accumulated_capacities = accumulate_capacities(capacities)
    if not accumulated_capacities > 0:
        logging.warning(f"Accumulated installed capacities seems very low at '{accumulated_capacities}' MW")
        decision = False
    else:
        decision = True
    return decision


def estimate_scenario(options: dict) -> bool:
    """Returns True if scenario passes all individual checks"""
    logging.debug("Calling estimator")
    scenario = load_yaml(options["scenario_path"])
    checks = [generation_capacity_available(scenario)]
    return all(checks)
