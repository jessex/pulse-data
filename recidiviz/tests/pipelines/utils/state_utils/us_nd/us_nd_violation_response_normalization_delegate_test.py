# Recidiviz - a data platform for criminal justice reform
# Copyright (C) 2021 Recidiviz, Inc.
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
"""Tests the US_ND-specific aspects of when the state-specific delegate is used in
the ViolationResponseNormalizationManager."""
import datetime
import unittest
from typing import List

import attr
import mock

from recidiviz.common.constants.state.state_supervision_violation import (
    StateSupervisionViolationType,
)
from recidiviz.common.constants.state.state_supervision_violation_response import (
    StateSupervisionViolationResponseType,
)
from recidiviz.persistence.entity.state.entities import (
    StateSupervisionViolation,
    StateSupervisionViolationResponse,
    StateSupervisionViolationTypeEntry,
)
from recidiviz.pipelines.ingest.state.normalization.normalization_managers.supervision_violation_responses_normalization_manager import (
    ViolationResponseNormalizationManager,
)
from recidiviz.pipelines.utils.execution_utils import (
    build_staff_external_id_to_staff_id_map,
)
from recidiviz.pipelines.utils.state_utils.us_nd.us_nd_violation_response_normalization_delegate import (
    UsNdViolationResponseNormalizationDelegate,
)
from recidiviz.tests.persistence.entity.state.entities_test_utils import (
    hydrate_bidirectional_relationships_on_expected_response,
)
from recidiviz.tests.pipelines.ingest.state.normalization.normalization_managers.assessment_normalization_manager_test import (
    STATE_PERSON_TO_STATE_STAFF_LIST,
)


class TestPrepareViolationResponsesForCalculations(unittest.TestCase):
    """Tests the US_ND-specific aspects of the
    normalized_violation_responses_for_calculations function on the
    ViolationResponseNormalizationManager when a
    UsNdViolationResponseNormalizationDelegate is provided."""

    def setUp(self) -> None:
        self.state_code = "US_ND"
        self.delegate = UsNdViolationResponseNormalizationDelegate()
        self.person_id = 3800000000000000123

        self.unique_id_patcher = mock.patch(
            "recidiviz.persistence.entity."
            "normalized_entities_utils.generate_primary_key"
        )
        self.mock_unique_id = self.unique_id_patcher.start()
        self.mock_unique_id.return_value = 3800000000012312345

    def tearDown(self) -> None:
        self.unique_id_patcher.stop()

    def _normalized_violation_responses_for_calculations(
        self,
        violation_responses: List[StateSupervisionViolationResponse],
    ) -> List[StateSupervisionViolationResponse]:
        entity_normalization_manager = ViolationResponseNormalizationManager(
            person_id=self.person_id,
            violation_responses=violation_responses,
            delegate=self.delegate,
            staff_external_id_to_staff_id=build_staff_external_id_to_staff_id_map(
                STATE_PERSON_TO_STATE_STAFF_LIST
            ),
        )

        (
            processed_vrs,
            _,
        ) = (
            entity_normalization_manager.normalized_violation_responses_for_calculations()
        )

        return processed_vrs

    def test_prepare_violation_responses_for_calculations_us_nd(self) -> None:
        supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=123,
            external_id="sv1",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.FELONY,
                ),
            ],
        )

        ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=123,
            external_id="svr1",
            supervision_violation=supervision_violation,
            response_date=datetime.date(2008, 12, 25),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        other_supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=456,
            external_id="sv2",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.FELONY,
                ),
            ],
        )

        duplicate_ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=456,
            external_id="svr2",
            supervision_violation=other_supervision_violation,
            response_date=datetime.date(2008, 12, 25),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        expected_response = attr.evolve(
            ssvr,
            supervision_violation=StateSupervisionViolation.new_with_defaults(
                supervision_violation_id=3800000000012312345,
                external_id="sv1",
                state_code=self.state_code,
                supervision_violation_types=[
                    StateSupervisionViolationTypeEntry.new_with_defaults(
                        supervision_violation_type_entry_id=3800000000012312345,
                        state_code=self.state_code,
                        violation_type=StateSupervisionViolationType.FELONY,
                    ),
                ],
            ),
        )

        # Hydrate bidirectional relationships
        hydrate_bidirectional_relationships_on_expected_response(expected_response)

        # Act
        updated_responses = self._normalized_violation_responses_for_calculations(
            violation_responses=[ssvr, duplicate_ssvr]
        )

        # Assert
        self.assertEqual([expected_response], updated_responses)

    def test_prepare_violation_responses_for_calculations_multiple_types_us_nd(
        self,
    ) -> None:
        supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=123,
            external_id="sv1",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.ABSCONDED,
                ),
            ],
        )

        ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=123,
            external_id="svr1",
            supervision_violation=supervision_violation,
            response_date=datetime.date(2008, 12, 25),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        duplicate_supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=123,
            external_id="sv1",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.FELONY,
                ),
            ],
        )

        duplicate_ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=123,
            external_id="svr1",
            supervision_violation=duplicate_supervision_violation,
            response_date=datetime.date(2008, 12, 25),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        expected_response = attr.evolve(
            ssvr,
            supervision_violation=attr.evolve(
                supervision_violation,
                supervision_violation_id=3800000000012312345,
                supervision_violation_types=[
                    StateSupervisionViolationTypeEntry.new_with_defaults(
                        state_code=self.state_code,
                        supervision_violation_type_entry_id=3800000000012312345,
                        violation_type=StateSupervisionViolationType.ABSCONDED,
                    ),
                    StateSupervisionViolationTypeEntry.new_with_defaults(
                        state_code=self.state_code,
                        supervision_violation_type_entry_id=3800000000012312345,
                        violation_type=StateSupervisionViolationType.FELONY,
                    ),
                ],
            ),
        )

        # Hydrate bidirectional relationships
        hydrate_bidirectional_relationships_on_expected_response(expected_response)

        # Act
        updated_responses = self._normalized_violation_responses_for_calculations(
            violation_responses=[ssvr, duplicate_ssvr]
        )

        # Assert
        self.assertEqual([expected_response], updated_responses)

    def test_prepare_violation_responses_for_calculations_different_days_us_nd(
        self,
    ) -> None:
        supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=123,
            external_id="sv1",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.ABSCONDED,
                ),
            ],
        )

        ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=123,
            external_id="svr1",
            supervision_violation=supervision_violation,
            response_date=datetime.date(2008, 12, 1),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        other_supervision_violation = StateSupervisionViolation.new_with_defaults(
            supervision_violation_id=456,
            external_id="sv2",
            state_code=self.state_code,
            supervision_violation_types=[
                StateSupervisionViolationTypeEntry.new_with_defaults(
                    state_code=self.state_code,
                    violation_type=StateSupervisionViolationType.FELONY,
                ),
            ],
        )

        other_ssvr = StateSupervisionViolationResponse.new_with_defaults(
            state_code=self.state_code,
            supervision_violation_response_id=456,
            external_id="svr2",
            supervision_violation=other_supervision_violation,
            response_date=datetime.date(2008, 12, 25),
            response_type=StateSupervisionViolationResponseType.PERMANENT_DECISION,
        )

        ssvr_copies = [
            attr.evolve(
                ssvr,
                supervision_violation=attr.evolve(
                    supervision_violation,
                    supervision_violation_id=3800000000012312345,
                    supervision_violation_types=[
                        StateSupervisionViolationTypeEntry.new_with_defaults(
                            state_code=self.state_code,
                            supervision_violation_type_entry_id=3800000000012312345,
                            violation_type=StateSupervisionViolationType.ABSCONDED,
                        ),
                    ],
                ),
            ),
            attr.evolve(
                other_ssvr,
                supervision_violation=attr.evolve(
                    other_supervision_violation,
                    supervision_violation_id=3800000000012312345,
                    supervision_violation_types=[
                        StateSupervisionViolationTypeEntry.new_with_defaults(
                            state_code=self.state_code,
                            supervision_violation_type_entry_id=3800000000012312345,
                            violation_type=StateSupervisionViolationType.FELONY,
                        ),
                    ],
                ),
            ),
        ]

        # Hydrate bidirectional relationships
        for expected_response in ssvr_copies:
            hydrate_bidirectional_relationships_on_expected_response(expected_response)

        # Act
        updated_responses = self._normalized_violation_responses_for_calculations(
            violation_responses=[ssvr, other_ssvr]
        )

        # Assert
        self.assertEqual(ssvr_copies, updated_responses)
