from dataclasses import dataclass
from textual.message import Message
from textual.reactive import reactive
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static
from upiano.note_render import render_upper_part_key, render_lower_part_key
from upiano import midi


"""
┌──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┬──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┐

│  │███││███│  │  │███││███││███│  │  │███││███│  │  │███││███││███│  │
│  │███││███│  │  │███││███││███│  │  │███││███│  │  │███││███││███│  │
│  │███││███│  │  │███││███││███│  │  │███││███│  │  │███││███││███│  │
│  │███││███│  │  │███││███││███│  │  │███││███│  │  │███││███││███│  │
│  │█W█││█E█│  │  │█T█││█Y█││█U█│  │  │█O█││█P█│  │  │█]█││███││███│  │
│  │███││███│  │  │███││███││███│  │  │███││███│  │  │███││███││███│  │

│  └─┬─┘└─┬─┘  │  └─┬─┘└─┬─┘└─┬─┘  │  └─┬─┘└─┬─┘  │  └─┬─┘└─┬─┘└─┬─┘  │

│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│ A  │ S  │ D  │ F  │ G  │  H │ J  │ K  │ L  │ ;  │ '  │ \  │    │    │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│ C  │ D  │ E  │    │    │  A │ B  │ c  │ d  │ e  │    │    │    │    │

└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

"""


KEYMAP_CHAR_TO_INDEX = {
    "A": 0,
    "W": 1,
    "S": 2,
    "E": 3,
    "D": 4,
    "F": 5,
    "T": 6,
    "G": 7,
    "Y": 8,
    "H": 9,
    "U": 10,
    "J": 11,
    "K": 12,
    "O": 13,
    "L": 14,
    "P": 15,
    ";": 16,
    "'": 17,
}


SCALE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTES = [f"{note}{octave}" for octave in [3, 4, 5, 6, 7] for note in SCALE]


@dataclass
class Key:
    note: str
    midi_value: int
    position: int


VIRTUAL_KEYS: list[Key] = [
    Key(note, midi.note_to_midi(note), index) for index, note in enumerate(NOTES)
]


class KeyDown(Message):
    def __init__(self, key: Key):
        super().__init__()
        self.key = key


class KeyUp(Message):
    def __init__(self, key: Key):
        super().__init__()
        self.key = key


class KeyUpperPart(Static):
    highlight = reactive(False)

    DEFAULT_CSS = """
    KeyUpperPart {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, note_index, **kwargs):
        super().__init__(**kwargs)
        self._content_width = 0
        self.key = VIRTUAL_KEYS[note_index]
        self.highlight = False

    def watch_highlight(self, value):
        rendered = render_upper_part_key(
            self.key.note,
            first_corner=self.key.position == 0,
            last_corner=self.key.position == len(NOTES) - 1,
            use_rich=True,
            highlight=value,
        )
        self._content_width = len(rendered.splitlines()[0])
        self.update(rendered)

    def get_content_height(self, *args, **kwargs):
        return 8

    def get_content_width(self, *args, **kwargs):
        return self._content_width

    def on_mouse_down(self, event):
        if event.button == 1:
            self.post_message(KeyDown(self.key))
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            self.post_message(KeyUp(self.key))
            self.highlight = False


class KeyLowerPart(Static):
    highlight = reactive(False)

    DEFAULT_CSS = """
    KeyLowerPart {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, note_index, **kwargs):
        super().__init__(**kwargs)
        self.key = VIRTUAL_KEYS[note_index]
        self.highlight = False

    def watch_highlight(self, value):
        self.update(
            render_lower_part_key(
                is_first=self.key.position == 0,
                is_last=self.key.position == len(NOTES) - 1,
                use_rich=True,
                highlight=value,
            )
        )

    def get_content_height(self, *args, **kwargs):
        return 8

    def get_content_width(self, *args, **kwargs):
        if self.key.position == len(NOTES) - 1:
            return 6
        return 0 if "#" in self.key.note else 5

    # TODO: when mouse moves out of the widget, the note should stop playing,
    # but only if it's started by this widget -- e.g., if it started by a key press event,
    # it should continue playing until the key is released
    # TODO: highlight on/off messages should be sent to parent widget, so that
    # corresponding uppper/lower part of the key can be highlighted
    def on_mouse_down(self, event):
        if event.button == 1:
            self.post_message(KeyDown(self.key))
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            self.post_message(KeyUp(self.key))
            self.highlight = False


class KeyboardWidget(Widget):
    can_focus = True

    DEFAULT_CSS = """
    KeyboardWidget Horizontal {
        height: 8;
    }
    """

    def __init__(self, note_on, note_off, **kwargs):
        super().__init__(**kwargs)
        self.note_upper_widgets = [
            KeyUpperPart(note_index=i) for i in range(len(NOTES))
        ]
        self.note_lower_widgets = [
            KeyLowerPart(note_index=i) for i in range(len(NOTES))
        ]
        self.note_on = note_on
        self.note_off = note_off

    def compose(self):
        with Horizontal():
            for w in self.note_upper_widgets:
                yield w
        with Horizontal():
            for w in self.note_lower_widgets:
                yield w

    def handle_key_down(self, key: Key):
        self.note_on(key.midi_value)
        self.note_upper_widgets[key.position].highlight = True
        self.note_lower_widgets[key.position].highlight = True

    def handle_key_up(self, key: Key):
        self.note_off(key.midi_value)
        self.note_upper_widgets[key.position].highlight = False
        self.note_lower_widgets[key.position].highlight = False

    def on_key_down(self, event):
        self.handle_key_down(event.key)

    def on_key_up(self, event):
        self.handle_key_up(event.key)
