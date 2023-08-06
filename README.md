# UPiano

A Piano in your terminal.


## Screenshot

 ![](./screenshot-upiano.png)


## How to run

Install via pip:

    pip install upiano

And then run:

    upiano

Make sure your terminal window is big enough.
The wider you can make it, the more keys you'll have! 🎹 😀


## Powered by

* [Python](https://www.python.org) 🐍
* [Textual](https://textual.textualize.io/)
* [FluidSynth](https://github.com/FluidSynth/fluidsynth)
* [pyFluidSynth](https://github.com/nwhitehead/pyfluidsynth)

Made with ❤️  by Elias Dorneles


## History

This started as a fun pairing project by friends
[Elias](https://github.com/eliasdorneles) and
[Nandaja](https://github.com/nandajavarma) around 2017, after they had
finished their [Recurse Center](https://recurse.com) retreat and were missing
hacking together.

They had fun building a small terminal piano app using
[urwid](https://urwid.org) for the user interface and playing notes by spawning
[sox](https://sox.sourceforge.net) subprocesses. This version is available in
the project source code, if you have urwid and sox installed, you can try it by
running: `python upiano/legacy.py`.

Fast-forward to 2023, Elias attended EuroPython and learned the
[Textual](https://textual.textualize.io) library there, got excited about
terminal apps again and decided to reboot this project using the newly acquired
knowledge, package and distribute it, and add to the fun by plugging a true
synthesizer to it, and playing with its controls.


### Changelog:

* **v0.1.0**
    * first version released to PyPI, already using Textual
* **v0.1.1**
    * added sustain
    * fix mouse handling, and allow playing by "swiping" over keys
