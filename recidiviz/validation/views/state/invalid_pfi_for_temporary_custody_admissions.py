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
"""A view revealing when normalized incarceration periods have a
specialized_purpose_for_incarceration other than TEMPORARY_CUSTODY or PAROLE_BOARD_HOLD
for admissions with an admission_reason of TEMPORARY_CUSTODY.

Existence of any rows indicates a bug in IP normalization logic.
"""
from recidiviz.big_query.big_query_view import SimpleBigQueryViewBuilder
from recidiviz.common.constants.state.state_incarceration_period import (
    StateIncarcerationPeriodAdmissionReason,
    StateSpecializedPurposeForIncarceration,
)
from recidiviz.ingest.views.dataset_config import NORMALIZED_STATE_DATASET
from recidiviz.persistence.entity.state.normalized_entities import (
    NormalizedStateIncarcerationPeriod,
)
from recidiviz.utils.environment import GCP_PROJECT_STAGING
from recidiviz.utils.metadata import local_project_id_override
from recidiviz.validation.views import dataset_config
from recidiviz.validation.views.utils.entities_validation_utils import (
    validation_query_for_normalized_entity,
)

INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_VIEW_NAME = (
    "invalid_pfi_for_temporary_custody_admissions"
)

INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_DESCRIPTION = """Normalized
incarceration periods with invalid pfi values for TEMPORARY_CUSTODY admissions."""

INVALID_ROWS_FILTER_CLAUSE = f"""WHERE admission_reason =
'{StateIncarcerationPeriodAdmissionReason.TEMPORARY_CUSTODY.value}'
-- Only PAROLE_BOARD_HOLD and TEMPORARY_CUSTODY periods should have an
-- admission_reason of TEMPORARY_CUSTODY 
AND specialized_purpose_for_incarceration NOT IN 
    ('{StateSpecializedPurposeForIncarceration.PAROLE_BOARD_HOLD.value}', 
    '{StateSpecializedPurposeForIncarceration.TEMPORARY_CUSTODY.value}')"""

INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_VIEW_BUILDER = SimpleBigQueryViewBuilder(
    dataset_id=dataset_config.VIEWS_DATASET,
    view_id=INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_VIEW_NAME,
    view_query_template=validation_query_for_normalized_entity(
        normalized_entity_class=NormalizedStateIncarcerationPeriod,
        additional_columns_to_select=[
            "person_id",
            "admission_reason",
            "specialized_purpose_for_incarceration",
            "admission_date",
        ],
        invalid_rows_filter_clause=INVALID_ROWS_FILTER_CLAUSE,
        validation_description=INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_DESCRIPTION,
    ),
    description=INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_DESCRIPTION,
    normalized_state_dataset=NORMALIZED_STATE_DATASET,
    should_materialize=True,
)

if __name__ == "__main__":
    with local_project_id_override(GCP_PROJECT_STAGING):
        INVALID_PFI_FOR_TEMPORARY_CUSTODY_ADMISSIONS_VIEW_BUILDER.build_and_print()
