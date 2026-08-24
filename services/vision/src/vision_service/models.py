from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Collection(Base):
    __tablename__ = "collections"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pipeline_id: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Subject(Base):
    __tablename__ = "subjects"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        ForeignKeyConstraint(["collection_id"], ["collections.collection_id"], ondelete="CASCADE"),
    )


class Image(Base):
    __tablename__ = "images"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    image_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    media_reference: Mapped[str | None] = mapped_column(String(256))
    storage_name: Mapped[str] = mapped_column(String(256))
    sha256: Mapped[str] = mapped_column(String(64))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="registered")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        ForeignKeyConstraint(["collection_id"], ["collections.collection_id"], ondelete="CASCADE"),
    )


class Face(Base):
    __tablename__ = "faces"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    face_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    image_id: Mapped[str] = mapped_column(String(128))
    bbox: Mapped[dict] = mapped_column(JSON)
    landmarks: Mapped[list] = mapped_column(JSON)
    detection_score: Mapped[float] = mapped_column(Float)
    quality: Mapped[dict] = mapped_column(JSON, default=dict)
    pipeline_id: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(128))
    crop_name: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(24), default="detected")
    actor_id: Mapped[str | None] = mapped_column(String(128))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (
        ForeignKeyConstraint(
            ["collection_id", "image_id"],
            ["images.collection_id", "images.image_id"],
            ondelete="CASCADE",
        ),
    )


class Reference(Base):
    __tablename__ = "references"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    reference_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(128))
    face_id: Mapped[str] = mapped_column(String(128))
    pipeline_id: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(128))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        ForeignKeyConstraint(
            ["collection_id", "subject_id"],
            ["subjects.collection_id", "subjects.subject_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["collection_id", "face_id"],
            ["faces.collection_id", "faces.face_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("collection_id", "subject_id", "face_id"),
    )


class Embedding(Base):
    __tablename__ = "embeddings"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    embedding_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(16))
    owner_id: Mapped[str] = mapped_column(String(128))
    pipeline_id: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(128))
    dimension: Mapped[int] = mapped_column(Integer)
    vector: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (
        UniqueConstraint("collection_id", "owner_type", "owner_id"),
        CheckConstraint("owner_type IN ('face','reference')", name="embedding_owner_type"),
    )


class Match(Base):
    __tablename__ = "matches"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    match_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    face_id: Mapped[str] = mapped_column(String(128))
    subject_id: Mapped[str] = mapped_column(String(128))
    score: Mapped[float] = mapped_column(Float)
    rank: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="proposed")
    actor_id: Mapped[str | None] = mapped_column(String(128))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (
        ForeignKeyConstraint(
            ["collection_id", "face_id"],
            ["faces.collection_id", "faces.face_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["collection_id", "subject_id"],
            ["subjects.collection_id", "subjects.subject_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("collection_id", "face_id", "subject_id"),
        CheckConstraint("status IN ('proposed','confirmed','rejected')", name="match_status"),
    )


class Job(Base):
    __tablename__ = "jobs"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    image_id: Mapped[str | None] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(24), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    pipeline_id: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(128))
    error_code: Mapped[str | None] = mapped_column(String(64))
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        ForeignKeyConstraint(["collection_id"], ["collections.collection_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(
            ["collection_id", "image_id"],
            ["images.collection_id", "images.image_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "status IN ('queued','running','completed','failed','cancelled')", name="job_status"
        ),
    )


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    collection_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    operation: Mapped[str] = mapped_column(String(64), primary_key=True)
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    resource_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (
        ForeignKeyConstraint(["collection_id"], ["collections.collection_id"], ondelete="CASCADE"),
    )
