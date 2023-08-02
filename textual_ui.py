from textual.app import App
from textual.reactive import reactive
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


"""
┌──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┬──┬───┬┬───┬──┬──┬───┬┬───┬┬───┬──┐
│  │   ││   │  │  │   ││   ││   │  │  │   ││   │  │  │   ││   ││   │  │
│  │   ││   │  │  │   ││   ││   │  │  │   ││   │  │  │   ││   ││   │  │
│  │   ││   │  │  │   ││   ││   │  │  │   ││   │  │  │   ││   ││   │  │
│  │   ││   │  │  │   ││   ││   │  │  │   ││   │  │  │   ││   ││   │  │
│  │   ││   │  │  │   ││   ││   │  │  │   ││   │  │  │   ││   ││   │  │
│  ╰─┬─╯╰─┬─╯  │  ╰─┬─╯╰─┬─╯╰─┬─╯  │  ╰─┬─┘╰─┬─╯  │  ╰─┬─╯╰─┬─╯╰─┬─╯  │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │    │    │    │    │    │    │
╰────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────╯

"""


NOTES = [
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
    "F5",
    "F#5",
    "G5",
    "G#5",
    "A5",
    "A#5",
    "B5",
    "C6",
    "C#6",
    "D6",
    "D#6",
    "E6",
]


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

    def compose(self):
        yield Header()
        yield Footer()
        yield KeyboardWidget()


if __name__ == "__main__":
    app = MyApp()
    app.run()
