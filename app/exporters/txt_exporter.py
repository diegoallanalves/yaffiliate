from __future__ import annotations

from app.exporters.content_exporter import (
    ExportedContent,
)


class TXTExporter:
    """
    Export generated content as a plain-text file.

    TXT = Plain Text File.

    Plain-text files contain text without advanced
    formatting such as font styles, tables or images.
    """

    @property
    def format_key(self) -> str:
        """
        Return the internal export-format identifier.
        """
        return "txt"

    @property
    def display_name(self) -> str:
        """
        Return the format name shown to users.
        """
        return "TXT"

    def export(
        self,
        *,
        title: str,
        content: str,
        filename_stem: str,
    ) -> ExportedContent:
        """
        Convert content into a UTF-8 encoded text file.

        UTF-8 = Unicode Transformation Format, 8-bit.

        UTF-8 allows the file to store international
        characters reliably.
        """
        cleaned_title = title.strip()
        cleaned_content = content.strip()

        document_parts: list[str] = []

        if cleaned_title:
            document_parts.extend(
                [
                    cleaned_title,
                    "",
                ]
            )

        document_parts.append(
            cleaned_content
        )

        document_text = "\n".join(
            document_parts
        ).strip()

        return ExportedContent(
            filename=f"{filename_stem}.txt",
            data=document_text.encode("utf-8"),
            mime_type="text/plain",
        )