import urwid
from functools import partial

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
                    u'│███\n',
                    u'│███\n',
                    u'│███\n',
                    u'│███\n',
                    u'└─┬─',
                ]
        if normalized_note in ('C', 'E', 'F', 'B'):
            top_right = u'┐' if self.last_corner else ''
            end_right = u'│' if self.last_corner else ''
            bottom_left = u'│' if normalized_note in ('C', 'F') else u'┘'
            return [
                    u'{}──{}\n'.format(edge_char, top_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
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
        top = urwid.Columns([
            ('pack', NoteUpperWidget('C', first_corner=True)),
            ('pack', NoteUpperWidget('C#')),
            ('pack', NoteUpperWidget('D')),
            ('pack', NoteUpperWidget('D#')),
            ('pack', NoteUpperWidget('E')),
            ('pack', NoteUpperWidget('F')),
            ('pack', NoteUpperWidget('F#')),
            ('pack', NoteUpperWidget('G')),
            ('pack', NoteUpperWidget('G#')),
            ('pack', NoteUpperWidget('A')),
            ('pack', NoteUpperWidget('A#')),
            ('pack', NoteUpperWidget('B')),
            ('pack', NoteUpperWidget('C5', last_corner=True)),
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


if __name__ == '__main__':
    widget = KeyboardWidget()
    widget = urwid.Padding(widget)
    widget = urwid.Filler(widget, 'top')
    loop = urwid.MainLoop(widget)
    loop.run()
