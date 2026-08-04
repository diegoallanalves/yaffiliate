from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.components.content_studio.landing_page_editor import (
    render_landing_page_editor,
)
from app.components.content_studio.seo_article_editor import (
    render_seo_article_editor,
)


# Callable:
# A Python object that can be executed like a function.
EditorRenderer = Callable[..., None]


@dataclass(frozen=True)
class ContentEditorDefinition:
    """
    Stores the configuration required to render one editor.

    content_parameter:
    The parameter name expected by the editor function.

    Example:
    The SEO editor expects generated content through a
    parameter named "article".

    SEO = Search Engine Optimization.
    """

    renderer: EditorRenderer
    content_parameter: str


class ContentEditorRegistry:
    """
    Central registry for AI Content Studio editors.

    AI = Artificial Intelligence.

    Registry:
    A central place that stores and retrieves available
    content editors.

    This prevents the Content Studio page from requiring
    separate if/elif conditions for every content type.
    """

    def __init__(self) -> None:
        self._editors: dict[
            str,
            ContentEditorDefinition,
        ] = {
            "seo_article": ContentEditorDefinition(
                renderer=render_seo_article_editor,
                content_parameter="article",
            ),
            "landing_page": ContentEditorDefinition(
                renderer=render_landing_page_editor,
                content_parameter="landing_page",
            ),
        }

    def get(
        self,
        template_id: str,
    ) -> ContentEditorDefinition | None:
        """
        Return an editor definition using its template ID.

        ID = Identifier.

        An identifier is a unique value used to distinguish
        one template from another.
        """
        cleaned_template_id = (
            template_id.strip().casefold()
        )

        return self._editors.get(
            cleaned_template_id
        )

    def register(
        self,
        *,
        template_id: str,
        renderer: EditorRenderer,
        content_parameter: str,
    ) -> None:
        """
        Register or replace a Content Studio editor.

        Future examples:
        - email_sequence
        - google_ads
        - product_review
        """
        cleaned_template_id = (
            template_id.strip().casefold()
        )

        cleaned_content_parameter = (
            content_parameter.strip()
        )

        if not cleaned_template_id:
            raise ValueError(
                "Template ID cannot be empty."
            )

        if not callable(renderer):
            raise TypeError(
                "Editor renderer must be callable."
            )

        if not cleaned_content_parameter:
            raise ValueError(
                "Content parameter cannot be empty."
            )

        self._editors[
            cleaned_template_id
        ] = ContentEditorDefinition(
            renderer=renderer,
            content_parameter=(
                cleaned_content_parameter
            ),
        )

    def unregister(
        self,
        template_id: str,
    ) -> bool:
        """
        Remove an editor from the registry.

        Returns True when an editor was removed.
        Returns False when the template ID did not exist.
        """
        cleaned_template_id = (
            template_id.strip().casefold()
        )

        if cleaned_template_id not in self._editors:
            return False

        del self._editors[
            cleaned_template_id
        ]

        return True

    def is_available(
        self,
        template_id: str,
    ) -> bool:
        """
        Check whether an editor is registered.
        """
        return self.get(
            template_id
        ) is not None

    def list_available_keys(
        self,
    ) -> list[str]:
        """
        Return all registered editor template IDs.
        """
        return sorted(
            self._editors.keys()
        )

    def render(
        self,
        *,
        template_id: str,
        generated_content: Any,
        generated_product: str,
    ) -> None:
        """
        Render the editor registered for a content template.
        """
        editor_definition = self.get(
            template_id
        )

        if editor_definition is None:
            raise ValueError(
                (
                    "An editor has not been registered "
                    "for this content type: "
                    f"{template_id}"
                )
            )

        editor_arguments = {
            editor_definition.content_parameter: (
                generated_content
            ),
            "generated_product": generated_product,
        }

        editor_definition.renderer(
            **editor_arguments
        )