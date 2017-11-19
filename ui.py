import asyncio
import urwid
from functools import partial
from upiano import play_note, NOTE_MAP

'''
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
'''


class NoteUpperWidget(urwid.WidgetWrap):
    def __init__(self, note, onclick=None, first_corner=False, last_corner=False, **kw):
        self.onclick = onclick
        self.first_corner = first_corner
        self.last_corner = last_corner
        self.note = note
        self.text = urwid.Text(self._build_text(), wrap='clip')
        super(NoteUpperWidget, self).__init__(self.text)

    def _build_block(self, character, size, highlight=False):
        if highlight:
            return '#' * size
        return character * size

    def blink(self, loop):
        self.update(highlight=True)
        loop.call_later(0.8, partial(self.update, highlight=False))

    def update(self, highlight=False):
        self.text.set_text(self._build_text(highlight=highlight))

    def _build_text(self, highlight=False):
        # 'C#'
        if self.first_corner:
            edge_char = u'┌'
        else:
            edge_char = u'┬'
        normalized_note = self.note.replace('5', '').upper()
        if normalized_note in ('C#', 'D#', 'F#', 'G#', 'A#'):
            return [
                    u'┬───\n',
                    u'│' + self._build_block('█', 3, highlight) + '\n',
                    u'│' + self._build_block('█', 3, highlight) + '\n',
                    u'│' + self._build_block('█', 3, highlight) + '\n',
                    u'│' + self._build_block('█', 3, highlight) + '\n',
                    u'└─┬─',
                ]
        if normalized_note in ('C', 'E', 'F', 'B'):
            top_right = u'┐' if self.last_corner else ''
            end_right = u'│' if self.last_corner else ''
            bottom_left = u'│' if normalized_note in ('C', 'F') else u'┘'
            return [
                    u'{}──{}\n'.format(edge_char, top_right),
                    u'│' + self._build_block(' ', 2, highlight) + '{}\n'.format(end_right),
                    u'│' + self._build_block(' ', 2, highlight) + '{}\n'.format(end_right),
                    u'│' + self._build_block(' ', 2, highlight) + '{}\n'.format(end_right),
                    u'│' + self._build_block(' ', 2, highlight) + '{}\n'.format(end_right),
                    u'{}  {}'.format(bottom_left, end_right),
                ]
        if normalized_note in ('D', 'G', 'A'):
            return [
                    u'┬\n',
                    u'│\n',
                    u'│\n',
                    u'│\n',
                    u'│\n',
                    u'┘',
                ]
        raise ValueError("Don't know how to draw note %r" % self.note)


class KeyboardWidget(urwid.WidgetWrap):
    def __init__(self):
        self.note_widgets ={
            'C': NoteUpperWidget('C', first_corner=True),
            'C#': NoteUpperWidget('C#'),
            'D': NoteUpperWidget('D'),
            'D#': NoteUpperWidget('D#'),
            'E': NoteUpperWidget('E'),
            'F': NoteUpperWidget('F'),
            'F#': NoteUpperWidget('F#'),
            'G': NoteUpperWidget('G'),
            'G#': NoteUpperWidget('G#'),
            'A': NoteUpperWidget('A'),
            'A#': NoteUpperWidget('A#'),
            'B': NoteUpperWidget('B'),
            'C5': NoteUpperWidget('C5', last_corner=True),
        }
        top = urwid.Columns([
            ('pack', self.note_widgets['C']),
            ('pack', self.note_widgets['C#']),
            ('pack', self.note_widgets['D']),
            ('pack', self.note_widgets['D#']),
            ('pack', self.note_widgets['E']),
            ('pack', self.note_widgets['F']),
            ('pack', self.note_widgets['F#']),
            ('pack', self.note_widgets['G']),
            ('pack', self.note_widgets['G#']),
            ('pack', self.note_widgets['A']),
            ('pack', self.note_widgets['A#']),
            ('pack', self.note_widgets['B']),
            ('pack', self.note_widgets['C5']),
        ])
        bottom = urwid.Text(['''
│    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │
└────┴────┴────┴────┴────┴────┴────┴────┘
'''.strip()
        ])
        self.pile = urwid.Pile([top, bottom])
        super(KeyboardWidget, self).__init__(self.pile)

    def play(self, loop, note):
        self.note_widgets[note].blink(loop)
        play_note(note)


def handle_key(key):
    if key.upper() in NOTE_MAP:
        note = NOTE_MAP[key.upper()]
        KEYBOARD_WIDGET.play(asyncio_loop, note)
    elif key.upper() == 'ESC':
        raise urwid.ExitMainLoop()


if __name__ == '__main__':
    KEYBOARD_WIDGET = widget = KeyboardWidget()
    widget = urwid.Padding(widget)
    widget = urwid.Filler(widget, 'top')

    asyncio_loop = asyncio.get_event_loop()
    asyncio_loop.call_later(3, KEYBOARD_WIDGET.play, asyncio_loop, 'E')
    evl = urwid.AsyncioEventLoop(loop=asyncio_loop)
    urwid_loop = urwid.MainLoop(widget, event_loop=evl, unhandled_input=handle_key)
    urwid_loop.run()
