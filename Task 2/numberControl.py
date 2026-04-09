from __future__ import division

import math
import sys
import time


LOOP_SLEEP_SECONDS = 0.05
SCROLL_STEP_SECONDS = 0.18
TEXT_COLOUR = (255, 255, 255)
BACKGROUND_COLOUR = (0, 0, 0)
ERROR_COLOUR = (255, 70, 70)

FONT_3X5 = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "001", "001", "001"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    "-": ["000", "000", "111", "000", "000"],
    ".": ["000", "000", "000", "000", "010"],
    "e": ["000", "111", "111", "100", "111"],
}


def create_sense():
    try:
        from sense_hat import SenseHat
    except ImportError:
        print("sense_hat is not installed. Run this on Raspberry Pi OS with Sense HAT support.", file=sys.stderr)
        sys.exit(1)

    try:
        return SenseHat()
    except Exception as exc:
        print("Could not access Sense HAT: {0}".format(exc), file=sys.stderr)
        sys.exit(1)


class NumberControlApp(object):
    def __init__(self):
        self.sense = create_sense()
        self.default_value = 16
        self.value = 16
        self.display_text = self.format_value()
        self.display_columns = self.build_columns(self.display_text)
        self.scroll_index = 0
        self.next_scroll_time = time.monotonic()

    def compact_scientific(self, value):
        mantissa, exponent = "{0:.2e}".format(value).split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        exponent = str(int(exponent))
        return "{0}e{1}".format(mantissa, exponent)

    def format_value(self):
        value = self.value

        if isinstance(value, float):
            if abs(value - round(value)) < 0.000001:
                value = int(round(value))
            elif abs(value) >= 1000000:
                return self.compact_scientific(value)
            else:
                return "{0:.3f}".format(value).rstrip("0").rstrip(".")

        if isinstance(value, int):
            if abs(value) >= 1000000:
                return self.compact_scientific(float(value))
            return str(value)

        return str(value)

    def build_columns(self, text):
        columns = []

        for char in text:
            glyph = FONT_3X5.get(char.lower(), FONT_3X5["-"])
            for column_index in range(3):
                column = []
                for row in glyph:
                    column.append(TEXT_COLOUR if row[column_index] == "1" else BACKGROUND_COLOUR)
                columns.append(column)
            columns.append([BACKGROUND_COLOUR] * 5)

        if columns:
            columns.pop()

        if len(columns) <= 8:
            left_padding = (8 - len(columns)) // 2
            right_padding = 8 - len(columns) - left_padding
            return (
                [[BACKGROUND_COLOUR] * 5] * left_padding
                + columns
                + [[BACKGROUND_COLOUR] * 5] * right_padding
            )

        return columns + [[BACKGROUND_COLOUR] * 5] * 4

    def refresh_display_text(self):
        self.display_text = self.format_value()
        self.display_columns = self.build_columns(self.display_text)
        self.scroll_index = 0
        self.next_scroll_time = time.monotonic()

    def draw_current_window(self):
        pixels = []
        start = self.scroll_index if len(self.display_columns) > 8 else 0
        visible = self.display_columns[start:start + 8]

        if len(visible) < 8:
            visible += [[BACKGROUND_COLOUR] * 5] * (8 - len(visible))

        top_padding = 1
        bottom_padding = 2

        for row in range(8):
            for column in range(8):
                if row < top_padding or row >= 8 - bottom_padding:
                    pixels.append(BACKGROUND_COLOUR)
                else:
                    pixels.append(visible[column][row - top_padding])

        self.sense.set_pixels(pixels)

    def update_display(self):
        now = time.monotonic()

        if len(self.display_columns) <= 8:
            self.draw_current_window()
            return

        if now >= self.next_scroll_time:
            self.draw_current_window()
            self.scroll_index += 1
            if self.scroll_index > len(self.display_columns) - 8:
                self.scroll_index = 0
            self.next_scroll_time = now + SCROLL_STEP_SECONDS

    def show_error(self):
        self.sense.show_message("ERR", text_colour=ERROR_COLOUR, scroll_speed=0.06)
        self.refresh_display_text()

    def handle_event(self, event):
        if event.action != "pressed":
            return

        if event.direction == "up":
            self.value += 1
        elif event.direction == "down":
            self.value -= 1
        elif event.direction == "left":
            self.value = self.value ** 2
        elif event.direction == "right":
            if self.value < 0:
                self.show_error()
                return
            self.value = math.sqrt(self.value)
        elif event.direction == "middle":
            self.value = self.default_value

        self.refresh_display_text()
        self.draw_current_window()

    def run(self):
        try:
            self.draw_current_window()
            while True:
                for event in self.sense.stick.get_events():
                    self.handle_event(event)
                self.update_display()
                time.sleep(LOOP_SLEEP_SECONDS)
        except KeyboardInterrupt:
            self.sense.clear()


if __name__ == "__main__":
    NumberControlApp().run()
