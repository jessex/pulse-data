# Recidiviz - a data platform for criminal justice reform
# Copyright (C) 2022 Recidiviz, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================
"""Unit tests for the SuperSimulation Initializer object"""

import unittest
from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from recidiviz.calculator.modeling.population_projection.super_simulation.initializer import (
    Initializer,
)


class TestInitializer(unittest.TestCase):
    """Test the SuperSimulation Initializer object runs correctly"""

    def test_fully_hydrate_admissions_happy_path_microsim(self) -> None:
        """Test the Initializer adds rows for all missing time steps for each run date"""
        test_admissions = (
            pd.DataFrame(
                {
                    "time_step": [6, 7, 8] * 2 + [7, 8, 9] * 2,
                    "simulation_group": ["FEMALE"] * 3
                    + ["MALE"] * 3
                    + ["FEMALE"] * 3
                    + ["MALE"] * 3,
                    "compartment": ["earth"] * 12,
                    "admission_to": ["moon"] * 12,
                    "run_date": [datetime(2020, 12, 1)] * 6
                    + [datetime(2021, 1, 1)] * 6,
                    "cohort_population": [3.0, 0.0, 4.0] * 4,
                }
            )
            .sort_values(by=["simulation_group"])
            .reset_index(drop=True)
        )
        # Remove the rows with 0 total population and test that the method adds them back
        admissions_missing_events = test_admissions[
            test_admissions["cohort_population"] > 0
        ]
        hydrated_admissions = Initializer.fully_hydrate_admissions(
            admissions_data=admissions_missing_events,
            microsim=True,
        )
        assert_frame_equal(hydrated_admissions, test_admissions)
