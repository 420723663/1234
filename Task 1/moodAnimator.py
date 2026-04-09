from __future__ import division

import sys
import time

from mood_assets import MOOD_EMOJIS, SLEEP_FACE


FRAME_DELAY_SECONDS = 0.45
INPUT_COOLDOWN_SECONDS = 3.0
IDLE_TIMEOUT_SECONDS = 15.0
LOOP_SLEEP_SECONDS = 0.05


def create_sense():
    try:
        from sense_hat import SenseHat
    except ImportError:
        print("sense_hat is not installed. Run this on Raspberry Pi OS with Sense HAT support.", file=sys.stderr)
        sys.exit(1)

    try:
        sense = SenseHat()
    except Exception as exc:
        print("Could not access Sense HAT: {0}".format(exc), file=sys.stderr)
        sys.exit(1)

    sense.low_light = False
    return sense


class MoodAnimatorApp(object):
    def __init__(self):
        self.sense = create_sense()
        self.emoji_index = 0
        self.frame_index = 0
        self.last_emoji_index = 0
        self.last_frame_index = 0
        self.paused = False
        self.sleeping = False
        self.last_input_time = 0.0
        self.last_activity_time = time.monotonic()
        self.next_frame_time = time.monotonic()

    def current_frames(self):
        return MOOD_EMOJIS[self.emoji_index]["frames"]

    def show_current_frame(self):
        frame = self.current_frames()[self.frame_index]
        self.sense.set_pixels(frame)
        self.last_emoji_index = self.emoji_index
        self.last_frame_index = self.frame_index

    def advance_frame(self):
        self.frame_index = (self.frame_index + 1) % len(self.current_frames())

    def enter_sleep(self):
        if self.sleeping:
            return
        self.sleeping = True
        self.sense.low_light = True
        self.sense.set_pixels(SLEEP_FACE)

    def wake_up(self):
        if not self.sleeping:
            return
        self.sleeping = False
        self.sense.low_light = False
        self.emoji_index = self.last_emoji_index
        self.frame_index = self.last_frame_index
        self.show_current_frame()
        self.next_frame_time = time.monotonic() + FRAME_DELAY_SECONDS

    def cycle_emoji(self, step):
        self.emoji_index = (self.emoji_index + step) % len(MOOD_EMOJIS)
        self.frame_index = 0
        self.last_emoji_index = self.emoji_index
        self.last_frame_index = self.frame_index
        self.show_current_frame()
        self.next_frame_time = time.monotonic() + FRAME_DELAY_SECONDS

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            self.next_frame_time = time.monotonic() + FRAME_DELAY_SECONDS

    def handle_event(self, event):
        if event.action != "pressed":
            return

        now = time.monotonic()
        self.last_activity_time = now

        if self.sleeping:
            self.wake_up()
            return

        if now - self.last_input_time < INPUT_COOLDOWN_SECONDS:
            return

        self.last_input_time = now

        if event.direction == "right":
            self.cycle_emoji(1)
        elif event.direction == "left":
            self.cycle_emoji(-1)
        elif event.direction == "middle":
            self.toggle_pause()

    def update(self):
        now = time.monotonic()

        if not self.sleeping and now - self.last_activity_time >= IDLE_TIMEOUT_SECONDS:
            self.enter_sleep()
            return

        if self.paused or self.sleeping:
            return

        if now >= self.next_frame_time:
            self.show_current_frame()
            self.advance_frame()
            self.next_frame_time = now + FRAME_DELAY_SECONDS

    def run(self):
        self.show_current_frame()
        self.advance_frame()
        self.next_frame_time = time.monotonic() + FRAME_DELAY_SECONDS

        try:
            while True:
                for event in self.sense.stick.get_events():
                    self.handle_event(event)
                self.update()
                time.sleep(LOOP_SLEEP_SECONDS)
        except KeyboardInterrupt:
            self.sense.clear()


if __name__ == "__main__":
    MoodAnimatorApp().run()
