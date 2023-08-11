#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
from .generator import generate_scenarios


def main():
    parser = argparse.ArgumentParser(description="Scenario Generator")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create scenarios")
    create_parser.add_argument("-n", "--num", type=int, required=True, help="Number of scenarios to generate")

    args = parser.parse_args()

    if args.command == "create":
        scenarios = generate_scenarios(args.num)
        for scenario in scenarios:
            print(scenario)
