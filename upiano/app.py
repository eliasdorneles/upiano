"""
UPiano - A piano in your terminal
"""

import os
from dataclasses import dataclass

from textual.app import App
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Label
from textual.widgets import Select

from upiano import midi
from upiano.keyboard_ui import KEYMAP_CHAR_TO_INDEX
from upiano.keyboard_ui import KeyboardWidget
from upiano.widgets import LabeledSwitch
from upiano.widgets import LabeledSlider
from upiano.widgets import NumericUpDownControl

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
        yield Label("Instrument")
        yield Select(
            prompt="Select instrument",
            allow_blank=False,
            options=self._instrument_options,
            value=0,
        )

    def on_select_changed(self, event):
        if event.value is not None:
            synthesizer.select_midi_program(event.value)


def tranposed_note_on(note_value: int):
    synthesizer.note_on(transpose_note(note_value), velocity=100)


def transposed_note_off(note_value: int):
    synthesizer.note_off(transpose_note(note_value))


class MyApp(App):
    BINDINGS = [
        ("ctrl-c", "quit", "Quit"),
        ("insert", "toggle_sustain", "Toggle sustain"),
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
            with Container(id="controls"):
                yield InstrumentSelector()
                yield NumericUpDownControl(
                    "Transpose",
                    lambda value: setattr(PLAY_SETTINGS, "transpose", value),
                    min_value=-11,
                    max_value=11,
                )
                yield NumericUpDownControl(
                    "Octave",
                    lambda value: setattr(PLAY_SETTINGS, "octave", value),
                    min_value=-3,
                    max_value=3,
                )
                yield LabeledSwitch(
                    "Sustain",
                    lambda value: synthesizer.set_sustain(100 if value else 0),
                )
                yield LabeledSlider(
                    "Volume",
                    lambda value: synthesizer.set_volume(value),
                )
                yield LabeledSlider(
                    "Reverb",
                    lambda value: synthesizer.set_reverb(value),
                    value=0,
                )
                yield LabeledSlider(
                    "Chorus",
                    lambda value: synthesizer.set_chorus(value),
                    value=0,
                )
            yield self.keyboard_widget

    def action_toggle_sustain(self):
        self.query_one(LabeledSwitch).toggle()

    def on_key(self, event):
        # TODO: since the terminal doesn't have a key up and down events, we'll
        # have to come up with a way emulate them. Maybe by a set_interval
        # function, which will keep track of the time we get each "key pressed"
        # event and compare the time of current event to the previous one. If
        # the difference is too big, we'll assume that the key was released.
        key = event.key.upper()
        note_index = KEYMAP_CHAR_TO_INDEX.get(key)
        if note_index is not None:
            self.keyboard_widget.play_key(note_index)


def run_app(args):
    global synthesizer
    synthesizer = midi.MidiSynth()

    MyApp().run()


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    args = parser.parse_args()
    run_app(args)


if __name__ == "__main__":
    main()
