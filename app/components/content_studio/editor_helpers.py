from __future__ import annotations

import streamlit as st


def slugify(
    value: str,
    *,
    fallback: str = "content",
) -> str:
    """
    Convert text into a safe filename value.

    Example:

    "Excel Course" becomes "excel_course".
    """
    cleaned_value = (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    allowed_characters = set(
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789_-"
    )

    slug = "".join(
        character
        for character in cleaned_value
        if character in allowed_characters
    )

    return slug or fallback


def clear_editor_state() -> None:
    """
    Remove editor values from Streamlit session state.

    Session state:
    Temporary information Streamlit keeps while the user
    continues using the application.
    """
    fixed_editor_keys = [
        "seo_article_title",
        "seo_article_meta_description",
        "seo_article_introduction",
        "seo_article_conclusion",
        "seo_article_call_to_action",
        "save_seo_article_edits",
        "edited_seo_article",
        "landing_page_title",
        "landing_page_meta_description",
        "landing_page_hero_headline",
        "landing_page_hero_subheadline",
        "landing_page_primary_cta",
        "landing_page_final_cta_heading",
        "landing_page_final_cta_text",
        "landing_page_final_cta_button",
        "save_landing_page_edits",
        "edited_landing_page",
    ]

    dynamic_prefixes = [
        "seo_section_heading_",
        "seo_section_content_",
        "landing_page_section_type_",
        "landing_page_section_heading_",
        "landing_page_section_content_",
        "landing_page_section_item_",
    ]

    dynamic_editor_keys = [
        key
        for key in list(
            st.session_state.keys()
        )
        if any(
            key.startswith(prefix)
            for prefix in dynamic_prefixes
        )
    ]

    editor_keys = (
        fixed_editor_keys
        + dynamic_editor_keys
    )

    for key in editor_keys:
        st.session_state.pop(
            key,
            None,
        )