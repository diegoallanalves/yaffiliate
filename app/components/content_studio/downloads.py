from __future__ import annotations

import streamlit as st

from app.services.content_export_registry import (
    ContentExportRegistry,
)


def render_export_buttons(
    *,
    title: str,
    content: str,
    filename_stem: str,
    component_key: str,
) -> None:
    """
    Render download buttons for every available export format.

    TXT = Plain Text File.

    DOCX = Microsoft Word Open XML Document.

    The export component does not generate files directly.
    It delegates file creation to ContentExportRegistry.
    """
    export_registry = ContentExportRegistry()

    available_formats = (
        export_registry.list_available_keys()
    )

    if not available_formats:
        st.warning(
            "No content export formats are currently "
            "available."
        )
        return

    st.markdown("### Download content")

    export_columns = st.columns(
        len(available_formats)
    )

    for column, format_key in zip(
        export_columns,
        available_formats,
    ):
        with column:
            _render_export_button(
                export_registry=export_registry,
                format_key=format_key,
                title=title,
                content=content,
                filename_stem=filename_stem,
                component_key=component_key,
            )


def _render_export_button(
    *,
    export_registry: ContentExportRegistry,
    format_key: str,
    title: str,
    content: str,
    filename_stem: str,
    component_key: str,
) -> None:
    """
    Generate and render one download button.

    MIME = Multipurpose Internet Mail Extensions.

    A MIME type tells the browser which type of file
    is being downloaded.
    """
    try:
        exported_content = export_registry.export(
            format_key=format_key,
            title=title,
            content=content,
            filename_stem=filename_stem,
        )

    except Exception as error:
        st.error(
            f"Unable to prepare the "
            f"{format_key.upper()} export."
        )

        with st.expander(
            f"View {format_key.upper()} export error"
        ):
            st.code(
                str(error)
            )

        return

    st.download_button(
        label=(
            f"Download as "
            f"{format_key.upper()}"
        ),
        data=exported_content.data,
        file_name=exported_content.filename,
        mime=exported_content.mime_type,
        width="stretch",
        key=(
            f"{component_key}_"
            f"download_{format_key}"
        ),
    )