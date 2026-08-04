"""Complete ZIP campaign exports for Filtrify."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from app.services.exports.base_exporter import BaseExporter
from app.services.exports.csv_exporter import CsvExporter
from app.services.exports.docx_exporter import DocxExporter
from app.services.exports.json_exporter import JsonExporter
from app.services.exports.pdf_exporter import PdfExporter


class ZipExporter(BaseExporter):
    """Package all campaign assets into one downloadable ZIP archive."""

    def __init__(
        self,
        *,
        docx_exporter: DocxExporter | None = None,
        csv_exporter: CsvExporter | None = None,
        json_exporter: JsonExporter | None = None,
        pdf_exporter: PdfExporter | None = None,
    ) -> None:
        """Initialize reusable child exporters."""

        self._docx = docx_exporter or DocxExporter()
        self._csv = csv_exporter or CsvExporter()
        self._json = json_exporter or JsonExporter()
        self._pdf = pdf_exporter or PdfExporter()

    def campaign_to_bytes(
        self,
        campaign: Any,
        *,
        include_pdf: bool = True,
    ) -> bytes:
        """Return a complete campaign ZIP as bytes."""

        self.validate_campaign(campaign)

        campaign_stem = self.safe_file_stem(
            campaign.campaign_name
        )

        stream = BytesIO()

        with ZipFile(
            stream,
            mode="w",
            compression=ZIP_DEFLATED,
        ) as archive:
            archive.writestr(
                f"{campaign_stem}/campaign.json",
                self._json.to_bytes(campaign),
            )
            archive.writestr(
                f"{campaign_stem}/seo_article.docx",
                self._docx.seo_article_to_bytes(
                    campaign.seo_article
                ),
            )
            archive.writestr(
                f"{campaign_stem}/landing_page.docx",
                self._docx.landing_page_to_bytes(
                    campaign.landing_page
                ),
            )
            archive.writestr(
                f"{campaign_stem}/email_sequence.docx",
                self._docx.email_sequence_to_bytes(
                    campaign.email_sequence
                ),
            )
            archive.writestr(
                f"{campaign_stem}/campaign_summary.docx",
                self._docx.campaign_summary_to_bytes(
                    campaign
                ),
            )
            archive.writestr(
                f"{campaign_stem}/google_ads.csv",
                self._csv.google_ads_to_bytes(
                    campaign.google_ads
                ),
            )

            if include_pdf:
                try:
                    pdf_bytes = (
                        self._pdf.campaign_summary_to_bytes(
                            campaign
                        )
                    )
                except RuntimeError:
                    pdf_bytes = b""

                if pdf_bytes:
                    archive.writestr(
                        f"{campaign_stem}/campaign_summary.pdf",
                        pdf_bytes,
                    )

        stream.seek(0)
        return stream.read()

    def export_campaign(
        self,
        campaign: Any,
        *,
        output_directory: str | Path = "outputs/campaigns",
        file_name: str | None = None,
        include_pdf: bool = True,
    ) -> Path:
        """Write a complete campaign ZIP to disk."""

        resolved_name = file_name or self.build_file_name(
            stem=campaign.campaign_name,
            extension="zip",
        )

        if not resolved_name.lower().endswith(".zip"):
            resolved_name = self.build_file_name(
                stem=resolved_name,
                extension="zip",
            )

        return self.write_bytes(
            data=self.campaign_to_bytes(
                campaign,
                include_pdf=include_pdf,
            ),
            output_directory=output_directory,
            file_name=resolved_name,
        )
