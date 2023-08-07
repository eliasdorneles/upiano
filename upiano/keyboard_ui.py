from dataclasses import dataclass
from functools import partial

from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from upiano import midi
from upiano.note_render import render_lower_part_key
from upiano.note_render import render_upper_part_key

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


class KeyDown(Message):
    def __init__(self, key: Key):
        super().__init__()
        self.key = key


class KeyUp(Message):
    def __init__(self, key: Key):
        super().__init__()
        self.key = key


@dataclass
class MouseStatus:
    pressed: bool = False
    black_key_pressed: bool = False


MOUSE_STATUS = MouseStatus()


class KeyPartMouseMixin:
    def on_mouse_down(self, event):
        MOUSE_STATUS.pressed = True
        MOUSE_STATUS.black_key_pressed = "#" in self.key.note
        if event.button == 1:
            self.post_message(KeyDown(self.key))
            self.highlight = True

    def on_mouse_up(self, event):
        MOUSE_STATUS.pressed = False
        MOUSE_STATUS.black_key_pressed = False
        if event.button == 1:
            self.post_message(KeyUp(self.key))
            self.highlight = False

    def on_leave(self, event):
        self.highlight = False
        self.post_message(KeyUp(self.key))

    def on_enter(self, event):
        if MOUSE_STATUS.pressed:
            if MOUSE_STATUS.black_key_pressed and "#" not in self.key.note:
                return
            self.post_message(KeyDown(self.key))
            self.highlight = True


class KeyUpperPart(Static, KeyPartMouseMixin):
    highlight = reactive(False)

    DEFAULT_CSS = """
    KeyUpperPart {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self._content_width = 0
        self.key = key
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


class KeyLowerPart(Static, KeyPartMouseMixin):
    highlight = reactive(False)

    DEFAULT_CSS = """
    KeyLowerPart {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.key = key
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


class KeyboardWidget(Widget):
    can_focus = True

    DEFAULT_CSS = """
    KeyboardWidget Horizontal {
        height: 8;
    }
    """

    def __init__(self, note_on, note_off, **kwargs):
        super().__init__(**kwargs)
        self.virtual_keys: list[Key] = [
            Key(note, midi.note_to_midi(note), index)
            for index, note in enumerate(NOTES)
        ]

        self.note_upper_widgets = [KeyUpperPart(key) for key in self.virtual_keys]
        self.note_lower_widgets = [KeyLowerPart(key) for key in self.virtual_keys]
        self.note_on = note_on
        self.note_off = note_off

        # Add a dictionary to keep track of which keys are currently being pressed
        self.keys_pressed = {}

    def compose(self):
        with Horizontal():
            for w in self.note_upper_widgets:
                yield w
        with Horizontal():
            for w in self.note_lower_widgets:
                yield w

    def handle_key_down(self, key: Key):
        # Only trigger note_on if the key was not already being pressed
        if not self.keys_pressed.get(key.midi_value):
            self.note_on(key.midi_value)
            self.note_upper_widgets[key.position].highlight = True
            self.note_lower_widgets[key.position].highlight = True
            self.keys_pressed[key.midi_value] = True

    def handle_key_up(self, key: Key):
        # Only trigger note_off if the key was being pressed
        if self.keys_pressed.get(key.midi_value):
            self.note_off(key.midi_value)
            self.note_upper_widgets[key.position].highlight = False
            self.note_lower_widgets[key.position].highlight = False
            self.keys_pressed[key.midi_value] = False

    def on_key_down(self, event):
        if hasattr(event, 'key'):
            key_value = event.key
            key_index = KEYMAP_CHAR_TO_INDEX.get(key_value.upper())
            if key_index is not None:
                self.handle_key_down(self.virtual_keys[key_index])



    def play_key(self, key_index):
        virtual_key = self.virtual_keys[key_index]
        self.handle_key_down(virtual_key)
        self.set_timer(0.3, partial(self.handle_key_up, virtual_key))
