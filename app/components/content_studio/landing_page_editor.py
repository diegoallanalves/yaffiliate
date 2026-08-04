from __future__ import annotations

from typing import Any

import streamlit as st

from app.components.content_studio.downloads import (
    render_export_buttons,
)
from app.components.content_studio.editor_helpers import (
    slugify,
)


def render_landing_page_editor(
    *,
    landing_page: Any,
    generated_product: str,
) -> None:
    """
    Render an editable landing page inside Content Studio.

    CTA = Call to Action.

    A CTA encourages the visitor to complete an action,
    such as purchasing a product or learning more.
    """
    st.divider()

    st.subheader(
        f"Landing Page editor — {generated_product}"
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric(
        "Conversion score",
        f"{landing_page.conversion_score:.1f}/100",
    )

    metric_col2.metric(
        "Estimated words",
        f"{landing_page.estimated_word_count:,}",
    )

    metric_col3.metric(
        "Writing tone",
        landing_page.tone,
    )

    st.markdown("### Page information")

    edited_page_title = st.text_input(
        "Page title",
        value=landing_page.page_title,
        key="landing_page_title",
    )

    edited_meta_description = st.text_area(
        "Meta description",
        value=landing_page.meta_description,
        height=100,
        key="landing_page_meta_description",
    )

    meta_length = len(
        edited_meta_description.strip()
    )

    st.caption(
        "Meta-description length: "
        f"{meta_length} characters"
    )

    if meta_length < 120:
        st.warning(
            "The meta description is shorter than the "
            "recommended range of 120–165 characters."
        )

    elif meta_length > 165:
        st.warning(
            "The meta description is longer than the "
            "recommended range of 120–165 characters."
        )

    st.markdown("### Hero section")

    edited_hero_headline = st.text_input(
        "Hero headline",
        value=landing_page.hero_headline,
        key="landing_page_hero_headline",
    )

    edited_hero_subheadline = st.text_area(
        "Hero subheadline",
        value=landing_page.hero_subheadline,
        height=120,
        key="landing_page_hero_subheadline",
    )

    edited_primary_cta = st.text_input(
        "Primary CTA",
        value=landing_page.primary_cta,
        key="landing_page_primary_cta",
    )

    edited_sections: list[dict[str, Any]] = []

    st.markdown("### Landing Page sections")

    for section_index, section in enumerate(
        landing_page.sections,
        start=1,
    ):
        section_label = (
            section.section_type
            .replace("_", " ")
            .strip()
            .title()
        )

        with st.expander(
            (
                f"Section {section_index}: "
                f"{section_label}"
            ),
            expanded=section_index == 1,
        ):
            edited_section_type = st.text_input(
                "Section type",
                value=section.section_type,
                key=(
                    "landing_page_section_type_"
                    f"{section_index}"
                ),
            )

            edited_heading = st.text_input(
                "Heading",
                value=section.heading,
                key=(
                    "landing_page_section_heading_"
                    f"{section_index}"
                ),
            )

            edited_content = st.text_area(
                "Content",
                value=section.content,
                height=180,
                key=(
                    "landing_page_section_content_"
                    f"{section_index}"
                ),
            )

            edited_items: list[str] = []

            if section.items:
                st.markdown("#### Section items")

                for item_index, item in enumerate(
                    section.items,
                    start=1,
                ):
                    edited_item = st.text_input(
                        f"Item {item_index}",
                        value=item,
                        key=(
                            "landing_page_section_item_"
                            f"{section_index}_"
                            f"{item_index}"
                        ),
                    )

                    if edited_item.strip():
                        edited_items.append(
                            edited_item.strip()
                        )

            edited_sections.append(
                {
                    "section_type": (
                        edited_section_type
                    ),
                    "heading": edited_heading,
                    "content": edited_content,
                    "items": edited_items,
                }
            )

    st.markdown("### Final Call to Action")

    edited_final_cta_heading = st.text_input(
        "Final CTA heading",
        value=landing_page.final_cta_heading,
        key="landing_page_final_cta_heading",
    )

    edited_final_cta_text = st.text_area(
        "Final CTA text",
        value=landing_page.final_cta_text,
        height=120,
        key="landing_page_final_cta_text",
    )

    edited_final_cta_button = st.text_input(
        "Final CTA button",
        value=landing_page.final_cta_button,
        key="landing_page_final_cta_button",
    )

    edited_landing_page_text = (
        build_editable_landing_page_text(
            page_title=edited_page_title,
            meta_description=(
                edited_meta_description
            ),
            hero_headline=edited_hero_headline,
            hero_subheadline=(
                edited_hero_subheadline
            ),
            primary_cta=edited_primary_cta,
            sections=edited_sections,
            final_cta_heading=(
                edited_final_cta_heading
            ),
            final_cta_text=(
                edited_final_cta_text
            ),
            final_cta_button=(
                edited_final_cta_button
            ),
        )
    )

    edited_word_count = len(
        edited_landing_page_text.split()
    )

    st.caption(
        "Current edited word count: "
        f"{edited_word_count:,}"
    )

    st.divider()

    filename_stem = (
        "filtrify_"
        f"{slugify(landing_page.product_name)}"
        "_landing_page"
    )

    render_export_buttons(
        title=edited_page_title,
        content=edited_landing_page_text,
        filename_stem=filename_stem,
        component_key="landing_page_editor",
    )

    save_edits = st.button(
        "Save edits in session",
        width="stretch",
        key="save_landing_page_edits",
    )

    if save_edits:
        st.session_state[
            "edited_landing_page"
        ] = {
            "page_title": edited_page_title,
            "meta_description": (
                edited_meta_description
            ),
            "hero_headline": (
                edited_hero_headline
            ),
            "hero_subheadline": (
                edited_hero_subheadline
            ),
            "primary_cta": edited_primary_cta,
            "sections": edited_sections,
            "final_cta_heading": (
                edited_final_cta_heading
            ),
            "final_cta_text": (
                edited_final_cta_text
            ),
            "final_cta_button": (
                edited_final_cta_button
            ),
            "landing_page_text": (
                edited_landing_page_text
            ),
            "word_count": edited_word_count,
        }

        st.success(
            "Landing Page edits were saved "
            "in this session."
        )

    saved_landing_page = st.session_state.get(
        "edited_landing_page"
    )

    if saved_landing_page:
        st.info(
            "A saved edited Landing Page is available "
            "in this session. Current saved word count: "
            f'{saved_landing_page["word_count"]:,}.'
        )


def build_editable_landing_page_text(
    *,
    page_title: str,
    meta_description: str,
    hero_headline: str,
    hero_subheadline: str,
    primary_cta: str,
    sections: list[dict[str, Any]],
    final_cta_heading: str,
    final_cta_text: str,
    final_cta_button: str,
) -> str:
    """
    Convert the editable Landing Page fields into plain text.

    TXT = Plain Text File.

    A TXT file contains plain text without advanced
    formatting, page design or visual styling.
    """
    parts = [
        page_title.strip(),
        "",
        (
            "Meta description: "
            f"{meta_description.strip()}"
        ),
        "",
        "Hero section",
        "",
        hero_headline.strip(),
        "",
        hero_subheadline.strip(),
        "",
        f"Primary CTA: {primary_cta.strip()}",
        "",
    ]

    for section in sections:
        section_type = str(
            section.get(
                "section_type",
                "",
            )
        ).strip()

        heading = str(
            section.get(
                "heading",
                "",
            )
        ).strip()

        content = str(
            section.get(
                "content",
                "",
            )
        ).strip()

        items = section.get(
            "items",
            [],
        )

        if (
            not section_type
            and not heading
            and not content
            and not items
        ):
            continue

        if section_type:
            readable_section_type = (
                section_type
                .replace("_", " ")
                .title()
            )

            parts.extend(
                [
                    readable_section_type,
                    "",
                ]
            )

        if heading:
            parts.extend(
                [
                    heading,
                    "",
                ]
            )

        if content:
            parts.extend(
                [
                    content,
                    "",
                ]
            )

        for item in items:
            cleaned_item = str(
                item
            ).strip()

            if cleaned_item:
                parts.append(
                    f"- {cleaned_item}"
                )

        if items:
            parts.append("")

    parts.extend(
        [
            "Final Call to Action",
            "",
            final_cta_heading.strip(),
            "",
            final_cta_text.strip(),
            "",
            (
                "CTA button: "
                f"{final_cta_button.strip()}"
            ),
        ]
    )

    return "\n".join(
        parts
    ).strip()