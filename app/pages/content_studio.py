from __future__ import annotations

from typing import Any

import streamlit as st

from app.collectors.hotmart_collector import HotmartCollector
from app.components.content_studio.editor_helpers import (
    clear_editor_state,
)
from app.components.content_studio.editor_registry import (
    ContentEditorRegistry,
)
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
editor_registry = ContentEditorRegistry()


def render() -> None:
    """
    Render the Filtrify AI Content Studio page.

    AI = Artificial Intelligence.
    """
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

    selected_product = products[
        selected_product_index
    ]

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
                "The selected content generator "
                "is not available yet."
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

            generated_content = (
                generator_registry.generate(
                    generator_key=(
                        selected_template.generator_key
                    ),
                    product=selected_product,
                    analysis=analysis,
                    field_values=field_values,
                )
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
        ] = dict(
            field_values
        )

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
            "Choose a product and generate content "
            "to open the editor."
        )
        return

    if not editor_registry.is_available(
        generated_template_id
    ):
        st.warning(
            "An editor has not yet been configured "
            "for this content type."
        )
        return

    try:
        editor_registry.render(
            template_id=generated_template_id,
            generated_content=generated_content,
            generated_product=generated_product,
        )

    except Exception as exc:
        st.error(
            f"Unable to open the content editor: {exc}"
        )


def render_template_fields(
    *,
    selected_template: Any,
    default_keyword: str,
) -> dict[str, Any]:
    """
    Render the dynamic form fields defined by a template.

    Dynamic:
    Created automatically from configuration rather than
    being manually hardcoded for each content type.
    """
    field_values: dict[str, Any] = {}

    for field in selected_template.fields:
        field_key = (
            "content_template_"
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
            options = list(
                field.options
            )

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
                "Unsupported field type: "
                f"{field.field_type}"
            )

    return field_values


def validate_required_fields(
    *,
    selected_template: Any,
    field_values: dict[str, Any],
) -> list[str]:
    """
    Return the labels of required fields without a value.
    """
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