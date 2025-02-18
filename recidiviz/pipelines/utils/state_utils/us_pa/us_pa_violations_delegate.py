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
"""Utils for state-specific logic related to violations
in US_PA."""
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from recidiviz.common.constants.state.state_supervision_violation import (
    StateSupervisionViolationType,
)
from recidiviz.persistence.entity.state.normalized_entities import (
    NormalizedStateSupervisionViolation,
    NormalizedStateSupervisionViolationTypeEntry,
)
from recidiviz.pipelines.utils.state_utils.state_specific_violations_delegate import (
    StateSpecificViolationDelegate,
)
from recidiviz.utils.types import assert_type

_LOW_TECHNICAL_SUBTYPE_STR: str = "LOW_TECH"
_MEDIUM_TECHNICAL_SUBTYPE_STR: str = "MED_TECH"
_HIGH_TECHNICAL_SUBTYPE_STR: str = "HIGH_TECH"
_ELECTRONIC_MONITORING_SUBTYPE_STR: str = "ELEC_MONITORING"
_SUBSTANCE_ABUSE_SUBTYPE_STR: str = "SUBSTANCE_ABUSE"

_UNSUPPORTED_VIOLATION_SUBTYPE_VALUES = [
    # We don't expect to see these types in US_PA
    StateSupervisionViolationType.ESCAPED.value,
    StateSupervisionViolationType.FELONY.value,
    StateSupervisionViolationType.MISDEMEANOR.value,
    StateSupervisionViolationType.MUNICIPAL.value,
    StateSupervisionViolationType.INTERNAL_UNKNOWN.value,
    StateSupervisionViolationType.EXTERNAL_UNKNOWN.value,
    # We expect all violations of type TECHNICAL to have expected special subtypes
    StateSupervisionViolationType.TECHNICAL.value,
]

_VIOLATION_TYPE_AND_SUBTYPE_SHORTHAND_ORDERED_MAP: List[
    Tuple[StateSupervisionViolationType, str, str]
] = [
    (StateSupervisionViolationType.LAW, StateSupervisionViolationType.LAW.value, "law"),
    (StateSupervisionViolationType.TECHNICAL, _HIGH_TECHNICAL_SUBTYPE_STR, "high_tech"),
    (
        StateSupervisionViolationType.ABSCONDED,
        StateSupervisionViolationType.ABSCONDED.value,
        "absc",
    ),
    (StateSupervisionViolationType.TECHNICAL, _SUBSTANCE_ABUSE_SUBTYPE_STR, "subs"),
    (StateSupervisionViolationType.TECHNICAL, _ELECTRONIC_MONITORING_SUBTYPE_STR, "em"),
    (
        StateSupervisionViolationType.TECHNICAL,
        _MEDIUM_TECHNICAL_SUBTYPE_STR,
        "med_tech",
    ),
    (StateSupervisionViolationType.TECHNICAL, _LOW_TECHNICAL_SUBTYPE_STR, "low_tech"),
]

_VIOLATION_TYPE_SEVERITY_ORDER = [
    StateSupervisionViolationType.LAW,
    StateSupervisionViolationType.ABSCONDED,
    StateSupervisionViolationType.TECHNICAL,
]

_SPECIAL_VIOLATION_TYPE_RAW_STRING_SUBTYPE_MAP: Dict[str, str] = {
    "H03": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "H12": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "L02": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "L08": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "M03": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "M14": _SUBSTANCE_ABUSE_SUBTYPE_STR,
    "M16": _ELECTRONIC_MONITORING_SUBTYPE_STR,
}


class UsPaViolationDelegate(StateSpecificViolationDelegate):
    """US_PA implementation of the StateSpecificViolationDelegate."""

    # US_PA has state-specific violation subtypes
    violation_type_and_subtype_shorthand_ordered_map = (
        _VIOLATION_TYPE_AND_SUBTYPE_SHORTHAND_ORDERED_MAP
    )

    def get_violation_type_subtype_strings_for_violation(
        self,
        violation: NormalizedStateSupervisionViolation,
    ) -> Dict[str, List[Optional[str]]]:
        """Returns a list of strings that represent the violation subtypes present on
        the given |violation|, along with the raw text used to determine the subtype.

        For TECHNICAL violation types, determines the US_PA-specific violation subtype
        using the violation_type_raw_text. For all other violation types, the subtype is
        just the violation_type raw value string.
        """
        violation_subtypes_map: Dict[str, List[Optional[str]]] = defaultdict(list)

        for violation_type_entry in violation.supervision_violation_types:
            if (
                violation_type_entry.violation_type
                and violation_type_entry.violation_type
                != StateSupervisionViolationType.TECHNICAL
            ):
                violation_subtypes_map[
                    violation_type_entry.violation_type.value
                ].append(violation_type_entry.violation_type_raw_text)

            else:
                violation_subtypes_map[
                    _violation_subtype_from_violation_type_entry(
                        assert_type(
                            violation_type_entry,
                            NormalizedStateSupervisionViolationTypeEntry,
                        )
                    )
                ].append(violation_type_entry.violation_type_raw_text)
        return violation_subtypes_map


def _violation_subtype_from_violation_type_entry(
    violation_type_entry: NormalizedStateSupervisionViolationTypeEntry,
) -> str:
    """Returns the subtype on the |violation_type_entry|. Fails if this does not have a violation_type_raw_text value
    that we expect to see for TECHNICAL violations in US_PA."""
    violation_type_raw_text = violation_type_entry.violation_type_raw_text

    if not violation_type_raw_text:
        # This should never happen
        raise ValueError("Unexpected null violation_type_raw_text.")

    special_subtype = _SPECIAL_VIOLATION_TYPE_RAW_STRING_SUBTYPE_MAP.get(
        violation_type_raw_text
    )

    if special_subtype:
        return special_subtype
    if violation_type_raw_text.startswith("L"):
        return _LOW_TECHNICAL_SUBTYPE_STR
    if violation_type_raw_text.startswith("M"):
        return _MEDIUM_TECHNICAL_SUBTYPE_STR
    if violation_type_raw_text.startswith("H"):
        return _HIGH_TECHNICAL_SUBTYPE_STR
    raise ValueError(f"Unexpected violation_type_raw_text: {violation_type_raw_text}")
