# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pandas as pd
from amirispy.source.cli import RunOptions

from scengen.logs import log

NAME_ENERGY_EXCHANGE = "DayAheadMarketSingleZone"
NAME_ELECTRICITY_PRICE_COLUMN = "ElectricityPriceInEURperMWH"  # noqa
SCARCITY_PRICE = 3000
THRESHOLD_SHARE_SCARCITY_HOURS = 0.10


def evaluate_scenario(options: dict) -> bool:
    """Returns True if results pass all individual checks"""
    log().debug("Calling evaluator")
    checks = [scarcity_occurrence(options)]
    return all(checks)


def scarcity_occurrence(options: dict) -> bool:
    """Returns True if occurrences of SCARCITY_PRICE is within THRESHOLD_SHARE_SCARCITY_HOURS"""
    path_to_exchange = Path(options[RunOptions.OUTPUT], f"{NAME_ENERGY_EXCHANGE}.csv")
    energy_exchange = pd.read_csv(path_to_exchange, sep=";")
    scarcity_hours = (energy_exchange[NAME_ELECTRICITY_PRICE_COLUMN] >= SCARCITY_PRICE).sum()
    n_of_tolerated_hours = round(len(energy_exchange) * THRESHOLD_SHARE_SCARCITY_HOURS)
    if scarcity_hours > n_of_tolerated_hours:
        decision = False
        log().warning(f"Number of scarcity hours ({scarcity_hours}) exceeds tolerance of {n_of_tolerated_hours} hours.")
    else:
        decision = True
    return decision
