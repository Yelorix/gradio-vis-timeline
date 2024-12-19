import datetime as dt
import gradio as gr
import json
import numpy as np
import os
from datetime import timedelta, date, datetime
from gradio_vistimeline import VisTimeline, VisTimelineData

# --- Region: Handlers for demo tab 1 ---
def pull_from_timeline(timeline):
    """Convert timeline data to JSON string for display"""
    if hasattr(timeline, "model_dump"):
        data = timeline.model_dump(exclude_none=True)
    else:
        data = timeline
    return json.dumps(data, indent=2)

def push_to_timeline(json_str):
    """Convert JSON string to timeline data"""
    try:
        return VisTimelineData.model_validate_json(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return VisTimelineData(groups=[], items=[])

def on_timeline_change():
    return f"Most recent value change event:\n{get_now()}"

def on_timeline_input(event_data: gr.EventData):
    return f"Most recent input event:\nAction: '{event_data._data}' at {get_now()}"

def on_timeline_select():
    return f"Most recent timeline selected event::\n{get_now()}"

def on_item_select(timeline, event_data: gr.EventData):
    selected_ids = event_data._data # A collection of selected item IDs that can be str or int: ["example", 0, "example2"]
    items = timeline.items

    if selected_ids:
        first_id = selected_ids[0]
        for item in items:
            if item.id == first_id:
                content = getattr(item, 'content', 'Unknown')
                return f"Currently selected item:\nContent: \"{content}\"\nID: \"{first_id}\""
    
    return "Currently selected item:\nNone"

# --- Region: Handlers for demo tab 1 ---
def update_table(timeline):
    if hasattr(timeline, "model_dump"):
        data = timeline.model_dump(exclude_none=True)
    else:
        data = timeline
    
    items = data["items"]
    track_length_ms = get_grouped_item_end_in_ms(items, "track-length")

    rows = []
    for item in items:
        if item["content"] != "":
            duration = calculate_and_format_duration(item["start"], item.get("end"), track_length_ms)
            rows.append([
                item["content"],
                format_date_to_milliseconds(item["start"]),
                duration
            ])
    
    return gr.DataFrame(
        value=rows,
        headers=["Item Name", "Start Time", "Duration"]
    )

# --- Region: Handlers for demo tab 2 ---
def update_audio(timeline):
    """
    Handler function for generating audio from timeline data.
    Returns audio data in format expected by Gradio's Audio component.
    """
    audio_data, sample_rate = generate_audio_from_timeline(timeline)
    # Convert to correct shape and data type for Gradio Audio
    # Gradio expects a 2D array with shape (samples, channels)
    audio_data = audio_data.reshape(-1, 1)  # Make it 2D with 1 channel
    return (sample_rate, audio_data)

def generate_audio_from_timeline(timeline_data, sample_rate=44100):
    """
    Generate audio from timeline items containing frequency information.
    
    Args:
        timeline_data: Timeline data containing items with start/end times in milliseconds
        sample_rate: Audio sample rate in Hz (default 44100)
        
    Returns:
        Tuple of (audio_data: np.ndarray, sample_rate: int)
    """
    # Get all items from the timeline
    if hasattr(timeline_data, "model_dump"):
        data = timeline_data.model_dump(exclude_none=True)
    else:
        data = timeline_data
    
    items = data["items"]
    
    # Find the track length from the background item
    track_length_ms = get_grouped_item_end_in_ms(items, "track-length")
    
    # Convert milliseconds to samples
    total_samples = int((track_length_ms / 1000) * sample_rate)
    
    # Initialize empty audio buffer
    audio_buffer = np.zeros(total_samples)
    
    # Frequency mapping
    freq_map = {
        1: 440.0,
        2: 554.37,
        3: 659.26
    }
    # Generate sine waves for each item
    for item in items:
        id = item.get("id", 0)
        start_time = parse_date_to_milliseconds(item["start"])
        end_time = parse_date_to_milliseconds(item["end"])

        # Skip items that are completely outside the valid range
        if end_time <= 0 or start_time >= track_length_ms or start_time >= end_time:
            continue
            
        # Clamp times to valid range
        start_time = max(0, min(start_time, track_length_ms))
        end_time = max(0, min(end_time, track_length_ms))

        if id in freq_map:
            freq = freq_map[id]
            
            # Convert millisecond timestamps to sample indices
            start_sample = int((start_time / 1000) * sample_rate)
            end_sample = int((end_time / 1000) * sample_rate)
            
            # Generate time array for this segment
            t = np.arange(start_sample, end_sample)
            
            # Generate sine wave
            duration = end_sample - start_sample
            envelope = np.ones(duration)
            fade_samples = min(int(0.10 * sample_rate), duration // 2)  # 100ms fade or half duration
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            wave = 0.2 * envelope * np.sin(2 * np.pi * freq * t / sample_rate)
            
            # Add to buffer
            audio_buffer[start_sample:end_sample] += wave
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio_buffer))
    if max_val > 0:
        audio_buffer = audio_buffer / max_val
    
    return (audio_buffer, sample_rate)

# Helper function to get hard-coded track-length from timeline value
def get_grouped_item_end_in_ms(items, group_id):
    default_length = 6000
    for item in items:
        if item.get("group") == group_id:
            return parse_date_to_milliseconds(item.get("end", default_length))
    return default_length

# --- Region: Demo specific datetime helper functions ---
def calculate_and_format_duration(start_date, end_date, max_range):
    """Calculate the seconds between two datetime inputs and format the result with up to 2 decimals."""
    if not end_date:
        return "0s"

    # Convert dates to milliseconds
    start_ms = max(0, parse_date_to_milliseconds(start_date))
    end_ms = min(max_range, parse_date_to_milliseconds(end_date))

    if end_ms < start_ms:
        return "0s"

    # Calculate duration in seconds
    duration = (end_ms - start_ms) / 1000

    # Format to remove trailing zeroes after rounding to 2 decimal places
    formatted_duration = f"{duration:.2f}".rstrip("0").rstrip(".")
    return f"{formatted_duration}s"

def format_date_to_milliseconds(date):
    """Format input (ISO8601 string or milliseconds) to mm:ss.SSS."""
    date_in_milliseconds = max(0, parse_date_to_milliseconds(date))
    time = timedelta(milliseconds=date_in_milliseconds)

    # Format timedelta into mm:ss.SSS
    minutes, seconds = divmod(time.seconds, 60)
    milliseconds_part = time.microseconds // 1000
    return f"{minutes:02}:{seconds:02}.{milliseconds_part:03}"

def parse_date_to_milliseconds(date):
    """Convert input (ISO8601 string or milliseconds) milliseconds"""
    if isinstance(date, int):  # Input is already in milliseconds (Unix timestamp)
        return date
    elif isinstance(date, str):  # Input is ISO8601 datetime string
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
        epoch = datetime(1970, 1, 1, tzinfo=dt.tzinfo) # Calculate difference from Unix epoch
        return int((dt - epoch).total_seconds() * 1000)
    else:
        return 0  # Fallback for unsupported types

def get_now():
    """Returns current time in HH:MM:SS format"""
    return datetime.now().strftime("%H:%M:%S")

TIMELINE_ID = "dateless_timeline"
AUDIO_ID = "timeline-audio"

# Example for how to access the timeline through JavaScript
# In this case, to bind the custom time bar of the timeline to be in sync with the audio component
# Read the JavaScript file
js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_time_control.js')
with open(js_path, 'r') as f:
    js_content = f.read()
script = f"""<script>{js_content}</script>"""
style = f"""<style>.vis-custom-time.{TIMELINE_ID} {{pointer-events: none !important;}}</style>"""
head = script + style

# --- Region: Gradio ---
with gr.Blocks(head=head) as demo:
    today = date.today()
    day_offset = lambda days: (today + dt.timedelta(days=days)).isoformat()

    gr.Markdown("# Vis.js Timeline Component Demo")
    
    with gr.Tabs():
        # --- Tab 1: Basic Timeline with Events ---
        with gr.Tab("Basic Timeline Demo"):
            # Timeline component
            basic_timeline = VisTimeline(
                value={
                    "groups": [{"id": 0, "content": ""}],
                    "items": []
                },
                options= {
                    "start": day_offset(-1),
                    "end": day_offset(20),
                    "editable": True,
                    "format": { # You don't need to define this as these are the default values, but for this demo it is necessary because of two timelines with different formats on one page
                        "minorLabels": { 
                            "millisecond": "SSS",
                            "second": "ss",
                            "minute": "HH:mm",
                            "hour": "HH:mm",
                        }
                    }
                },
                label="Interactive Timeline",
                interactive=True
            )
            
            gr.Markdown("### Events")

            # Event listener outputs
            with gr.Row():
                change_textbox = gr.Textbox(value="Most recent value change event:", label="Change:", lines=3, interactive=False)
                input_textbox = gr.Textbox(value="Most recent user input event:", label="Input:", lines=3, interactive=False)
                select_textbox = gr.Textbox(value="Most recent timeline selected event:", label="Select:", lines=3, interactive=False)
                item_select_textbox = gr.Textbox(value="Currently selected item:\nNone", label="Currently selected item:", lines=3, interactive=False)
            
            # Examples and JSON area in two columns
            with gr.Row():
                # Left column: Examples
                with gr.Column():
                    gr.Markdown("### Timeline Examples")
                    gr.Examples(
                        examples=[
                            {
                                "groups": [{"id": 0, "content": ""}],
                                "items": [
                                    {"content": "Working", "group": 0, "start": day_offset(1), "end": day_offset(5)},
                                    {"content": "Resting", "group": 0, "start": day_offset(5), "end": day_offset(7)},
                                    {"content": "Working", "group": 0, "start": day_offset(7), "end": day_offset(11)},
                                    {"content": "Resting", "group": 0, "start": day_offset(11), "end": day_offset(13)},
                                    {"content": "Working", "group": 0, "start": day_offset(13), "end": day_offset(17)},
                                    {"content": "Resting", "group": 0, "start": day_offset(17), "end": day_offset(19)},
                                    {"content": "Working", "group": 0, "start": day_offset(19), "end": day_offset(23)},
                                ],
                                "description": "DateTime ranges"
                            },
                            {
                                "groups": [{"id": 0, "content": "Group"}],
                                "items": [
                                    {"id": 0, "content": "Simple item", "group": 0, "start": day_offset(9)}
                                ]
                            },
                            {
                                "groups": [{"id": 0, "content": "Worker 1"}, {"id": 1, "content": "Worker 2"}],
                                "items": [
                                    {"content": "Working", "group": 0, "start": day_offset(1), "end": day_offset(5)},
                                    {"content": "Resting", "group": 0, "start": day_offset(5), "end": day_offset(7)},
                                    {"content": "Working", "group": 0, "start": day_offset(7), "end": day_offset(11)},
                                    {"content": "Resting", "group": 0, "start": day_offset(11), "end": day_offset(13)},
                                    {"content": "Working", "group": 0, "start": day_offset(13), "end": day_offset(17)},
                                    {"content": "Resting", "group": 0, "start": day_offset(17), "end": day_offset(19)},
                                    {"content": "Working", "group": 0, "start": day_offset(19), "end": day_offset(23)},
                                    {"content": "Working", "group": 1, "start": day_offset(-3), "end": day_offset(2)},
                                    {"content": "Resting", "group": 1, "start": day_offset(2), "end": day_offset(4)},
                                    {"content": "Working", "group": 1, "start": day_offset(4), "end": day_offset(8)},
                                    {"content": "Resting", "group": 1, "start": day_offset(8), "end": day_offset(10)},
                                    {"content": "Working", "group": 1, "start": day_offset(10), "end": day_offset(14)},
                                    {"content": "Resting", "group": 1, "start": day_offset(14), "end": day_offset(16)},
                                    {"content": "Working", "group": 1, "start": day_offset(16), "end": day_offset(20)}
                                ],
                                "description": "DateTime ranges in groups"
                            },
                            {
                                "groups": [{"id": 1, "content": "Group 1"}, {"id": 2, "content": "Group 2"}],
                                "items": [
                                    {"id": "A", "content": "Period A", "start": day_offset(1), "end": day_offset(7), "type": "background", "group": 1 },
                                    {"id": "B", "content": "Period B", "start": day_offset(8), "end": day_offset(11), "type": "background", "group": 2 },
                                    {"id": "C", "content": "Period C", "start": day_offset(12), "end": day_offset(17), "type": "background" },
                                    {"content": "Range inside period A", "start": day_offset(2), "end": day_offset(6), "group": 1 },
                                    {"content": "Item inside period C", "group": 2, "start": day_offset(14) }
                                ],
                                "description": "Background type example"
                            },
                            {
                                "groups": [{"id": 1, "content": "Group 1"}, {"id": 2, "content": "Group 2"}],
                                "items": [
                                    {"content": "Range item", "group": 1, "start": day_offset(7), "end": day_offset(14) },
                                    {"content": "Point item", "group": 2, "start": day_offset(7), "type": "point" },
                                    {"content": "Point item with a longer name", "group": 2, "start": day_offset(7), "type": "point" },
                                ],
                                "description": "Point type example"
                            },
                            {
                                "groups": [{"id": 1, "content": "Group 1", "subgroupStack": {"A": True, "B": True}}, {"id": 2, "content": "Group 2" }],
                                "items": [
                                    {"content": "Subgroup 2 Background", "start": day_offset(0), "end": day_offset(4), "type": "background", "group": 1, "subgroup": "A", "subgroupOrder": 0},
                                    {"content": "Subgroup 2 Item", "start": day_offset(5), "end": day_offset(7), "group": 1, "subgroup": "A", "subgroupOrder": 0},
                                    {"content": "Subgroup 1 Background", "start": day_offset(0), "end": day_offset(4), "type": "background", "group": 1, "subgroup": "B", "subgroupOrder": 1},
                                    {"content": "Subgroup 1 Item", "start": day_offset(8), "end": day_offset(10), "group": 1, "subgroup": "B", "subgroupOrder": 1},
                                    {"content": "Full group background", "start": day_offset(5), "end": day_offset(9), "type": "background", "group": 2},
                                    {"content": "No subgroup item 1", "start": day_offset(10), "end": day_offset(12), "group": 2},
                                    {"content": "No subgroup item 2", "start": day_offset(13), "end": day_offset(15), "group": 2}
                                    
                                ],
                                "description": "Subgroups with backgrounds and items"
                            },
                            {
                                "groups": [{"id": 1, "content": "Group 1", "subgroupStack": {"A": True, "B": True}}, {"id": 2, "content": "Group 2" }],
                                "items": [
                                    {"content": "Subgroup 2 background", "start": day_offset(0), "end": day_offset(4), "type": "background", "group": 1, "subgroup": "A", "subgroupOrder": 0},
                                    {"content": "Subgroup 2 range", "start": day_offset(5), "end": day_offset(7), "group": 1, "subgroup": "A", "subgroupOrder": 0},
                                    {"content": "Subgroup 2 item", "start": day_offset(10), "group": 1, "subgroup": "A" },
                                    {"content": "Subgroup 1 background", "start": day_offset(0), "end": day_offset(4), "type": "background", "group": 1, "subgroup": "B", "subgroupOrder": 1},
                                    {"content": "Subgroup 1 range", "start": day_offset(8), "end": day_offset(10), "group": 1, "subgroup": "B", "subgroupOrder": 1},
                                    {"content": "Subgroup 1 item", "start": day_offset(14), "group": 1, "subgroup": "B" },
                                    {"content": "No subgroup item", "start": day_offset(12), "group": 1},
                                    {"content": "Full group background", "start": day_offset(5), "end": day_offset(9), "type": "background", "group": 2},
                                    {"content": "No subgroup range 1", "start": day_offset(11), "end": day_offset(13), "group": 2},
                                    {"content": "No subgroup range 2", "start": day_offset(15), "end": day_offset(17), "group": 2},
                                    {"content": "No subgroup point", "start": day_offset(1), "group": 2, "type": "point" }
                                    
                                ],
                                "description": "Combination of item and group types"
                            }
                        ],
                        inputs=basic_timeline
                    )
                
                # Right column: JSON staging area
                with gr.Column():
                    gr.Markdown("### Serialized Timeline Value")
                    json_textbox = gr.Textbox(label="JSON", lines=4)
                    with gr.Row():
                        pull_button = gr.Button("Pull Timeline into JSON")
                        push_button = gr.Button("Push JSON onto Timeline", variant="primary")
            
            # Event handlers
            basic_timeline.change(fn=on_timeline_change, outputs=[change_textbox]) # Triggered when the value of the timeline changes by any means
            basic_timeline.input(fn=on_timeline_input, outputs=[input_textbox]) # Triggered when the value of the timeline changes, caused directly by a user input on the component (dragging, adding & removing items)
            basic_timeline.select(fn=on_timeline_select, outputs=[select_textbox]) # Triggered when the timeline is clicked
            basic_timeline.item_select(fn=on_item_select, inputs=[basic_timeline], outputs=[item_select_textbox]) # Triggered when items are selected or unselected
            
            pull_button.click(fn=pull_from_timeline, inputs=[basic_timeline], outputs=[json_textbox]) # Example of using the timeline as an input
            push_button.click(fn=push_to_timeline, inputs=[json_textbox], outputs=[basic_timeline]) # Example of using the timeline as an output
        
        # --- Tab 2: Timeline without date ---
        with gr.Tab("Timeline Without Date"):
            audio_output = gr.Audio(label="Generated Audio", type="numpy", elem_id=AUDIO_ID)

            dateless_timeline = VisTimeline(
                value={
                    "groups": [{"id": "track-length", "content": ""}, {"id": 1, "content": ""}, {"id": 2, "content": ""}, {"id": 3, "content": ""}],
                    "items": [
                        {"content": "", "group": "track-length", "selectable": False, "type": "background", "start": 0, "end": 6000, "className": "color-primary-600"},
                        {"id": 1, "content": "440.00Hz", "group": 1, "selectable": False, "start": 0, "end": 1500},
                        {"id": 2, "content": "554.37Hz", "group": 2, "selectable": False, "start": 2000, "end": 3500},
                        {"id": 3, "content": "659.26Hz", "group": 3, "selectable": False, "start": 4000, "end": 5500}
                    ]},
                options={
                    "moment": "+00:00", # Force the timeline into a certain UTC offset timezone
                    "showCurrentTime": False,
                    "editable": {
                        "add": False,
                        "remove": False,
                        "updateGroup": False,
                        "updateTime": True
                    },
                    "itemsAlwaysDraggable": { # So dragging does not require selection first
                        "item": True,
                        "range": True
                    },
                    "showMajorLabels": False, # This hides the month & year labels
                    "format": {
                        "minorLabels": { # Force the minor labels into a format that does not include weekdays or months
                            "millisecond": "mm:ss.SSS",
                            "second": "mm:ss",
                            "minute": "mm:ss",
                            "hour": "HH:mm:ss"
                        }
                    },
                    "start": 0,      # Timeline will start at unix epoch
                    "end": 6000,     # Initial timeline range will end at 1 minute (unix timestamp in milliseconds)
                    "min": 0,        # Restrict timeline navigation, timeline can not be scrolled further to the left than 0 seconds
                    "max": 7000,     # Restrict timeline navigation, timeline can not be scrolled further to the right than 70 seconds
                    "zoomMin": 1000, # Allow zoom in up until the entire timeline spans 1000 milliseconds
                },
                label="Timeline without date labels, with restrictions on navigation and zoom. You can drag and resize items without having to select them first.",
                elem_id=TIMELINE_ID  # This will also make the timeline instance accessible in JavaScript via 'window.visTimelineInstances["your elem_id"]'
            )
            
            table = gr.DataFrame(
                headers=["Item Name", "Start Time", "Duration"],
                label="Timeline Items",
                interactive=False
            )

            generate_audio_button = gr.Button("Generate Audio")
            
            # Event handlers
            dateless_timeline.change(fn=update_table, inputs=[dateless_timeline], outputs=[table])
            dateless_timeline.load(fn=update_table, inputs=[dateless_timeline], outputs=[table])
            generate_audio_button.click(fn=update_audio, inputs=[dateless_timeline], outputs=[audio_output])

            generate_audio_button.click(
                fn=update_audio, 
                inputs=[dateless_timeline], 
                outputs=[audio_output],
            ).then(
                fn=None,
                inputs=None,
                outputs=None,
                js=f'() => initAudioSync("{TIMELINE_ID}", "{AUDIO_ID}", 6000)'
            )
        
        # --- Tab 3: Links to documentation and examples ---
        with gr.Tab("Documentation & More Examples"):
            gr.Markdown("""
                ## Vis.js Timeline Examples  
                A collection of HTML/CSS/JavaScript snippets displaying various properties and use-cases:  
                [https://visjs.github.io/vis-timeline/examples/timeline/](https://visjs.github.io/vis-timeline/examples/timeline/)
                <br><br>
                ## Vis.js Timeline Documentation  
                The official documentation of the timeline:  
                [https://visjs.github.io/vis-timeline/docs/timeline/](https://visjs.github.io/vis-timeline/docs/timeline/)
                <br><br>
                ## Vis.js DataSet Documentation  
                The official documentation of the DataSet model:  
                [https://visjs.github.io/vis-data/data/dataset.html](https://visjs.github.io/vis-data/data/dataset.html)
            """)

if __name__ == "__main__":
    demo.launch(show_api=False)
