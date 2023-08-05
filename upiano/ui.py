import asyncio
import urwid
from functools import partial
from upiano.piano import play_note, NOTE_MAP
from upiano.note_render import render_upper_part_key
from upiano.note_render import render_lower_part_key

"""
This is what we're gonna builddddd....
┌──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┬──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┐
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


class NoteUpperWidget(urwid.WidgetWrap):
    def __init__(self, note, onclick=None, first_corner=False, last_corner=False, **kw):
        self.onclick = onclick
        self.first_corner = first_corner
        self.last_corner = last_corner
        self.note = note
        self.text = urwid.Text(self._build_text(), wrap="clip")
        super(NoteUpperWidget, self).__init__(self.text)

    def update(self, highlight=False):
        self.text.set_text(self._build_text(highlight=highlight))

    def _build_text(self, highlight=False):
        return render_upper_part_key(
            self.note, self.first_corner, self.last_corner, highlight=highlight
        )


class NoteBottomWidget(urwid.WidgetWrap):
    def __init__(self, which="middle"):
        self.which = which
        self.text = urwid.Text(self._build_text())
        super(NoteBottomWidget, self).__init__(self.text)

    def update(self, highlight=False):
        self.text.set_text(self._build_text(highlight=highlight))

    def _build_text(self, highlight=False):
        return render_lower_part_key(
            is_first=self.which == "first",
            is_last=self.which == "last",
            highlight=highlight,
        )


class KeyboardWidget(urwid.WidgetWrap):
    def __init__(self):
        self.note_widgets = {
            "C": (NoteUpperWidget("C", first_corner=True), NoteBottomWidget("first")),
            "C#": (NoteUpperWidget("C#"), NoteBottomWidget()),
            "D": (NoteUpperWidget("D"), NoteBottomWidget()),
            "D#": (NoteUpperWidget("D#"), NoteBottomWidget()),
            "E": (NoteUpperWidget("E"), NoteBottomWidget()),
            "F": (NoteUpperWidget("F"), NoteBottomWidget()),
            "F#": (NoteUpperWidget("F#"), NoteBottomWidget()),
            "G": (NoteUpperWidget("G"), NoteBottomWidget()),
            "G#": (NoteUpperWidget("G#"), NoteBottomWidget()),
            "A": (NoteUpperWidget("A"), NoteBottomWidget()),
            "A#": (NoteUpperWidget("A#"), NoteBottomWidget()),
            "B": (NoteUpperWidget("B"), NoteBottomWidget()),
            "C5": (NoteUpperWidget("C5"), NoteBottomWidget()),
            "C#5": (NoteUpperWidget("C#5"), NoteBottomWidget()),
            "D5": (NoteUpperWidget("D5"), NoteBottomWidget()),
            "D#5": (NoteUpperWidget("C#5"), NoteBottomWidget()),
            "E5": (NoteUpperWidget("E5", last_corner=True), NoteBottomWidget("last")),
        }
        self.available_notes = [
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
            "C5",
            "C#5",
            "D5",
            "D#5",
            "E5",
        ]
        top = urwid.Columns(
            [("pack", self.note_widgets[note][0]) for note in self.available_notes]
        )
        bottom = urwid.Columns(
            [
                ("pack", self.note_widgets[note][1])
                for note in self.available_notes
                if "#" not in note
            ]
        )
        self.pile = urwid.Pile([top, bottom])
        super(KeyboardWidget, self).__init__(self.pile)

    def play(self, loop, note):
        if note not in self.available_notes:
            return
        self.blink(note, loop)
        play_note(note)

    def blink(self, note, loop):
        upper_widget, bottom_widget = self.note_widgets[note]
        upper_widget.update(highlight=True)
        bottom_widget.update(highlight=True)
        loop.call_later(0.8, partial(upper_widget.update, highlight=False))
        loop.call_later(0.8, partial(bottom_widget.update, highlight=False))


def handle_key(key):
    if key.upper() in NOTE_MAP:
        note = NOTE_MAP[key.upper()]
        KEYBOARD_WIDGET.play(asyncio_loop, note)
    elif key.upper() == "ESC":
        raise urwid.ExitMainLoop()


if __name__ == "__main__":
    KEYBOARD_WIDGET = widget = KeyboardWidget()
    widget = urwid.Padding(widget)
    widget = urwid.Filler(widget, "top")

    asyncio_loop = asyncio.get_event_loop()
    evl = urwid.AsyncioEventLoop(loop=asyncio_loop)
    urwid_loop = urwid.MainLoop(widget, event_loop=evl, unhandled_input=handle_key)
    urwid_loop.run()
