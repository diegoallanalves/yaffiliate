from __future__ import annotations

from app.exporters.content_exporter import (
    ContentExporter,
    ExportedContent,
)
from app.exporters.docx_exporter import (
    DOCXExporter,
)
from app.exporters.pdf_exporter import (
    PDFExporter,
)
from app.exporters.txt_exporter import (
    TXTExporter,
)


class ContentExportRegistry:
    """
    Central registry for Filtrify content exporters.

    Registry:
    A central place that stores and retrieves available
    exporters.

    This follows the same architecture already used by:

    - ContentGeneratorRegistry
    - ContentEditorRegistry

    New export formats can be added without changing
    the content editors.
    """

    def __init__(self) -> None:
        self._exporters: dict[
            str,
            ContentExporter,
        ] = {}

        self.register(
            TXTExporter()
        )

        self.register(
            DOCXExporter()
        )

        self.register(
            PDFExporter()
        )

    def register(
        self,
        exporter: ContentExporter,
    ) -> None:
        """
        Register or replace a content exporter.
        """
        format_key = (
            exporter.format_key
            .strip()
            .casefold()
        )

        if not format_key:
            raise ValueError(
                "Export format key cannot be empty."
            )

        export_method = getattr(
            exporter,
            "export",
            None,
        )

        if not callable(
            export_method
        ):
            raise TypeError(
                "Exporter must provide an export method."
            )

        self._exporters[
            format_key
        ] = exporter

    def unregister(
        self,
        format_key: str,
    ) -> bool:
        """
        Remove an exporter from the registry.

        Return True when an exporter was removed.

        Return False when the requested export format
        was not registered.
        """
        cleaned_format_key = (
            format_key
            .strip()
            .casefold()
        )

        if (
            cleaned_format_key
            not in self._exporters
        ):
            return False

        del self._exporters[
            cleaned_format_key
        ]

        return True

    def get(
        self,
        format_key: str,
    ) -> ContentExporter | None:
        """
        Return an exporter using its format key.
        """
        cleaned_format_key = (
            format_key
            .strip()
            .casefold()
        )

        return self._exporters.get(
            cleaned_format_key
        )

    def is_available(
        self,
        format_key: str,
    ) -> bool:
        """
        Check whether an export format is registered.
        """
        return self.get(
            format_key
        ) is not None

    def list_available_keys(
        self,
    ) -> list[str]:
        """
        Return all registered export-format keys.
        """
        return sorted(
            self._exporters.keys()
        )

    def list_exporters(
        self,
    ) -> list[ContentExporter]:
        """
        Return all registered exporters.
        """
        return [
            self._exporters[key]
            for key in self.list_available_keys()
        ]

    def export(
        self,
        *,
        format_key: str,
        title: str,
        content: str,
        filename_stem: str,
    ) -> ExportedContent:
        """
        Export content using the selected file format.
        """
        exporter = self.get(
            format_key
        )

        if exporter is None:
            raise ValueError(
                (
                    "The requested export format "
                    "is not available: "
                    f"{format_key}"
                )
            )

        cleaned_filename_stem = (
            filename_stem.strip()
        )

        if not cleaned_filename_stem:
            raise ValueError(
                "Filename stem cannot be empty."
            )

        return exporter.export(
            title=title,
            content=content,
            filename_stem=(
                cleaned_filename_stem
            ),
        )