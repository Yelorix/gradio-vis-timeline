from typing import Any, Callable, Optional, List, Union
from gradio.data_classes import GradioModel

class VisTimelineGroup(GradioModel):
    id: Union[str, int]
    content: str
    className: Optional[str] = None
    style: Optional[str] = None
    order: Optional[Union[str, int]] = None
    subgroupOrder: Optional[Union[str, Callable]] = None
    subgroupStack: Optional[Union[bool, dict]] = None
    subgroupVisibility: Optional[dict] = None
    title: Optional[str] = None
    visible: Optional[bool] = None
    nestedGroups: Optional[List[Union[str, int]]] = None
    showNested: Optional[bool] = None

class VisTimelineItem(GradioModel):
    id: Optional[Union[str, int]] = None
    content: str
    start: str
    end: Optional[str] = None
    group: Optional[Union[str, int]] = None
    className: Optional[str] = None
    align: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None  # 'box', 'point', 'range', or 'background'
    selectable: Optional[bool] = None
    limitSize: Optional[bool] = None
    subgroup: Optional[Union[str, int]] = None

class VisTimelineData(GradioModel):
    groups: List[Union[VisTimelineGroup, dict[str, Any]]]
    items: List[Union[VisTimelineItem, dict[str, Any]]]
