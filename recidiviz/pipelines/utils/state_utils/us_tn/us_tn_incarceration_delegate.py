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
"""Contains US_TN implementation of the StateSpecificIncarcerationDelegate."""
from recidiviz.common.constants.state.state_shared_enums import StateCustodialAuthority
from recidiviz.persistence.entity.state.normalized_entities import (
    NormalizedStateIncarcerationPeriod,
)
from recidiviz.pipelines.utils.state_utils.state_specific_incarceration_delegate import (
    StateSpecificIncarcerationDelegate,
)


class UsTnIncarcerationDelegate(StateSpecificIncarcerationDelegate):
    """US_TN implementation of the StateSpecificIncarcerationDelegate."""

    def is_period_included_in_state_population(
        self,
        incarceration_period: NormalizedStateIncarcerationPeriod,
    ) -> bool:
        """In US_TN, only periods of incarceration that are under the custodial
        authority of the state prison or the courts are included in the state population.

        """
        return incarceration_period.custodial_authority in (
            StateCustodialAuthority.STATE_PRISON,
            StateCustodialAuthority.COUNTY,
        )
