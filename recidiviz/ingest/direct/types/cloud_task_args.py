# Recidiviz - a data platform for criminal justice reform
# Copyright (C) 2019 Recidiviz, Inc.
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
"""Defines types used for direct ingest."""
import abc
from typing import Any, Dict, Optional, Type

import attr
import cattr

from recidiviz.cloud_storage.gcsfs_path import GcsfsFilePath
from recidiviz.common import serialization
from recidiviz.ingest.direct.gcs.filename_parts import filename_parts_from_path
from recidiviz.ingest.direct.types.direct_ingest_instance import DirectIngestInstance
from recidiviz.ingest.direct.types.direct_ingest_instance_factory import (
    DirectIngestInstanceFactory,
)
from recidiviz.utils.types import ClsT


# TODO(#28239) remove once raw data import dag is fully rolled out
@attr.s(frozen=True)
class CloudTaskArgs:
    @abc.abstractmethod
    def task_id_tag(self) -> Optional[str]:
        """Tag to add to the name of an associated cloud task."""

    def to_serializable(self) -> Dict[str, Any]:
        converter = serialization.with_datetime_hooks(cattr.Converter())
        return converter.unstructure(self)

    @classmethod
    def from_serializable(cls: Type[ClsT], serializable: Dict[str, Any]) -> ClsT:
        converter = serialization.with_datetime_hooks(cattr.Converter())
        return converter.structure(serializable, cls)


@attr.s(frozen=True)
class GcsfsRawDataBQImportArgs(CloudTaskArgs):
    raw_data_file_path: GcsfsFilePath = attr.ib()

    def task_id_tag(self) -> str:
        parts = filename_parts_from_path(self.raw_data_file_path)
        return f"raw_data_import_{parts.stripped_file_name}_{parts.date_str}"

    def file_id(self) -> str:
        parts = filename_parts_from_path(self.raw_data_file_path)
        return f"{parts.file_tag}_{parts.utc_upload_datetime_str}"

    def ingest_instance(self) -> DirectIngestInstance:
        return DirectIngestInstanceFactory.for_ingest_bucket(
            self.raw_data_file_path.bucket_path
        )
