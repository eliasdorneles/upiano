import os
from functools import partial
from dataclasses import dataclass
from textual.app import App
from textual.reactive import reactive
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.containers import Grid
from textual.widget import Widget
from textual.widgets import Header
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import Button
from upiano.keyboard_ui import KeyboardWidget, KEYMAP_CHAR_TO_INDEX, VIRTUAL_KEYS
from upiano import midi


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


def tranposed_note_on(note_value: int):
    synthesizer.note_on(transpose_note(note_value), velocity=100)


def transposed_note_off(note_value: int):
    synthesizer.note_off(transpose_note(note_value))


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
        self.keyboard_widget = KeyboardWidget(
            note_on=tranposed_note_on,
            note_off=transposed_note_off,
        )
        with Container(id="main"):
            with Vertical(id="instrument-controls"):
                yield InstrumentSelector()
                with Grid():
                    yield OctaveControls()
                    yield TranspositionControls()
            yield self.keyboard_widget

    def on_key(self, event):
        # TODO: since the terminal doesn't have a key up and down events, we'll
        # have to come up with a way emulate them. Maybe by a set_interval
        # function, which will keep track of the time we get each "key pressed"
        # event and compare the time of current event to the previous one. If
        # the difference is too big, we'll assume that the key was released.
        key = event.key.upper()
        note_index = KEYMAP_CHAR_TO_INDEX.get(key)
        if note_index is not None:
            virtual_key = VIRTUAL_KEYS[note_index]
            self.keyboard_widget.handle_key_down(virtual_key)
            self.set_timer(
                1.5, partial(self.keyboard_widget.handle_key_up, virtual_key)
            )


if __name__ == "__main__":
    synthesizer = midi.MidiSynth()

    app = MyApp()
    app.run()
