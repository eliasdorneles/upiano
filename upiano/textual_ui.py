import os
import fluidsynth
from textual.app import App
from textual.reactive import reactive
from textual.containers import Container
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static
from textual.widgets import Header
from textual.widgets import Footer
from note_render import render_upper_part_key, render_lower_part_key

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

NOTES = [f"{note}{octave}" for octave in [3, 4, 5, 6] for note in SCALE]


def midi_value(note):
    midi_c4 = 60
    return NOTES.index(note) + midi_c4


def start_play_note(note_value, channel=0, velocity=100):
    synthesizer.noteon(channel, note_value, velocity)


def stop_play_note(note_value, channel=0):
    synthesizer.noteoff(channel, note_value)


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
        self.note_midi_value = midi_value(self.note)
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
            start_play_note(self.note_midi_value)
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            stop_play_note(self.note_midi_value)
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
        self.note_midi_value = midi_value(self.note)
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
            start_play_note(self.note_midi_value)
            self.highlight = True

    def on_mouse_up(self, event):
        if event.button == 1:
            stop_play_note(self.note_midi_value)
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


class MyApp(App):
    BINDINGS = [
        ("ctrl-c", "quit", "Quit"),
    ]
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")

    def compose(self):
        # TODO: add a MIDI program selector widget
        yield Header()
        yield Footer()
        with Container(id="main"):
            yield KeyboardWidget()


if __name__ == "__main__":
    synthesizer = fluidsynth.Synth()
    synthesizer.start()

    # TODO: check license of this soundfont
    # http://www.schristiancollins.com/generaluser.php
    soundfont_id = synthesizer.sfload("GeneralUser_GS_v1.471.sf2")
    synthesizer.program_select(0, soundfont_id, 0, 0)

    app = MyApp()
    app.run()
