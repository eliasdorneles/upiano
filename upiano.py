import urwid
import subprocess

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

NOTE_MAP = {
    'A': 'C',
    'W': 'C#',
    'S': 'D',
    'E': 'D#',
    'D': 'E',
    'F': 'F',
    'T': 'F#',
    'G': 'G',
    'Y': 'G#',
    'H': 'A',
    'U': 'A#',
    'J': 'B',
    'K': 'C5',
    'O': 'C#5',
    'L': 'D5',
    'P': 'D#5',
    ';': 'E5',
           }


# play -qn synth {duration} pluck {note}
# fade l 0 {duration} {fadeout_len} reverb vol {vol}

def play_note(note='C', duration=1.5, delay=0, vol=1, verbose=False):
    # requires sox to be installed: http://sox.sf.net
    fadeout_len = duration/2.0
    command = (
        "play -qn synth {duration} pluck {note}"
        " fade l 0 {duration} {fadeout_len} reverb vol {vol}"
    ).format(note=note, duration=duration, fadeout_len=fadeout_len, vol=vol)

    if verbose:
        print(command)

    subprocess.Popen(command.split(), stderr=subprocess.DEVNULL)


def handle_key(key):
    if key.upper() in NOTE_MAP:
        txt.set_text(repr(key))
        play_note(NOTE_MAP[key.upper()])
    elif key.upper() == 'ESC':
        raise urwid.ExitMainLoop()


if __name__ == '__main__':
    txt = urwid.Text(u"Play some piano, mannnnnnn!!!")
    fill = urwid.Filler(txt, 'top')
    loop = urwid.MainLoop(fill, unhandled_input=handle_key)
    loop.run()
