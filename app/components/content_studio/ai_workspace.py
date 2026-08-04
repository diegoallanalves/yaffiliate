"""Reusable Artificial Intelligence Workspace for Filtrify editors.

The workspace reads available actions from the Artificial Intelligence action
registry and automatically renders the corresponding Streamlit controls.

Streamlit is the Python framework used to build Filtrify's web interface.
"""

from dataclasses import dataclass

import streamlit as st

from app.ai_actions import (
    AIActionContext,
    AIActionResult,
)
from app.services.ai_action_loader import (
    ensure_ai_actions_loaded,
)
from app.services.ai_action_registry import (
    AIActionRegistry,
)


@dataclass(frozen=True)
class AIWorkspaceResponse:
    """Information returned after the workspace processes an action.

    Attributes:
        action_executed:
            Indicates whether the user selected and executed an action.

        result:
            Result returned by the selected Artificial Intelligence action.

        accepted_content:
            Suggested content accepted by the user. This remains ``None`` until
            a generated suggestion is accepted.

        discarded:
            Indicates whether the current suggestion was discarded.
    """

    action_executed: bool = False
    result: AIActionResult | None = None
    accepted_content: str | None = None
    discarded: bool = False


def render_ai_workspace(
    content: str,
    *,
    content_type: str | None = None,
    language: str | None = None,
    tone: str | None = None,
    target_audience: str | None = None,
    keywords: tuple[str, ...] = (),
    key_prefix: str = "ai_workspace",
    registry: AIActionRegistry | None = None,
) -> AIWorkspaceResponse:
    """Render the reusable Filtrify Artificial Intelligence Workspace.

    Args:
        content:
            Current editor content that may be transformed.

        content_type:
            Type of content being edited, such as ``seo_article`` or
            ``landing_page``.

        language:
            Language in which the generated result should be written.

        tone:
            Desired writing tone.

        target_audience:
            Intended audience for the content.

        keywords:
            Search-engine keywords that should be considered.

        key_prefix:
            Unique prefix used for Streamlit component keys. Each editor should
            provide a different prefix to prevent duplicate-key errors.

        registry:
            Optional custom action registry. When omitted, Filtrify's shared
            application registry is used.

    Returns:
        An ``AIWorkspaceResponse`` describing what happened in the workspace.
    """

    action_registry = ensure_ai_actions_loaded(
        registry
    )

    _initialize_workspace_state(
        key_prefix
    )

    st.markdown(
        "### ✨ AI Workspace"
    )

    st.caption(
        "Improve the current content using registered Artificial Intelligence "
        "actions. Suggestions will not replace your content automatically."
    )

    if not action_registry.all():
        st.info(
            "No Artificial Intelligence actions are currently available."
        )

        return AIWorkspaceResponse()

    additional_instructions = _render_workspace_options(
        key_prefix=key_prefix,
    )

    action_context = AIActionContext(
        content_type=content_type,
        language=language,
        tone=tone,
        target_audience=target_audience,
        keywords=keywords,
        additional_instructions=(
            additional_instructions
            or None
        ),
    )

    executed_result = _render_action_groups(
        registry=action_registry,
        content=content,
        context=action_context,
        key_prefix=key_prefix,
    )

    if executed_result is not None:
        _save_result_to_state(
            key_prefix=key_prefix,
            result=executed_result,
        )

    current_result = _get_result_from_state(
        key_prefix
    )

    if current_result is None:
        return AIWorkspaceResponse(
            action_executed=(
                executed_result is not None
            ),
        )

    return _render_suggestion_panel(
        result=current_result,
        key_prefix=key_prefix,
        action_executed=(
            executed_result is not None
        ),
    )


def _initialize_workspace_state(
    key_prefix: str,
) -> None:
    """Create the Streamlit session values required by the workspace."""

    result_key = _state_key(
        key_prefix,
        "result",
    )

    accepted_key = _state_key(
        key_prefix,
        "accepted_content",
    )

    if result_key not in st.session_state:
        st.session_state[
            result_key
        ] = None

    if accepted_key not in st.session_state:
        st.session_state[
            accepted_key
        ] = None


def _render_workspace_options(
    *,
    key_prefix: str,
) -> str:
    """Render optional instructions that apply to the selected action."""

    with st.expander(
        "Additional instructions",
        expanded=False,
    ):
        instructions = st.text_area(
            "Tell the AI how the content should be changed",
            placeholder=(
                "Example: Make it more persuasive, use shorter paragraphs, "
                "and keep the tone friendly."
            ),
            key=_widget_key(
                key_prefix,
                "additional_instructions",
            ),
            height=100,
        )

        st.caption(
            "These instructions will be included when an action is executed."
        )

    return instructions.strip()


def _render_action_groups(
    *,
    registry: AIActionRegistry,
    content: str,
    context: AIActionContext,
    key_prefix: str,
) -> AIActionResult | None:
    """Render every action before executing the selected action.

    Rendering all buttons first prevents later actions from disappearing when
    an earlier action is selected.
    """

    selected_action_key: str | None = None

    for category, actions in registry.grouped().items():
        st.markdown(
            f"#### {category}"
        )

        number_of_columns = min(
            len(actions),
            4,
        )

        columns = st.columns(
            number_of_columns
        )

        for index, action in enumerate(
            actions
        ):
            column = columns[
                index % number_of_columns
            ]

            with column:
                button_clicked = st.button(
                    f"{action.icon} {action.title}",
                    help=action.description,
                    key=_widget_key(
                        key_prefix,
                        f"action_{action.key}",
                    ),
                    width="stretch",
                )

                if button_clicked:
                    selected_action_key = (
                        action.key
                    )

    if selected_action_key is None:
        return None

    try:
        return registry.execute(
            key=selected_action_key,
            content=content,
            context=context,
        )

    except (
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        st.error(
            str(error)
        )

    except Exception as error:
        st.error(
            "The Artificial Intelligence action could not be completed."
        )

        st.exception(
            error
        )

    return None


def _render_suggestion_panel(
    *,
    result: AIActionResult,
    key_prefix: str,
    action_executed: bool,
) -> AIWorkspaceResponse:
    """Render the latest action result and its decision controls."""

    st.divider()

    st.markdown(
        f"#### {result.action_title} suggestion"
    )

    if result.message:
        if result.success:
            st.info(
                result.message
            )
        else:
            st.error(
                result.message
            )

    original_tab, suggestion_tab = st.tabs(
        [
            "Original content",
            "AI suggestion",
        ]
    )

    with original_tab:
        st.text_area(
            "Original",
            value=result.original_content,
            height=280,
            disabled=True,
            key=_widget_key(
                key_prefix,
                f"original_{result.action_key}",
            ),
            label_visibility="collapsed",
        )

    with suggestion_tab:
        suggested_content = st.text_area(
            "Suggestion",
            value=result.generated_content,
            height=280,
            key=_widget_key(
                key_prefix,
                f"suggestion_{result.action_key}",
            ),
            label_visibility="collapsed",
        )

    if (
        result.metadata.get("status")
        == "provider_not_connected"
    ):
        with st.expander(
            "Development prompt preview",
            expanded=False,
        ):
            prompt = result.metadata.get(
                "prompt"
            )

            if isinstance(
                prompt,
                str,
            ) and prompt:
                st.code(
                    prompt,
                    language="text",
                )
            else:
                st.caption(
                    "No prompt preview is available."
                )

    accept_column, discard_column = st.columns(
        2
    )

    with accept_column:
        accepted = st.button(
            "Accept suggestion",
            type="primary",
            width="stretch",
            key=_widget_key(
                key_prefix,
                "accept_suggestion",
            ),
        )

    with discard_column:
        discarded = st.button(
            "Discard suggestion",
            width="stretch",
            key=_widget_key(
                key_prefix,
                "discard_suggestion",
            ),
        )

    if accepted:
        st.session_state[
            _state_key(
                key_prefix,
                "accepted_content",
            )
        ] = suggested_content

        _clear_result_from_state(
            key_prefix
        )

        st.success(
            "Suggestion accepted. It can now be applied to the editor."
        )

        return AIWorkspaceResponse(
            action_executed=action_executed,
            result=result,
            accepted_content=suggested_content,
            discarded=False,
        )

    if discarded:
        _clear_result_from_state(
            key_prefix
        )

        st.info(
            "Suggestion discarded."
        )

        return AIWorkspaceResponse(
            action_executed=action_executed,
            result=result,
            accepted_content=None,
            discarded=True,
        )

    return AIWorkspaceResponse(
        action_executed=action_executed,
        result=result,
        accepted_content=None,
        discarded=False,
    )


def _save_result_to_state(
    *,
    key_prefix: str,
    result: AIActionResult,
) -> None:
    """Save the most recent action result in the Streamlit session."""

    st.session_state[
        _state_key(
            key_prefix,
            "result",
        )
    ] = result

    st.session_state[
        _state_key(
            key_prefix,
            "accepted_content",
        )
    ] = None


def _get_result_from_state(
    key_prefix: str,
) -> AIActionResult | None:
    """Return the current result stored for the workspace."""

    result = st.session_state.get(
        _state_key(
            key_prefix,
            "result",
        )
    )

    if isinstance(
        result,
        AIActionResult,
    ):
        return result

    return None


def _clear_result_from_state(
    key_prefix: str,
) -> None:
    """Remove the current action result from the Streamlit session."""

    st.session_state[
        _state_key(
            key_prefix,
            "result",
        )
    ] = None


def _state_key(
    key_prefix: str,
    name: str,
) -> str:
    """Build a unique Streamlit session-state key."""

    return (
        f"{key_prefix}__{name}"
    )


def _widget_key(
    key_prefix: str,
    name: str,
) -> str:
    """Build a unique Streamlit widget key."""

    return (
        f"{key_prefix}__widget__{name}"
    )