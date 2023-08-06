import re


def render_upper_part_key(
    note,
    first_corner: bool = False,
    last_corner: bool = False,
    highlight=False,
    use_rich=False,
):
    """
    Return a list of strings that represent the note in the upper part of the
    piano keyboard.
    """
    normalized_note = re.sub("[0-9]", "", note).upper()

    if normalized_note in ("C#", "D#", "F#", "G#", "A#"):
        filling = ("#" if highlight else "█") * 3
        if use_rich:
            filling = " " * len(filling)
            filling = "[on {}]{}[/]".format(
                "red" if highlight else "transparent", filling
            )

        return "\n".join(
            [
                "┬───",
                "│" + filling,
                "│" + filling,
                "│" + filling,
                "│" + filling,
                "│" + filling,
                "│" + filling,
                "└─┬─",
            ]
        )

    if normalized_note in ("D", "G", "A"):
        return "\n".join(
            [
                "┬",
                "│",
                "│",
                "│",
                "│",
                "│",
                "│",
                "╯",
            ]
        )

    if normalized_note in ("C", "E", "F", "B"):
        top_right = "┐" if last_corner else ""
        end_right = "│" if last_corner else ""
        bottom_left = "│" if normalized_note in ("C", "F") else "╯"
        fill_char = "#" if highlight else " "
        filling = fill_char * 2
        top_edge = "──"

        if last_corner and normalized_note == "C":
            top_edge += "──"
            filling = fill_char * 4

        if use_rich:
            filling = " " * len(filling)
            filling = "[on {}]{}[/]".format("red" if highlight else "white", filling)

        edge_char = "┌" if first_corner else "┬"
        return "\n".join(
            [
                "{}{}{}".format(edge_char, top_edge, top_right),
                "│{}{}".format(filling, end_right),
                "│{}{}".format(filling, end_right),
                "│{}{}".format(filling, end_right),
                "│{}{}".format(filling, end_right),
                "│{}{}".format(filling, end_right),
                "│{}{}".format(filling, end_right),
                "{}{}{}".format(bottom_left, filling, end_right),
            ]
        )

    raise ValueError("Don't know how to draw note %r" % note)


def render_lower_part_key(
    is_first=False, is_last=False, highlight=False, use_rich=False
):
    if is_first and is_last:
        raise ValueError("Can't be first and last at the same time")

    if is_first:
        text = """
│    
│    
│    
│    
└────
        """.strip()
    elif is_last:
        text = """
│    │
│    │
│    │
│    │
┴────┘
        """.strip()
    else:
        text = """
│    
│    
│    
│    
┴────
        """.strip()

    if use_rich:
        color = "red" if highlight else "white"
        text = text.replace("    ", f"[on {color}]    [/]")
    else:
        if highlight:
            text = text.replace(" ", "#")

    return text
