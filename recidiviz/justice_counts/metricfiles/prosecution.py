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
"""Metricfile objects used for prosecution metrics."""

from recidiviz.justice_counts.dimensions.common import (
    CaseSeverityType,
    DispositionType,
    ExpenseType,
)
from recidiviz.justice_counts.dimensions.person import BiologicalSex, RaceAndEthnicity
from recidiviz.justice_counts.dimensions.prosecution import (
    CaseDeclinedSeverityType,
    DivertedCaseSeverityType,
    FundingType,
    ProsecutedCaseSeverityType,
    ReferredCaseSeverityType,
    StaffType,
)
from recidiviz.justice_counts.metricfile import MetricFile
from recidiviz.justice_counts.metrics import prosecution

PROSECUTION_METRIC_FILES = [
    MetricFile(
        canonical_filename="funding",
        definition=prosecution.funding,
    ),
    MetricFile(
        canonical_filename="funding_by_type",
        definition=prosecution.funding,
        disaggregation=FundingType,
        disaggregation_column_name="funding_type",
    ),
    MetricFile(
        canonical_filename="expenses",
        definition=prosecution.expenses,
    ),
    MetricFile(
        canonical_filename="expenses_by_type",
        definition=prosecution.expenses,
        disaggregation=ExpenseType,
        disaggregation_column_name="expense_type",
    ),
    MetricFile(
        canonical_filename="total_staff",
        definition=prosecution.staff,
    ),
    MetricFile(
        canonical_filename="total_staff_by_type",
        definition=prosecution.staff,
        disaggregation=StaffType,
        disaggregation_column_name="staff_type",
    ),
    MetricFile(
        canonical_filename="open_cases",
        definition=prosecution.caseload_numerator,
    ),
    MetricFile(
        canonical_filename="open_cases_by_type",
        definition=prosecution.caseload_numerator,
        disaggregation=CaseSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="staff_with_caseload",
        definition=prosecution.caseload_denominator,
    ),
    MetricFile(
        canonical_filename="staff_with_caseload_by_type",
        definition=prosecution.caseload_denominator,
        disaggregation=CaseSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="cases_disposed",
        definition=prosecution.cases_disposed,
    ),
    MetricFile(
        canonical_filename="cases_disposed_by_type",
        definition=prosecution.cases_disposed,
        disaggregation=DispositionType,
        disaggregation_column_name="disposition_type",
    ),
    MetricFile(
        canonical_filename="cases_referred",
        definition=prosecution.cases_referred,
    ),
    MetricFile(
        canonical_filename="cases_referred_by_severity",
        definition=prosecution.cases_referred,
        disaggregation=ReferredCaseSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="cases_prosecuted",
        definition=prosecution.cases_prosecuted,
    ),
    MetricFile(
        canonical_filename="cases_prosecuted_by_type",
        definition=prosecution.cases_prosecuted,
        disaggregation=ProsecutedCaseSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="cases_prosecuted_by_sex",
        definition=prosecution.cases_prosecuted,
        disaggregation=BiologicalSex,
        disaggregation_column_name="biological_sex",
    ),
    MetricFile(
        canonical_filename="cases_prosecuted_by_race",
        definition=prosecution.cases_prosecuted,
        disaggregation=RaceAndEthnicity,
        disaggregation_column_name="race/ethnicity",
    ),
    MetricFile(
        canonical_filename="cases_diverted",
        definition=prosecution.cases_diverted_or_deferred,
    ),
    MetricFile(
        canonical_filename="cases_diverted_by_type",
        definition=prosecution.cases_diverted_or_deferred,
        disaggregation=DivertedCaseSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="cases_diverted_by_race",
        definition=prosecution.cases_diverted_or_deferred,
        disaggregation=RaceAndEthnicity,
        disaggregation_column_name="race/ethnicity",
    ),
    MetricFile(
        canonical_filename="cases_diverted_by_sex",
        definition=prosecution.cases_diverted_or_deferred,
        disaggregation=BiologicalSex,
        disaggregation_column_name="biological_sex",
    ),
    MetricFile(
        canonical_filename="cases_declined",
        definition=prosecution.cases_declined,
    ),
    MetricFile(
        canonical_filename="cases_declined_by_severity",
        definition=prosecution.cases_declined,
        disaggregation=CaseDeclinedSeverityType,
        disaggregation_column_name="case_severity",
    ),
    MetricFile(
        canonical_filename="cases_declined_by_sex",
        definition=prosecution.cases_declined,
        disaggregation=BiologicalSex,
        disaggregation_column_name="biological_sex",
    ),
    MetricFile(
        canonical_filename="cases_declined_by_race",
        definition=prosecution.cases_declined,
        disaggregation=RaceAndEthnicity,
        disaggregation_column_name="race/ethnicity",
    ),
    MetricFile(
        canonical_filename="violations_filed",
        definition=prosecution.violations,
    ),
]
