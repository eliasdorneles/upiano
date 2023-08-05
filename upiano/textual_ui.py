import os
from dataclasses import dataclass
from textual.app import App
from textual.reactive import reactive
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.containers import Grid
from textual.widget import Widget
from textual.widgets import Static
from textual.widgets import Header
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import Button
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

SCALE = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]

NOTES = [f"{note}{octave}" for octave in [3, 4, 5, 6, 7] for note in SCALE]

SOUNDFONTS_DIR = os.path.join(os.path.dirname(__file__), "soundfonts")


@dataclass
class KeyboardPlayingSettings:
    octave: int = 0
    transpose: int = 0


PLAY_SETTINGS = KeyboardPlayingSettings()


def transpose_note(note_value: int):
    """
    Transpose a note value by the current settings (transpose and octave)
    """
    return note_value + PLAY_SETTINGS.transpose + PLAY_SETTINGS.octave * 12


class NoteUpperWidget(Static):
    highlight = reactive(False)

    DEFAULT_CSS = """
    NoteUpperWidget {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, note_index, **kwargs):
        super().__init__(**kwargs)
        self._content_width = 0
        self.note_index = note_index
        self.note = NOTES[note_index]
        self.note_midi_value = midi.note_to_midi(self.note)
        self.highlight = False

    def watch_highlight(self, value):
        rendered = render_upper_part_key(
            NOTES[self.note_index],
            first_corner=self.note_index == 0,
            last_corner=self.note_index == len(NOTES) - 1,
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
            synthesizer.note_on(transpose_note(self.note_midi_value))
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            synthesizer.note_off(transpose_note(self.note_midi_value))
            self.highlight = False


class NoteLowerWidget(Static):
    highlight = reactive(False)

    DEFAULT_CSS = """
    NoteLowerWidget {
        width: auto;
        height: 8;
    }
    """

    def __init__(self, note_index, **kwargs):
        super().__init__(**kwargs)
        self.note_index = note_index
        self.note = NOTES[note_index]
        self.note_midi_value = midi.note_to_midi(self.note)
        self.highlight = False

    def watch_highlight(self, value):
        self.update(
            render_lower_part_key(
                is_first=self.note_index == 0,
                is_last=self.note_index == len(NOTES) - 1,
                use_rich=True,
                highlight=value,
            )
        )

    def get_content_height(self, *args, **kwargs):
        return 8

    def get_content_width(self, *args, **kwargs):
        if self.note_index == len(NOTES) - 1:
            return 6
        return 0 if "#" in self.note else 5

    # TODO: when mouse moves out of the widget, the note should stop playing,
    # but only if it's started by this widget -- e.g., if it started by a key press event,
    # it should continue playing until the key is released
    # TODO: highlight on/off messages should be sent to parent widget, so that
    # corresponding uppper/lower part of the key can be highlighted
    def on_mouse_down(self, event):
        if event.button == 1:
            synthesizer.note_on(transpose_note(self.note_midi_value))
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            synthesizer.note_off(transpose_note(self.note_midi_value))
            self.highlight = False


class KeyboardWidget(Widget):
    can_focus = True

    DEFAULT_CSS = """
    KeyboardWidget Horizontal {
        height: 8;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_upper_widgets = [
            NoteUpperWidget(note_index=i) for i in range(len(NOTES))
        ]
        self.note_lower_widgets = [
            NoteLowerWidget(note_index=i) for i in range(len(NOTES))
        ]

    def compose(self):
        with Horizontal():
            for w in self.note_upper_widgets:
                yield w
        with Horizontal():
            for w in self.note_lower_widgets:
                yield w

    # TODO: on click, play note
    # TODO: on key press, play note according to keymap
    def on_key(self, event):
        key = event.key.upper()
        print("key pressed", key)
        if key in NOTES:
            note_index = NOTES.index(key)
            print(f"Pressed {key}")
            self.note_upper_widgets[note_index].highlight = True
            self.note_lower_widgets[note_index].highlight = True


class InstrumentSelector(Widget):
    def __init__(self):
        super().__init__()
        self._instrument_options = [
            (instrument, i)
            for i, instrument in enumerate(midi.GENERAL_MIDI_INSTRUMENTS)
        ]

    def compose(self):
        yield Label("Instrument:")
        yield Select(
            prompt="Select instrument",
            allow_blank=False,
            options=self._instrument_options,
            value=0,
        )

    def on_select_changed(self, event):
        if event.value is not None:
            synthesizer.select_midi_program(event.value)


class TranspositionControls(Widget):
    current_transposition = reactive(0)

    def __init__(self):
        super().__init__()
        self.current_transposition = PLAY_SETTINGS.transpose

    def compose(self):
        yield Label("Transpose:")
        with Horizontal():
            yield Button("⬇️ ", id="transpose-down")
            yield Label("0", id="transpose-value", classes="value-holder")
            yield Button("⬆️ ", id="transpose-up")

    def on_button_pressed(self, event):
        if event.button.id == "transpose-down":
            self.current_transposition -= 1
        elif event.button.id == "transpose-up":
            self.current_transposition += 1
        label = self.query_one("#transpose-value", Label)
        label.update(str(self.current_transposition))
        if self.current_transposition == 0:
            label.remove_class("modified")
        else:
            label.add_class("modified")

    def watch_current_transposition(self, value):
        PLAY_SETTINGS.transpose = value


class OctaveControls(Widget):
    current_octave = reactive(0)

    def __init__(self):
        super().__init__()
        self.current_octave = PLAY_SETTINGS.octave

    def compose(self):
        yield Label("Octave:")
        with Horizontal():
            yield Button("⬇️ ", id="octave-down")
            yield Label("0", id="octave-value", classes="value-holder")
            yield Button("⬆️ ", id="octave-up")

    def on_button_pressed(self, event):
        if event.button.id == "octave-down":
            self.current_octave -= 1
        elif event.button.id == "octave-up":
            self.current_octave += 1
        label = self.query_one("#octave-value", Label)
        label.update(str(self.current_octave))
        if self.current_octave == 0:
            label.remove_class("modified")
        else:
            label.add_class("modified")

    def watch_current_octave(self, value):
        PLAY_SETTINGS.octave = value


class MyApp(App):
    BINDINGS = [
        ("ctrl-c", "quit", "Quit"),
    ]
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")
    TITLE = "UPiano"
    SUB_TITLE = "A piano in your terminal"

    def compose(self):
        yield Header()
        yield Footer()
        with Container(id="main"):
            with Vertical(id="instrument-controls"):
                yield InstrumentSelector()
                with Grid():
                    yield OctaveControls()
                    yield TranspositionControls()
            yield KeyboardWidget()


if __name__ == "__main__":
    synthesizer = midi.MidiSynth()

    app = MyApp()
    app.run()
