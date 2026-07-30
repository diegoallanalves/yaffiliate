from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContentTemplateField:
    """
    One configurable input shown in Content Studio.
    """

    name: str
    label: str
    field_type: str = "text"
    default_value: Any = None
    placeholder: str = ""
    options: list[str] = field(default_factory=list)
    required: bool = False
    help_text: str = ""


@dataclass(slots=True)
class ContentTemplate:
    """
    Defines one content type available in AI Content Studio.
    """

    template_id: str
    name: str
    description: str
    icon: str
    generator_key: str
    fields: list[ContentTemplateField] = field(
        default_factory=list
    )
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "TemplateID": self.template_id,
            "Name": self.name,
            "Description": self.description,
            "Icon": self.icon,
            "GeneratorKey": self.generator_key,
            "Enabled": self.enabled,
            "Fields": [
                {
                    "Name": field.name,
                    "Label": field.label,
                    "FieldType": field.field_type,
                    "DefaultValue": field.default_value,
                    "Placeholder": field.placeholder,
                    "Options": list(field.options),
                    "Required": field.required,
                    "HelpText": field.help_text,
                }
                for field in self.fields
            ],
        }