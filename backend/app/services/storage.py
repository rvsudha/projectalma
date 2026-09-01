"""Pluggable resume storage.

Backends:

* ``LocalStorageBackend`` — files under ``settings.storage_local_dir`` (dev, tests,
  a mounted Docker volume).
* ``S3StorageBackend`` — any S3-compatible object store (prod). Lazily imports
  ``boto3``.

The app depends only on the :class:`StorageBackend` interface and
:func:`get_storage`, so switching providers is a config change.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import aiofiles
import anyio

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Leading "magic bytes" per accepted MIME type. A spoofed Content-Type header is
# rejected before the file is stored.
_MAGIC: dict[str, tuple[bytes, ...]] = {
    "application/pdf": (b"%PDF-",),
    # DOCX (and any OOXML) is a ZIP container.
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        b"PK\x03\x04",
        b"PK\x05\x06",
    ),
    # Legacy .doc — OLE2 compound file.
    "application/msword": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
}

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def sniff_matches(content_type: str, data: bytes) -> bool:
    signatures = _MAGIC.get(content_type)
    if not signatures:
        return False
    return any(data.startswith(sig) for sig in signatures)


def sanitize_filename(name: str) -> str:
    base = Path(name or "resume").name
    cleaned = _SAFE_NAME.sub("_", base).strip("._") or "resume"
    return cleaned[:255]


@dataclass(frozen=True)
class StoredFile:
    key: str
    filename: str
    content_type: str
    size: int


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, *, data: bytes, filename: str, content_type: str) -> StoredFile: ...

    @abstractmethod
    async def load(self, key: str) -> bytes: ...

    @abstractmethod
    async def url(self, key: str) -> str | None:
        """A directly-servable URL if the backend supports one, else ``None``."""


def _key_for(filename: str) -> str:
    suffix = Path(filename).suffix.lower()[:12]
    return f"resumes/{uuid.uuid4().hex}{suffix}"


class LocalStorageBackend(StorageBackend):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save(self, *, data: bytes, filename: str, content_type: str) -> StoredFile:
        key = _key_for(filename)
        dest = self.root / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(dest, "wb") as fh:
            await fh.write(data)
        logger.info("resume stored", extra={"backend": "local", "key": key, "bytes": len(data)})
        return StoredFile(key=key, filename=filename, content_type=content_type, size=len(data))

    async def load(self, key: str) -> bytes:
        async with aiofiles.open(self.root / key, "rb") as fh:
            return await fh.read()

    async def url(self, key: str) -> str | None:
        return None


class S3StorageBackend(StorageBackend):
    def __init__(self) -> None:
        import boto3

        if not settings.s3_bucket:
            raise RuntimeError("storage_backend=s3 requires S3_BUCKET")
        self.bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    async def save(self, *, data: bytes, filename: str, content_type: str) -> StoredFile:
        key = _key_for(filename)
        await anyio.to_thread.run_sync(
            partial(
                self._client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        )
        logger.info("resume stored", extra={"backend": "s3", "key": key, "bytes": len(data)})
        return StoredFile(key=key, filename=filename, content_type=content_type, size=len(data))

    async def load(self, key: str) -> bytes:
        obj = await anyio.to_thread.run_sync(
            partial(self._client.get_object, Bucket=self.bucket, Key=key)
        )
        return await anyio.to_thread.run_sync(obj["Body"].read)

    async def url(self, key: str) -> str | None:
        return await anyio.to_thread.run_sync(
            partial(
                self._client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=settings.s3_presign_expiry_seconds,
            )
        )


_backend: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _backend
    if _backend is None:
        _backend = (
            S3StorageBackend()
            if settings.storage_backend == "s3"
            else LocalStorageBackend(settings.storage_local_dir)
        )
    return _backend


def reset_storage_cache() -> None:
    """Test hook."""
    global _backend
    _backend = None
