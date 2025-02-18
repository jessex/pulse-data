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
"""Functions for archiving product ETL data"""
from datetime import date

from recidiviz.cloud_storage.gcsfs_factory import GcsfsFactory
from recidiviz.cloud_storage.gcsfs_path import GcsfsFilePath
from recidiviz.utils import metadata
from recidiviz.utils.string import StrictStringFormatter


def archive_etl_file(filename: str, export_output_directory_uri: str) -> None:
    """Given a storage blob name, copies that file to the corresponding ETL Archive bucket, stamped with today's date.
    Assumes that the archive bucket name is identical to the export directory with the -archive suffix.

    For example, `US_XX/data.json` => `2022-04-07/US_XX/data.json`"""

    ETL_BUCKET_PATH = StrictStringFormatter().format(
        export_output_directory_uri,
        project_id=metadata.project_id(),
    )

    source_path = GcsfsFilePath.from_absolute_path(f"{ETL_BUCKET_PATH}/{filename}")
    destination_path = GcsfsFilePath.from_absolute_path(
        f"{ETL_BUCKET_PATH}-archive/{date.today().isoformat()}/{filename}",
    )

    gcs_file_system = GcsfsFactory.build()
    gcs_file_system.copy(source_path, destination_path)
