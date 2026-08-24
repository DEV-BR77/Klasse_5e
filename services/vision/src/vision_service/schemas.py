from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Identified(ApiModel):
    @field_validator("*", mode="before")
    @classmethod
    def validate_ids(cls, value, info):
        if info.field_name and info.field_name.endswith("_id") and value is not None:
            if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
                raise ValueError("identifier must be opaque and URL-safe")
        return value


class CollectionCreate(Identified):
    collection_id: str
    pipeline_id: str = "yunet-sface-2023mar-2021dec"


class CollectionRead(Identified):
    collection_id: str
    pipeline_id: str
    model_version: str
    status: str


class SubjectCreate(Identified):
    subject_id: str


class SubjectRead(Identified):
    collection_id: str
    subject_id: str
    status: str


class ImageRead(Identified):
    collection_id: str
    image_id: str
    media_reference: str | None
    sha256: str
    width: int
    height: int
    status: str


class JobRead(Identified):
    collection_id: str
    job_id: str
    image_id: str | None
    type: str
    status: str
    progress: int
    pipeline_id: str
    model_version: str
    error_code: str | None


class FaceRead(Identified):
    collection_id: str
    face_id: str
    image_id: str
    bbox: dict
    landmarks: list
    detection_score: float
    quality: dict
    pipeline_id: str
    model_version: str
    status: str


class MatchRead(Identified):
    collection_id: str
    match_id: str
    face_id: str
    subject_id: str
    score: float
    rank: int
    status: str
    actor_id: str | None


class DecisionRequest(Identified):
    actor_id: str
    add_as_reference: bool = False


class RejectRequest(Identified):
    actor_id: str


class DismissRequest(Identified):
    actor_id: str


class ReferenceCreate(Identified):
    reference_id: str
    face_id: str


class ReferenceRead(Identified):
    collection_id: str
    reference_id: str
    subject_id: str
    face_id: str
    pipeline_id: str
    model_version: str
    confirmed: bool
    revoked_at: datetime | None


class DeleteResult(ApiModel):
    status: str = "deleted"


class HealthRead(ApiModel):
    status: str
    database: str
    pipeline: str


class ErrorRead(ApiModel):
    detail: str = Field(max_length=128)
