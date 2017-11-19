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
            filling = self._build_block('█', 3, highlight)
            return [
                    u'┬───\n',
                    u'│' + filling + '\n',
                    u'│' + filling + '\n',
                    u'│' + filling + '\n',
                    u'│' + filling + '\n',
                    u'└─┬─',
                ]
        if normalized_note in ('C', 'E', 'F', 'B'):
            top_right = u'┐' if self.last_corner else ''
            end_right = u'│' if self.last_corner else ''
            bottom_left = u'│' if normalized_note in ('C', 'F') else u'┘'
            filling = self._build_block(' ', 2, highlight)
            top_edge = u'──'
            if self.last_corner:
                top_edge += u'──'
                filling = self._build_block(' ', 4, highlight)
            return [
                    u'{}{}{}\n'.format(edge_char, top_edge, top_right),
                    u'│' + filling + '{}\n'.format(end_right),
                    u'│' + filling + '{}\n'.format(end_right),
                    u'│' + filling + '{}\n'.format(end_right),
                    u'│' + filling + '{}\n'.format(end_right),
                    u'{}{}{}'.format(bottom_left, filling, end_right),
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


class NoteBottomWidget(urwid.WidgetWrap):
    def __init__(self, which='middle'):
        self.which = which
        self.text = urwid.Text(self._build_text())
        super(NoteBottomWidget, self).__init__(self.text)

    def update(self, highlight=False):
        self.text.set_text(self._build_text(highlight=highlight))

    def _build_text(self, highlight=False):
        if self.which == 'first':
            text = '''
│    
│    
│    
│    
└────
            '''.strip()
        if self.which == 'last':
            text = '''
│    │
│    │
│    │
│    │
┴────┘
            '''.strip()
        else:
            text = '''
│    
│    
│    
│    
┴────
        '''.strip()
        if highlight:
            text = text.replace(' ', '#')
        return text


class KeyboardWidget(urwid.WidgetWrap):
    def __init__(self):
        self.note_widgets = {
            'C':
            (NoteUpperWidget('C', first_corner=True), NoteBottomWidget('first')),
            'C#':
            (NoteUpperWidget('C#'), NoteBottomWidget()),
            'D':
            (NoteUpperWidget('D'), NoteBottomWidget()),
            'D#':
            (NoteUpperWidget('D#'), NoteBottomWidget()),
            'E':
            (NoteUpperWidget('E'), NoteBottomWidget()),
            'F':
            (NoteUpperWidget('F'), NoteBottomWidget()),
            'F#':
            (NoteUpperWidget('F#'), NoteBottomWidget()),
            'G':
            (NoteUpperWidget('G'), NoteBottomWidget()),
            'G#':
            (NoteUpperWidget('G#'), NoteBottomWidget()),
            'A':
            (NoteUpperWidget('A'), NoteBottomWidget()),
            'A#':
            (NoteUpperWidget('A#'), NoteBottomWidget()),
            'B':
            (NoteUpperWidget('B'), NoteBottomWidget()),
            'C5':
            (NoteUpperWidget('C5', last_corner=True), NoteBottomWidget('last')),
        }
        self.available_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#',
                                'A', 'A#', 'B', 'C5']
        top = urwid.Columns([('pack', self.note_widgets[note][0])
                             for note in self.available_notes])
        bottom = urwid.Columns([
            ('pack', self.note_widgets[note][1])
            for note in self.available_notes
            if '#' not in note])
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
