"""Editable Search Engine Optimization article interface for Filtrify.

SEO means Search Engine Optimization. It is the process of improving content
so that it can appear more effectively in unpaid search-engine results.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.components.content_studio.ai_workspace import (
    render_ai_workspace,
)
from app.components.content_studio.downloads import (
    render_export_buttons,
)
from app.components.content_studio.editor_helpers import (
    slugify,
)


AI_CONTENT_KEY = "seo_article_ai_content"
AI_EDITOR_KEY = "seo_article_ai_content_editor"


def render_seo_article_editor(
    *,
    article: Any,
    generated_product: str,
) -> None:
    """Render an editable Search Engine Optimization article.

    The editor allows the user to:

    - Edit every structured article field.
    - Improve the complete article through the Artificial Intelligence
      Workspace.
    - Review suggestions before accepting them.
    - Export the current article.
    - Save edits in the Streamlit session.

    AI means Artificial Intelligence.
    """

    st.divider()

    st.subheader(
        f"Article editor — {generated_product}"
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric(
        "SEO score",
        f"{article.seo_score:.1f}/100",
    )

    metric_col2.metric(
        "Estimated words",
        f"{article.estimated_word_count:,}",
    )

    metric_col3.metric(
        "Target keyword",
        article.target_keyword,
    )

    edited_title = st.text_input(
        "Title",
        value=article.title,
        key="seo_article_title",
    )

    edited_meta_description = st.text_area(
        "Meta description",
        value=article.meta_description,
        height=100,
        key="seo_article_meta_description",
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

    edited_introduction = st.text_area(
        "Introduction",
        value=article.introduction,
        height=180,
        key="seo_article_introduction",
    )

    edited_sections: list[dict[str, str]] = []

    st.markdown("### Article sections")

    for index, section in enumerate(
        article.sections,
        start=1,
    ):
        with st.expander(
            f"Section {index}: {section.heading}",
            expanded=index == 1,
        ):
            edited_heading = st.text_input(
                "Heading",
                value=section.heading,
                key=(
                    "seo_section_heading_"
                    f"{index}"
                ),
            )

            edited_content = st.text_area(
                "Content",
                value=section.content,
                height=180,
                key=(
                    "seo_section_content_"
                    f"{index}"
                ),
            )

            edited_sections.append(
                {
                    "heading": edited_heading,
                    "content": edited_content,
                }
            )

    edited_conclusion = st.text_area(
        "Conclusion",
        value=article.conclusion,
        height=160,
        key="seo_article_conclusion",
    )

    edited_call_to_action = st.text_area(
        "Call to action",
        value=article.call_to_action,
        height=120,
        key="seo_article_call_to_action",
    )

    structured_article_text = build_editable_article_text(
        title=edited_title,
        meta_description=edited_meta_description,
        introduction=edited_introduction,
        sections=edited_sections,
        conclusion=edited_conclusion,
        call_to_action=edited_call_to_action,
    )

    structured_word_count = len(
        structured_article_text.split()
    )

    st.caption(
        "Current edited word count: "
        f"{structured_word_count:,}"
    )

    _render_ai_workspace_section(
        article_text=structured_article_text,
        article=article,
        generated_product=generated_product,
    )

    final_article_text = _render_ai_article_override(
        default_content=structured_article_text,
    )

    final_word_count = len(
        final_article_text.split()
    )

    if final_article_text != structured_article_text:
        st.caption(
            "Current AI-assisted article word count: "
            f"{final_word_count:,}"
        )

    st.divider()

    filename_stem = (
        "filtrify_"
        f"{slugify(article.target_keyword)}"
        "_article"
    )

    render_export_buttons(
        title=edited_title,
        content=final_article_text,
        filename_stem=filename_stem,
        component_key="seo_article_editor",
    )

    save_edits = st.button(
        "Save edits in session",
        width="stretch",
        key="save_seo_article_edits",
    )

    if save_edits:
        st.session_state[
            "edited_seo_article"
        ] = {
            "title": edited_title,
            "meta_description": edited_meta_description,
            "introduction": edited_introduction,
            "sections": edited_sections,
            "conclusion": edited_conclusion,
            "call_to_action": edited_call_to_action,
            "article_text": final_article_text,
            "word_count": final_word_count,
            "ai_assisted": (
                final_article_text
                != structured_article_text
            ),
        }

        st.success(
            "Article edits were saved "
            "in this session."
        )

    saved_article = st.session_state.get(
        "edited_seo_article"
    )

    if saved_article:
        saved_word_count = saved_article.get(
            "word_count",
            0,
        )

        st.info(
            "A saved edited version is available "
            "in this session. Current saved word "
            "count: "
            f"{saved_word_count:,}."
        )


def _render_ai_workspace_section(
    *,
    article_text: str,
    article: Any,
    generated_product: str,
) -> None:
    """Render the Artificial Intelligence Workspace for the article.

    The complete article is sent to the selected action. The result is kept
    separate until the user explicitly accepts the suggestion.
    """

    st.divider()

    target_keyword = str(
        getattr(
            article,
            "target_keyword",
            "",
        )
    ).strip()

    keywords = (
        (target_keyword,)
        if target_keyword
        else ()
    )

    workspace_response = render_ai_workspace(
        content=article_text,
        content_type="seo_article",
        target_audience=generated_product,
        keywords=keywords,
        key_prefix="seo_article_ai_workspace",
    )

    accepted_content = (
        workspace_response.accepted_content
    )

    if accepted_content is None:
        return

    cleaned_content = str(
        accepted_content
    ).strip()

    if not cleaned_content:
        return

    st.session_state[
        AI_CONTENT_KEY
    ] = cleaned_content

    st.session_state[
        AI_EDITOR_KEY
    ] = cleaned_content

    st.success(
        "The Artificial Intelligence suggestion "
        "has been applied to the article."
    )

    st.rerun()


def _render_ai_article_override(
    *,
    default_content: str,
) -> str:
    """Render an accepted Artificial Intelligence version when available.

    The structured editor remains unchanged. An accepted suggestion is stored
    as a complete article version and becomes the content used for saving and
    exporting.
    """

    ai_content = st.session_state.get(
        AI_CONTENT_KEY
    )

    if not isinstance(ai_content, str):
        return default_content

    cleaned_ai_content = ai_content.strip()

    if not cleaned_ai_content:
        return default_content

    if AI_EDITOR_KEY not in st.session_state:
        st.session_state[
            AI_EDITOR_KEY
        ] = cleaned_ai_content

    st.divider()
    st.markdown("### AI-assisted article")

    st.caption(
        "This is the accepted Artificial Intelligence version. "
        "It will be used for saving and exporting."
    )

    edited_ai_content = st.text_area(
        "AI-assisted article content",
        height=500,
        key=AI_EDITOR_KEY,
        label_visibility="collapsed",
    )

    reset_ai_version = st.button(
        "Return to structured editor version",
        width="stretch",
        key="reset_seo_article_ai_content",
    )

    if reset_ai_version:
        st.session_state.pop(
            AI_CONTENT_KEY,
            None,
        )

        st.session_state.pop(
            AI_EDITOR_KEY,
            None,
        )

        st.rerun()

    cleaned_edited_content = (
        edited_ai_content.strip()
    )

    if not cleaned_edited_content:
        return default_content

    st.session_state[
        AI_CONTENT_KEY
    ] = edited_ai_content

    return edited_ai_content


def build_editable_article_text(
    *,
    title: str,
    meta_description: str,
    introduction: str,
    sections: list[dict[str, str]],
    conclusion: str,
    call_to_action: str,
) -> str:
    """Convert the editable article fields into plain text.

    TXT means Plain Text File. A TXT file contains unformatted text without
    advanced features such as custom fonts, colours, or page layouts.
    """

    parts = [
        title.strip(),
        "",
        (
            "Meta description: "
            f"{meta_description.strip()}"
        ),
        "",
        introduction.strip(),
        "",
    ]

    for section in sections:
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

        if not heading and not content:
            continue

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

    parts.extend(
        [
            "Conclusion",
            "",
            conclusion.strip(),
            "",
            "Call to action",
            "",
            call_to_action.strip(),
        ]
    )

    return "\n".join(
        parts
    ).strip()