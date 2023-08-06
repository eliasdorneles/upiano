from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import Switch


class NumericUpDownControl(Widget):
    DEFAULT_CSS = """
    NumericUpDownControl {
        height: 5;
    }
    NumericUpDownControl Button {
        min-width: 5;
    }

    NumericUpDownControl .value-holder {
        min-width: 2;
        border: thick $primary;
        text-style: bold;
        padding: 0 1;
        text-align: right;
    }

    NumericUpDownControl .value-holder.modified {
        border: thick $secondary;
    }
    """

    value = reactive(0)

    def __init__(self, label, watch_value=None, min_value=-11, max_value=11, id=""):
        id = id or label.lower().replace(" ", "-").replace(":", "")
        super().__init__(id=id)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.watch_value = watch_value

    def compose(self):
        yield Label(self.label)
        with Horizontal():
            yield Button("⬇️ ", id="{}-down".format(self.id))
            yield Label("0", id="{}-value".format(self.id), classes="value-holder")
            yield Button("⬆️ ", id="{}-up".format(self.id))

    def on_button_pressed(self, event):
        if event.button.id == "{}-down".format(self.id):
            if self.value > self.min_value:
                self.value -= 1
        elif event.button.id == "{}-up".format(self.id):
            if self.value < self.max_value:
                self.value += 1

        label = self.query_one("#{}-value".format(self.id), Label)
        label.update(str(self.value))
        if self.value == 0:
            label.remove_class("modified")
        else:
            label.add_class("modified")


class LabeledSwitch(Widget):
    value = reactive(False)

    def __init__(self, label, watch_value=None, id=""):
        id = id or label.lower().replace(" ", "-").replace(":", "")
        super().__init__(id=id)
        self.label = label
        self.watch_value = watch_value

    def compose(self):
        yield Label(self.label)
        yield Switch(id="{}-switch".format(self.id))

    def on_switch_changed(self, event):
        self.value = event.value

    def toggle(self):
        self.query_one(Switch).toggle()
