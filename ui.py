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

class NoteWidget(urwid.WidgetWrap):
    def __init__(self, note, onclick=None, first_corner=False, last_corner=False, **kw):
        self.onclick = onclick
        self.first_corner = first_corner
        self.last_corner = last_corner
        self.note = note
        self.text = urwid.Text(self._build_text(), wrap='clip')
        super(NoteWidget, self).__init__(self.text)

    def _build_text(self, highlight=False):
        # 'C#'
        if self.first_corner:
            edge_char = u'┌'
        else:
            edge_char = u'┬'
        if self.note.upper() in ('C#', 'D#', 'F#', 'G#', 'A#'):
            return [
                    u'┬───\n',
                    u'│███\n',
                    u'│███\n',
                    u'│███\n',
                    u'│███\n',
                    u'└─┬─\n',
                ]
        if self.note.upper() in ('C', 'E', 'F', 'B'):
            top_right = u'┐' if self.last_corner else ''
            end_right = u'│' if self.last_corner else ''
            bottom_left = u'│' if self.note.upper() in ('C', 'F') else u'┘'
            return [
                    u'{}──{}\n'.format(edge_char, top_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
                    u'│  {}\n'.format(end_right),
                    u'{}  {}\n'.format(bottom_left, end_right),
                ]
        if self.note.upper() in ('D', 'G', 'A'):
            return [
                    u'┬\n',
                    u'│\n',
                    u'│\n',
                    u'│\n',
                    u'│\n',
                    u'┘\n',
                ]
        raise ValueError("Don't know how to draw note %r" % self.note)

#class NoteBottomWidget(
class KeyboardWidget(urwid.WidgetWrap):
    def __init__(self):
        self.columns = urwid.Columns([
                                      ('pack', NoteWidget('C', first_corner=True)),
                                      ('pack', NoteWidget('C#')),
                                      ('pack', NoteWidget('D')),
                                      ('pack', NoteWidget('D#')),
                                      ('pack', NoteWidget('E')),
                                      ('pack', NoteWidget('F')),
                                      ('pack', NoteWidget('F#')),
                                      ('pack', NoteWidget('G')),
                                      ('pack', NoteWidget('G#')),
                                      ('pack', NoteWidget('A')),
                                      ('pack', NoteWidget('A#')),
                                      ('pack', NoteWidget('B')),
                                      ('pack', NoteWidget('c', last_corner=True)),
                                     ])
if __name__== '__main__':
    widget = urwid.Columns([
                                      ('pack', NoteWidget('C', first_corner=True)),
                                      ('pack', NoteWidget('C#')),
                                      ('pack', NoteWidget('D')),
                                      ('pack', NoteWidget('D#')),
                                      ('pack', NoteWidget('E')),
                                      ('pack', NoteWidget('F')),
                                      ('pack', NoteWidget('F#')),
                                      ('pack', NoteWidget('G')),
                                      ('pack', NoteWidget('G#')),
                                      ('pack', NoteWidget('A')),
                                      ('pack', NoteWidget('A#')),
                                      ('pack', NoteWidget('B')),
                                      ('pack', NoteWidget('c', last_corner=True)),
                                  ])
    widget = urwid.Padding(widget)
    widget = urwid.Filler(widget, 'top')
    loop = urwid.MainLoop(widget)
    loop.run()

