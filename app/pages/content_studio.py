from __future__ import annotations

from typing import Any

import streamlit as st

from app.collectors.hotmart_collector import HotmartCollector
from app.components.layout import page_header
from app.services.comparison_service import ComparisonService
from app.services.content_generator_registry import (
    ContentGeneratorRegistry,
)
from app.services.content_template_service import (
    ContentTemplateService,
)
from app.services.product_analysis_service import (
    ProductAnalysisService,
)


collector = HotmartCollector()
comparison_service = ComparisonService()
analysis_service = ProductAnalysisService()
template_service = ContentTemplateService()
generator_registry = ContentGeneratorRegistry()


def render() -> None:
    page_header(
        "AI Content Studio",
        "Generate structured content from product intelligence.",
        (
            "Choose a product, select a content template and create "
            "an editable marketing asset."
        ),
    )

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    if not products:
        st.info(
            "No products are available for content generation."
        )
        return

    product_options = {
        index: product.product_name
        for index, product in enumerate(products)
    }

    selected_product_index = st.selectbox(
        "Select a product",
        options=list(product_options.keys()),
        format_func=lambda index: product_options[index],
    )

    selected_product = products[selected_product_index]

    default_keyword = (
        selected_product.product_name
        .replace("Masterclass", "course")
        .strip()
    )

    templates = template_service.list_templates()

    if not templates:
        st.info(
            "No content templates are currently available."
        )
        return

    template_lookup = {
        template.template_id: template
        for template in templates
    }

    selected_template_id = st.selectbox(
        "Content template",
        options=list(template_lookup.keys()),
        format_func=lambda template_id: (
            f"{template_lookup[template_id].icon} "
            f"{template_lookup[template_id].name}"
        ),
    )

    selected_template = template_lookup[
        selected_template_id
    ]

    st.caption(
        selected_template.description
    )

    field_values = render_template_fields(
        selected_template=selected_template,
        default_keyword=default_keyword,
    )

    generate_content = st.button(
        f"Generate {selected_template.name}",
        type="primary",
        width="stretch",
    )

    if generate_content:
        missing_fields = validate_required_fields(
            selected_template=selected_template,
            field_values=field_values,
        )

        if missing_fields:
            st.error(
                "Complete the following required fields: "
                + ", ".join(missing_fields)
            )
            return

        if not generator_registry.is_available(
            selected_template.generator_key
        ):
            st.error(
                "The selected content generator is not available yet."
            )
            return

        try:
            comparison = comparison_service.compare(
                products
            )

            selected_comparison = next(
                (
                    item
                    for item in comparison.products
                    if (
                        item.product.product_name
                        == selected_product.product_name
                    )
                ),
                None,
            )

            analysis = analysis_service.analyse(
                product=selected_product,
                comparison=selected_comparison,
            )

            generated_content = generator_registry.generate(
                generator_key=selected_template.generator_key,
                product=selected_product,
                analysis=analysis,
                field_values=field_values,
            )

        except Exception as exc:
            st.error(
                f"Unable to generate the content: {exc}"
            )
            return

        clear_editor_state()

        st.session_state[
            "generated_content"
        ] = generated_content

        st.session_state[
            "generated_content_product"
        ] = selected_product.product_name

        st.session_state[
            "generated_content_template_id"
        ] = selected_template.template_id

        st.session_state[
            "generated_content_field_values"
        ] = dict(field_values)

        st.rerun()

    generated_content = st.session_state.get(
        "generated_content"
    )

    generated_product = st.session_state.get(
        "generated_content_product",
        "",
    )

    generated_template_id = st.session_state.get(
        "generated_content_template_id",
        "",
    )

    if generated_content is None:
        st.info(
            "Choose a product and generate content to open the editor."
        )
        return

    if generated_template_id == "seo_article":
        render_seo_article_editor(
            article=generated_content,
            generated_product=generated_product,
        )

    else:
        st.warning(
            "An editor has not yet been configured for this "
            "content type."
        )


def render_template_fields(
    *,
    selected_template: Any,
    default_keyword: str,
) -> dict[str, Any]:
    field_values: dict[str, Any] = {}

    for field in selected_template.fields:
        field_key = (
            f"content_template_"
            f"{selected_template.template_id}_"
            f"{field.name}"
        )

        if field.field_type == "text":
            if field.name == "keyword":
                default_value = (
                    field.default_value
                    or default_keyword
                )
            else:
                default_value = (
                    field.default_value
                    or ""
                )

            field_values[field.name] = st.text_input(
                field.label,
                value=str(default_value),
                placeholder=field.placeholder,
                help=field.help_text or None,
                key=field_key,
            )

        elif field.field_type == "textarea":
            field_values[field.name] = st.text_area(
                field.label,
                value=str(
                    field.default_value
                    or ""
                ),
                placeholder=field.placeholder,
                help=field.help_text or None,
                key=field_key,
            )

        elif field.field_type == "select":
            options = list(field.options)

            if not options:
                field_values[field.name] = None
                continue

            default_index = 0

            if (
                field.default_value
                and field.default_value in options
            ):
                default_index = options.index(
                    field.default_value
                )

            field_values[field.name] = st.selectbox(
                field.label,
                options=options,
                index=default_index,
                help=field.help_text or None,
                key=field_key,
            )

        else:
            st.warning(
                f"Unsupported field type: {field.field_type}"
            )

    return field_values


def validate_required_fields(
    *,
    selected_template: Any,
    field_values: dict[str, Any],
) -> list[str]:
    missing_fields: list[str] = []

    for field in selected_template.fields:
        if not field.required:
            continue

        value = field_values.get(
            field.name
        )

        if value is None:
            missing_fields.append(
                field.label
            )
            continue

        if (
            isinstance(value, str)
            and not value.strip()
        ):
            missing_fields.append(
                field.label
            )

    return missing_fields


def render_seo_article_editor(
    *,
    article: Any,
    generated_product: str,
) -> None:
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
        f"Meta-description length: "
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
                key=f"seo_section_heading_{index}",
            )

            edited_content = st.text_area(
                "Content",
                value=section.content,
                height=180,
                key=f"seo_section_content_{index}",
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

    edited_article_text = build_editable_article_text(
        title=edited_title,
        meta_description=edited_meta_description,
        introduction=edited_introduction,
        sections=edited_sections,
        conclusion=edited_conclusion,
        call_to_action=edited_call_to_action,
    )

    edited_word_count = len(
        edited_article_text.split()
    )

    st.caption(
        f"Current edited word count: "
        f"{edited_word_count:,}"
    )

    st.divider()

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        st.download_button(
            label="Download edited article as TXT",
            data=edited_article_text,
            file_name=(
                "filtrify_"
                f"{slugify(article.target_keyword)}"
                "_article.txt"
            ),
            mime="text/plain",
            width="stretch",
        )

    with action_col2:
        save_edits = st.button(
            "Save edits in session",
            width="stretch",
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
            "article_text": edited_article_text,
            "word_count": edited_word_count,
        }

        st.success(
            "Article edits were saved in this session."
        )

    saved_article = st.session_state.get(
        "edited_seo_article"
    )

    if saved_article:
        st.info(
            "A saved edited version is available in this "
            "session. Current saved word count: "
            f'{saved_article["word_count"]:,}.'
        )


def build_editable_article_text(
    *,
    title: str,
    meta_description: str,
    introduction: str,
    sections: list[dict[str, str]],
    conclusion: str,
    call_to_action: str,
) -> str:
    parts = [
        title.strip(),
        "",
        f"Meta description: "
        f"{meta_description.strip()}",
        "",
        introduction.strip(),
        "",
    ]

    for section in sections:
        heading = section["heading"].strip()
        content = section["content"].strip()

        if not heading and not content:
            continue

        parts.extend(
            [
                heading,
                "",
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

    return "\n".join(parts).strip()


def clear_editor_state() -> None:
    editor_keys = [
        "seo_article_title",
        "seo_article_meta_description",
        "seo_article_introduction",
        "seo_article_conclusion",
        "seo_article_call_to_action",
        "edited_seo_article",
    ]

    editor_keys.extend(
        [
            key
            for key in list(
                st.session_state.keys()
            )
            if (
                key.startswith(
                    "seo_section_heading_"
                )
                or key.startswith(
                    "seo_section_content_"
                )
            )
        ]
    )

    for key in editor_keys:
        st.session_state.pop(
            key,
            None,
        )


def slugify(
    value: str,
) -> str:
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

    return slug or "seo_article"