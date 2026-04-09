from __future__ import division

import sys
import time

from mood_assets import ORIENTATION_ANIMATIONS, SPECIAL_FLIP_ANIMATION


ROLL_THRESHOLD = 25.0
PITCH_THRESHOLD = 25.0
FLAT_THRESHOLD = 10.0
RAPID_FLIP_SECONDS = 0.5
RAPID_FLIP_ROLL_DELTA = 60.0
FRAME_DELAY_SECONDS = 0.22
LOOP_SLEEP_SECONDS = 0.05
SPECIAL_COOLDOWN_SECONDS = 1.0


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


def normalize_signed_angle(angle):
    angle = angle % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle


def angular_difference(first, second):
    return abs((first - second + 180.0) % 360.0 - 180.0)


class TiltEmotionApp(object):
    def __init__(self):
        self.sense = create_sense()
        self.paused = False
        self.current_zone = None
        self.resume_zone = None
        self.active_frames = []
        self.active_frame_index = 0
        self.next_frame_time = 0.0
        self.special_playing = False
        self.roll_history = []
        self.last_special_time = -SPECIAL_COOLDOWN_SECONDS

    def read_orientation(self):
        raw = self.sense.get_orientation_degrees()
        pitch = normalize_signed_angle(raw["pitch"])
        roll = normalize_signed_angle(raw["roll"])
        yaw = raw["yaw"] % 360.0
        return pitch, roll, yaw

    def detect_zone(self, pitch, roll):
        if abs(pitch) <= FLAT_THRESHOLD and abs(roll) <= FLAT_THRESHOLD:
            return "flat"

        if abs(roll) >= abs(pitch):
            if roll >= ROLL_THRESHOLD:
                return "tilt_right"
            if roll <= -ROLL_THRESHOLD:
                return "tilt_left"

        if pitch <= -PITCH_THRESHOLD:
            return "tilt_forward"
        if pitch >= PITCH_THRESHOLD:
            return "tilt_back"
        return "flat"

    def queue_animation(self, frames, special=False, resume_zone=None):
        self.active_frames = frames
        self.active_frame_index = 0
        self.next_frame_time = time.monotonic()
        self.special_playing = special
        self.resume_zone = resume_zone

    def maybe_trigger_flip(self, roll, now):
        self.roll_history.append((now, roll))
        cutoff = now - RAPID_FLIP_SECONDS
        self.roll_history = [(sample_time, sample_roll) for sample_time, sample_roll in self.roll_history if sample_time >= cutoff]

        if len(self.roll_history) < 2:
            return False

        oldest_time, oldest_roll = self.roll_history[0]
        roll_change = angular_difference(roll, oldest_roll)
        elapsed = now - oldest_time

        if (
            elapsed <= RAPID_FLIP_SECONDS
            and roll_change > RAPID_FLIP_ROLL_DELTA
            and now - self.last_special_time >= SPECIAL_COOLDOWN_SECONDS
        ):
            self.last_special_time = now
            self.roll_history = [(now, roll)]
            return True
        return False

    def handle_joystick(self):
        for event in self.sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                self.paused = not self.paused

    def update_animation(self):
        if not self.active_frames:
            return

        now = time.monotonic()
        if now < self.next_frame_time:
            return

        frame = self.active_frames[self.active_frame_index]
        self.sense.set_pixels(frame)
        self.active_frame_index += 1
        self.next_frame_time = now + FRAME_DELAY_SECONDS

        if self.active_frame_index >= len(self.active_frames):
            self.active_frames = []
            if self.special_playing and self.resume_zone:
                self.special_playing = False
                self.queue_animation(ORIENTATION_ANIMATIONS[self.resume_zone], special=False)

    def update(self):
        if self.paused:
            return

        now = time.monotonic()
        pitch, roll, yaw = self.read_orientation()
        zone = self.detect_zone(pitch, roll)

        if self.maybe_trigger_flip(roll, now) and not self.special_playing:
            self.queue_animation(SPECIAL_FLIP_ANIMATION, special=True, resume_zone=zone)
            self.current_zone = zone
        elif not self.special_playing and zone != self.current_zone:
            self.current_zone = zone
            self.queue_animation(ORIENTATION_ANIMATIONS[zone], special=False)

        self.update_animation()

    def run(self):
        try:
            while True:
                self.handle_joystick()
                self.update()
                time.sleep(LOOP_SLEEP_SECONDS)
        except KeyboardInterrupt:
            self.sense.clear()


if __name__ == "__main__":
    TiltEmotionApp().run()
