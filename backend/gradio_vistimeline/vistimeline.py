from __future__ import annotations
from typing import Any, Callable, Union
from gradio.components import Component
from gradio.events import Events
from .model import VisTimelineData

class VisTimeline(Component):
    """
    Custom Gradio component integrating vis.js Timeline.
    """
    data_model = VisTimelineData
    EVENTS = [Events.load, Events.change, Events.input, "item_select", Events.select]

    def __init__(
        self,
        value: Union[VisTimelineData, dict[str, Any], Callable, None] = None,
        options: dict[str, Any] | None = None,
        preserve_old_content_on_value_change: bool = False,
        *,
        label: str | None = None,
        interactive: bool | None = True,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | None = None,
    ):
        self.value = self._get_default_value_if_none(value)
        self.options = options or {}
        self.preserve_old_content_on_value_change = preserve_old_content_on_value_change

        super().__init__(
            value=self.value,
            label=label,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key
        )

    def preprocess(self, payload: Union[VisTimelineData, dict[str, Any], None]) -> Union[VisTimelineData, dict[str, Any], None]:
        return self._get_default_value_if_none(payload)

    def postprocess(self, value: Union[VisTimelineData, dict[str, Any], None]) -> Union[VisTimelineData, dict[str, Any], None]:
        def remove_first_level_none_properties(obj):
            return {key: value for key, value in obj.items() if value is not None}

        value = self._get_default_value_if_none(value)

        if isinstance(value, VisTimelineData):
            value.groups = [remove_first_level_none_properties(vars(group)) for group in value.groups]
            value.items = [remove_first_level_none_properties(vars(item)) for item in value.items]
        elif isinstance(value, dict):
            value["groups"] = [remove_first_level_none_properties(group) for group in value.get("groups", [])]
            value["items"] = [remove_first_level_none_properties(item) for item in value.get("items", [])]

        return value

    def example_payload(self) -> Any:
        return {
            "groups": [{"id": 0, "content": "Group 1"}],
            "items": [{"content": "Item 1", "group": 0, "start": "2024-01-01"}]
        }

    def example_value(self) -> dict[str, Any]:
        return self.example_payload()
    
    def _get_default_value_if_none(self, value):
        if isinstance(value, VisTimelineData):
            return value or VisTimelineData(groups=[], items=[])
        else:
            return value or {"groups": [], "items": []}
