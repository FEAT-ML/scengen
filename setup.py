#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from setuptools import find_packages, setup

__author__ = [
    "Felix Nitsch",  # noqa
    "Ulrich Frey",  # noqa
    "Christoph Schimeczek",  # noqa
]
__copyright__ = "Copyright 2023, German Aerospace Center (DLR)"

__license__ = "Apache License 2.0"
__maintainer__ = "Felix Nitsch"  # noqa
__email__ = "amiris@dlr.de"
__status__ = "Production"


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="scengen",  # noqa
    version="0.1.2",
    description="Scenario generator for the open electricity market model AMIRIS",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords=[
        "scenario",
        "generator",
        "AMIRIS",
        "agent-based modelling",
        "electricity market",
        "simulation",
    ],
    url="https://gitlab.com/dlr-ve/esy/amiris/",
    author=", ".join(__author__),
    author_email=__email__,
    license=__license__,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "scengen=scengen:main",  # noqa
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "amirispy>=1.3,<2",
        "fameio>=1.8.1,<2",
        "pandas>2.0,<3",
    ],
    extras_require={"dev": ["pytest>=7.2"]},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
)
