# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pandas as pd

from scengen.cli import CreateOptions
from scengen.runner import NAME_SCENARIO_YAML

NAME_ENERGY_EXCHANGE = "EnergyExchange"
NAME_ELECTRICITY_PRICE_COLUMN = "ElectricityPriceInEURperMWH"  # noqa
SCARCITY_PRICE = 3000
THRESHOLD_SHARE_SCARCITY_HOURS = 0.10


def evaluate_scenario(options: dict) -> bool:
    """
    Evaluates results of scenario by checking of occurrences of SCARCITY_PRICE is within THRESHOLD_SHARE_SCARCITY_HOURS

    Args:
        options: options dictionary

    Returns:
        True if occurrences of SCARCITY_PRICE is within THRESHOLD_SHARE_SCARCITY_HOURS, otherwise False
    """
    energy_exchange = pd.read_csv(
        Path(
            options[CreateOptions.DIRECTORY],
            options["scenario_name"],
            Path(NAME_SCENARIO_YAML).stem,
            f"{NAME_ENERGY_EXCHANGE}.csv",
        ),
        sep=";",
    )

    scarcity_hours = (energy_exchange[NAME_ELECTRICITY_PRICE_COLUMN] >= SCARCITY_PRICE).sum()
    within_threshold = scarcity_hours / len(energy_exchange) < THRESHOLD_SHARE_SCARCITY_HOURS

    return within_threshold
