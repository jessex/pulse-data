# Recidiviz - a data platform for criminal justice reform
# Copyright (C) 2020 Recidiviz, Inc.
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
"""Test the PopulationSimulation object"""
import unittest
from copy import deepcopy
from typing import Dict, Optional, cast
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal

from recidiviz.calculator.modeling.population_projection.population_simulation.population_simulation_factory import (
    PopulationSimulation,
    PopulationSimulationFactory,
)
from recidiviz.calculator.modeling.population_projection.spark_policy import SparkPolicy
from recidiviz.calculator.modeling.population_projection.super_simulation.initializer import (
    SimulationInputData,
    UserInputs,
)
from recidiviz.calculator.modeling.population_projection.transition_table import (
    TransitionTable,
)


class TestPopulationSimulation(unittest.TestCase):
    """Test the PopulationSimulation class runs correctly"""

    test_admissions_data = pd.DataFrame()
    test_transitions_data = pd.DataFrame()
    test_population_data = pd.DataFrame()
    user_inputs: UserInputs = cast(UserInputs, None)
    simulation_architecture: Dict[str, str] = {}
    macro_population_simulation: Optional[PopulationSimulation] = None
    macro_projection = pd.DataFrame()

    def setUp(self) -> None:
        self.test_admissions_data = pd.DataFrame(
            {
                "cohort_population": [4, 3] * 2,
                "simulation_group": ["NAR"] * 2 + ["BUR"] * 2,
                "admission_to": [
                    "supervision",
                    "prison",
                ]
                * 2,
                "compartment": [
                    "pretrial",
                    "pretrial",
                ]
                * 2,
                "time_step": [0] * 4,
            }
        )

        self.test_transitions_data = pd.DataFrame(
            {
                "compartment_duration": [1, 1, 2] * 2,
                "cohort_portion": [4, 2, 2] * 2,
                "simulation_group": ["NAR"] * 3 + ["BUR"] * 3,
                "outflow_to": ["supervision", "prison", "supervision"] * 2,
                "compartment": ["prison", "supervision", "prison"] * 2,
            }
        )

        self.test_population_data = pd.DataFrame(
            {
                "compartment_population": [10] * 10,
                "compartment": ["prison"] * 10,
                "simulation_group": ["NAR"] * 5 + ["BUR"] * 5,
                "time_step": list(range(-4, 1)) * 2,
            }
        )

        self.user_inputs = UserInputs(
            projection_time_steps=10,
            start_time_step=0,
            constant_admissions=True,
            speed_run=False,
        )
        self.simulation_architecture = {
            "pretrial": "shell",
            "prison": "full",
            "supervision": "full",
        }
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        self.macro_population_simulation = (
            PopulationSimulationFactory.build_population_simulation(
                self.user_inputs, [], -5, test_data_inputs
            )
        )
        self.macro_projection = self.macro_population_simulation.simulate_policies()

    def test_simulation_forces_complete_user_inputs_dict(self) -> None:
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        test_user_inputs = deepcopy(self.user_inputs)
        test_user_inputs.speed_run = None
        with self.assertRaises(ValueError):
            _ = PopulationSimulationFactory.build_population_simulation(
                test_user_inputs, [], -5, test_data_inputs
            )

    def test_microsimulation_can_initialize_with_policy_list(self) -> None:
        """Run a policy scenario with a microsimulation to make sure it doesn't break along the way."""
        policy_list = [
            SparkPolicy(
                "supervision",
                "NAR",
                self.user_inputs.start_time_step + 2,
                False,
                TransitionTable.test_non_retroactive_policy,
            )
        ]
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        policy_sim = PopulationSimulationFactory.build_population_simulation(
            self.user_inputs, policy_list, -5, test_data_inputs
        )

        policy_sim.simulate_policies()

    def test_baseline_with_backcast_projection_on(self) -> None:
        """Assert that the simulation results has negative time steps when the back-cast is enabled"""
        assert_index_equal(
            self.macro_projection.index.unique().sort_values(),
            pd.Int64Index(range(-5, 10)),
        )

    def test_baseline_with_backcast_projection_off(self) -> None:
        """Assert that microsim simulation results only have positive time steps"""
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        population_simulation = PopulationSimulationFactory.build_population_simulation(
            self.user_inputs, [], 0, test_data_inputs
        )
        projection = population_simulation.simulate_policies()

        assert_index_equal(
            projection.index.unique().sort_values(), pd.Index(range(10), dtype=int)
        )

    def test_unused_data_raises_warning(self) -> None:
        """Assert that PopulationSimulation throws an error when some input data goes unused"""
        non_disaggregated_admissions_data = self.test_admissions_data.copy()
        non_disaggregated_admissions_data.simulation_group = None
        non_disaggregated_transitions_data = self.test_transitions_data.copy()
        non_disaggregated_transitions_data.simulation_group = None

        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=pd.concat(
                [self.test_transitions_data, non_disaggregated_transitions_data]
            ),
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        with patch("logging.Logger.warning") as mock:
            _ = PopulationSimulationFactory.build_population_simulation(
                self.user_inputs, [], -5, test_data_inputs
            )
            mock.assert_called_once()
            self.assertEqual(
                mock.mock_calls[0].args[0], "Some transitions data left unused: %s"
            )
        test_data_inputs = SimulationInputData(
            admissions_data=pd.concat(
                [self.test_admissions_data, non_disaggregated_admissions_data]
            ),
            transitions_data=self.test_transitions_data,
            population_data=self.test_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        with patch("logging.Logger.warning") as mock:
            _ = PopulationSimulationFactory.build_population_simulation(
                self.user_inputs, [], -5, test_data_inputs
            )
            mock.assert_called_once()
            self.assertEqual(
                mock.mock_calls[0].args[0], "Some admissions data left unused: %s"
            )

    def test_doubled_populations_doubles_simulation_populations(self) -> None:
        """Validates population scaling is actually scaling populations"""

        doubled_population_data = self.test_population_data.copy()
        doubled_population_data.compartment_population *= 2
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=doubled_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        doubled_population_simulation = (
            PopulationSimulationFactory.build_population_simulation(
                self.user_inputs, [], -5, test_data_inputs
            )
        )

        doubled_projection = doubled_population_simulation.simulate_policies()

        for _, row in doubled_population_data.iterrows():
            baseline_pop = self.macro_projection.loc[
                (self.macro_projection.compartment == row.compartment)
                & (self.macro_projection.time_step == row.time_step),
                "compartment_population",
            ].iloc[0]
            doubled_pop = doubled_projection.loc[
                (doubled_projection.compartment == row.compartment)
                & (doubled_projection.time_step == row.time_step),
                "compartment_population",
            ].iloc[0]
            self.assertEqual(round(baseline_pop * 2), round(doubled_pop))

    def test_coarse_population_data(self) -> None:
        """
        Test that PopulationSimulation can handle population_data with one less disaggregation axis
            than other data dfs
        """
        coarse_population_data = (
            self.test_population_data.groupby(["compartment", "time_step"])
            .sum()
            .reset_index()
        )
        test_data_inputs = SimulationInputData(
            admissions_data=self.test_admissions_data,
            transitions_data=self.test_transitions_data,
            population_data=coarse_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=False,
            microsim_data=pd.DataFrame(),
            should_initialize_compartment_populations=False,
            should_scale_populations_after_step=True,
            override_cross_flow_function=None,
        )
        coarse_macro_population_simulation = (
            PopulationSimulationFactory.build_population_simulation(
                self.user_inputs, [], -5, test_data_inputs
            )
        )
        coarse_population_projection = (
            coarse_macro_population_simulation.simulate_policies()
        )

        assert_frame_equal(coarse_population_projection, self.macro_projection)

    def test_update_attributes_age_recidiviz_schema_matches_example_by_hand(
        self,
    ) -> None:
        """Validate age cross function works as expected."""
        age_admissions_data = pd.DataFrame(
            {
                "cohort_population": [0] * 5,
                "simulation_group": ["0-24", "25-29", "30-34", "35-39", "40+"],
                "compartment": ["pretrial"] * 5,
                "admission_to": ["prison"] * 5,
                "time_step": [0] * 5,
            }
        )

        age_transitions_data = pd.DataFrame(
            {
                "compartment_duration": [1000, 1000, 1000] * 5,
                "cohort_portion": [4, 2, 2] * 5,
                "simulation_group": ["0-24"] * 3
                + ["25-29"] * 3
                + ["30-34"] * 3
                + ["35-39"] * 3
                + ["40+"] * 3,
                "outflow_to": ["supervision", "prison", "supervision"] * 5,
                "compartment": ["prison", "supervision", "prison"] * 5,
                "time_step": [0] * 15,
            }
        )

        age_population_data = pd.DataFrame(
            {
                "compartment_population": [10, 0, 0, 5, 0],
                "compartment": ["prison"] * 5,
                "simulation_group": ["0-24", "25-29", "30-34", "35-39", "40+"],
                "time_step": [0] * 5,
            }
        )

        age_user_inputs = UserInputs(
            projection_time_steps=121,
            start_time_step=0,
            constant_admissions=True,
            cross_flow_function="update_attributes_age_recidiviz_schema",
        )
        age_data_inputs = SimulationInputData(
            admissions_data=age_admissions_data,
            transitions_data=age_transitions_data,
            population_data=age_population_data,
            compartments_architecture=self.simulation_architecture,
            microsim=True,
            microsim_data=age_transitions_data,
            should_initialize_compartment_populations=True,
            should_scale_populations_after_step=False,
            override_cross_flow_function=None,
        )
        population_simulation = PopulationSimulationFactory.build_population_simulation(
            age_user_inputs, [], 0, age_data_inputs
        )
        population_projection = population_simulation.simulate_policies()
        prison_populations = (
            population_projection[population_projection.compartment == "prison"]
            .groupby(["time_step", "simulation_group"])
            .sum()
            .unstack("simulation_group")
        )

        prison_populations.columns = prison_populations.columns.get_level_values(
            "simulation_group"
        )

        expected = pd.DataFrame(index=range(121))
        expected.columns.name = "simulation_group"
        expected.index.name = "time_step"
        expected["0-24"] = [10.0] * 60 + [0.0] * 61
        expected["25-29"] = [0.0] * 60 + [10.0] * 60 + [0.0]
        expected["30-34"] = [0.0] * 120 + [10.0]
        expected["35-39"] = [5.0] * 60 + [0.0] * 61
        expected["40+"] = [0.0] * 60 + [5.0] * 61

        assert_frame_equal(expected, prison_populations)
