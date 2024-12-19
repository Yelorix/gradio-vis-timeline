<h1 style='text-align: center; margin-bottom: 1rem'> Gradio vis.js Timeline </h1>

<div style="display: flex; flex-direction: row; justify-content: center">
<img style="display: block; padding-right: 5px; height: 20px;" alt="Static Badge" src="https://img.shields.io/pypi/v/gradio_vistimeline">
<a href="https://github.com/Yelorix/gradio-vis-timeline" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/github-white?logo=github&logoColor=black"></a>
<a href="https://huggingface.co/spaces/Yelorix/gradio_vistimeline" target="_blank"><img alt="Open in Spaces" src="https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm-dark.svg"></a>
</div>

A Gradio component that implements the [vis.js Timeline](https://github.com/visjs/vis-timeline) visualization library, allowing you to create interactive timelines in your Gradio apps.

**Resources:**
- [Timeline Examples](https://visjs.github.io/vis-timeline/examples/timeline/)
- [Timeline Documentation](https://visjs.github.io/vis-timeline/docs/timeline/)
- [Dataset Documentation](https://visjs.github.io/vis-data/data/dataset.html)

## Installation

```bash
pip install gradio_vistimeline
```

## Usage

```python
import gradio as gr
from gradio_vistimeline import VisTimeline

demo = gr.Interface(
    lambda x: x,
    VisTimeline(
        value={
            "items": [
                {"content": "Item 1", "start": "2024-12-2", "end": "2024-12-10"},
                {"content": "Item 2", "start": "2024-12-14"}
            ]
        },
        options={
            "start": "2024-12-1",
            "end": "2024-12-15",
            "editable": True
        }
    ),
    "json"
)

if __name__ == "__main__":
    demo.launch()
```

## `VisTimeline`

### Features

- Interactive timeline visualization
- Integration of vis.js Timeline includes:
    - Items
    - Ranges
    - Points
    - Background items
    - Groups
    - Subgroups
- Pass options object during instantiation
- Styled with the gradio style variables
- Gradio events for editing data and selecting items

### Value Data Format

The timeline accepts a value in the following format:

```python
{
    "groups": [
        {
            "id": "group_id", 
            "content": "Group Name" # Optional
        }
    ],
    "items": [
        {
            "content": "Item content",
            "start": "2024-01-01",  # ISO date string or Unix timestamp
            "end": "2024-01-05",    # Optional
            "group": "group_id",    # Optional
        }
    ]
}
```

Or as a VisTimelineData object:

```python
from gradio_vistimeline import VisTimelineGroup, VisTimelineItem, VisTimelineData

value = VisTimelineData(
    groups=[
        VisTimelineGroup(
            id="group_id", 
            content="Group Name"   # Optional
        )
    ],
    items=[
        VisTimelineItem(
            content="Item content",
            start="2024-01-01",    # ISO date string or Unix timestamp
            end="2024-01-05",      # Optional
            group="group_id"       # Optional
        )
    ]
)
```

### Events

| name | description |
|:-----|:------------|
| `load` | Triggered when the component is mounted for the first time |
| `change` | Triggered when the timeline value changes through any means |
| `input` | Triggered when a user directly modifies timeline items (add/remove/update) |
| `select` | Triggered when clicking the timeline |
| `item_select` | Triggered when items are selected or unselected |

### Configuration

#### vis.js Timeline Options

The component accepts all configuration options supported by vis.js Timeline. Some commonly used options:

```python
options = {
    "editable": True,             # Enable item editing
    "multiselect": True,          # Allow selecting multiple items
    "showCurrentTime": True,      # Show a marker for current time
    "stack": True,                # Stack overlapping items
    "zoomable": True              # Allow zooming the timeline
}
```

For a complete list of options, see the [vis.js Timeline documentation](https://visjs.github.io/vis-timeline/docs/timeline/).

#### Component-Specific Options

**Data Synchronization**
```python
VisTimeline(
    value=value,
    preserve_old_content_on_value_change=True  # Default: False
)
```
Controls how the timeline updates their groups and items DataSets when the component value changes:
- `False`: Clears and reinitializes all DataSets to ensure perfect sync with the Gradio component value
- `True`: Merges new data with existing content (updates existing items, adds new ones, removes missing ones)

Defaulted to false to ensure the value matches the visualization on the timeline.

Changing it to true reduces visual flicker when dragging items around. 
Desync is only a real risk in this mode when you edit item ID's or add/remove item properties of existing items.

**JavaScript Integration**
```python
VisTimeline(
    value=value,
    elem_id="my-timeline"  # Optional
)
```
When `elem_id` is set, the timeline instance becomes available in JavaScript as `window.visTimelineInstances["my-timeline"]`, allowing easy access through custom scripts.

**Styling Items**
The component provides pre-defined color classes matching Gradio's theme colors. Apply them by setting an item's `className`:

```python
item = {
    "content": "Colored item",
    "start": "2024-01-01",
    "className": "color-primary-500"  # Uses Gradio's primary-500 color
}
```

Available color classes follow the pattern:
- `color-primary-[50-950]`
- `color-secondary-[50-950]`
- `color-neutral-[50-950]`

Custom styles can be applied by defining your own CSS classes.
