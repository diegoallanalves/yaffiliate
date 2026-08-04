from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ExportedContent:
    """
    Represents one generated downloadable file.

    filename:
    The filename presented to the user.

    data:
    The file content stored as bytes.

    MIME = Multipurpose Internet Mail Extensions.

    A MIME type tells the browser what type of file
    is being downloaded.
    """

    filename: str
    data: bytes
    mime_type: str


class ContentExporter(Protocol):
    """
    Defines the common interface used by content exporters.

    Protocol:
    A Python typing structure that describes which methods
    another object must provide.

    Every Filtrify exporter must provide an export method.
    """

    @property
    def format_key(self) -> str:
        """
        Return the unique export-format identifier.
        """
        ...

    @property
    def display_name(self) -> str:
        """
        Return the human-readable format name.
        """
        ...

    def export(
        self,
        *,
        title: str,
        content: str,
        filename_stem: str,
    ) -> ExportedContent:
        """
        Convert content into a downloadable file.
        """
        ...