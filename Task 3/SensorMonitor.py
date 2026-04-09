from __future__ import division

import argparse
import os
import sys
import time
from datetime import datetime

from config_validator import load_and_validate_config
from sensor_db import SensorDatabase


GREEN = (60, 220, 120)
RED = (255, 70, 70)
BLUE = (70, 170, 255)
AMBER = (255, 180, 0)

LOOP_SLEEP_SECONDS = 0.05
MESSAGE_SCROLL_SPEED = 0.09


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


def normalize_yaw(angle):
    angle = angle % 360.0
    if abs(angle - 360.0) < 0.000001:
        return 0.0
    return angle


class SensorMonitor(object):
    def __init__(self, config_path, db_path):
        self.config_path = config_path
        self.db_path = db_path
        self.config = load_and_validate_config(config_path)
        self.sense = create_sense()
        self.database = SensorDatabase(db_path)
        self.paused = False
        self.last_reading = None
        self.next_poll_time = 0.0
        self.next_display_time = 0.0
        self.display_page_index = 0

    def classify_metric(self, value, minimum, maximum):
        if value < minimum:
            return "Low"
        if value > maximum:
            return "High"
        return "Comfortable"

    def classify_orientation(self, pitch, roll, yaw):
        orientation = self.config["orientation"]
        pitch_ok = orientation["pitch_min"] <= pitch <= orientation["pitch_max"]
        roll_ok = orientation["roll_min"] <= roll <= orientation["roll_max"]
        yaw_ok = orientation["yaw_min"] <= yaw <= orientation["yaw_max"]
        if pitch_ok and roll_ok and yaw_ok:
            return "Aligned"
        return "Tilted"

    def read_sensors(self):
        pitch_roll_yaw = self.sense.get_orientation_degrees()
        temperature = self.sense.get_temperature() + self.config["temperature"]["offset"]
        humidity = self.sense.get_humidity()
        pressure = self.sense.get_pressure()

        pitch = normalize_signed_angle(pitch_roll_yaw["pitch"])
        roll = normalize_signed_angle(pitch_roll_yaw["roll"])
        yaw = normalize_yaw(pitch_roll_yaw["yaw"])

        temperature_status = self.classify_metric(
            temperature,
            self.config["temperature"]["min"],
            self.config["temperature"]["max"],
        )
        humidity_status = self.classify_metric(
            humidity,
            self.config["humidity"]["min"],
            self.config["humidity"]["max"],
        )
        pressure_status = self.classify_metric(
            pressure,
            self.config["pressure"]["min"],
            self.config["pressure"]["max"],
        )
        orientation_status = self.classify_orientation(pitch, roll, yaw)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temperature, 2),
            "temperature_status": temperature_status,
            "humidity": round(humidity, 2),
            "humidity_status": humidity_status,
            "pressure": round(pressure, 2),
            "pressure_status": pressure_status,
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "yaw": round(yaw, 2),
            "orientation_status": orientation_status,
        }

    def store_reading(self, reading):
        self.database.insert_reading(
            reading["timestamp"],
            reading["temperature"],
            reading["temperature_status"],
            reading["humidity"],
            reading["humidity_status"],
            reading["pressure"],
            reading["pressure_status"],
            reading["pitch"],
            reading["roll"],
            reading["yaw"],
            reading["orientation_status"],
        )

    def poll_once(self):
        reading = self.read_sensors()
        self.store_reading(reading)
        self.last_reading = reading

    def get_environment_colour(self, reading):
        statuses = [
            reading["temperature_status"],
            reading["humidity_status"],
            reading["pressure_status"],
        ]
        if "High" in statuses:
            return RED
        if "Low" in statuses:
            return BLUE
        return GREEN

    def get_orientation_colour(self, reading):
        if reading["orientation_status"] == "Tilted":
            return AMBER
        return GREEN

    def build_display_pages(self, reading):
        environment_text = "T:{0:.1f} H:{1:.1f} P:{2:.0f}".format(
            reading["temperature"],
            reading["humidity"],
            reading["pressure"],
        )
        orientation_text = "ORI:{0}".format("A" if reading["orientation_status"] == "Aligned" else "T")
        detail_text = "P:{0:.0f} R:{1:.0f} Y:{2:.0f}".format(
            reading["pitch"],
            reading["roll"],
            reading["yaw"],
        )

        environment_colour = self.get_environment_colour(reading)
        orientation_colour = self.get_orientation_colour(reading)

        return [
            {"text": environment_text, "colour": environment_colour},
            {"text": orientation_text, "colour": orientation_colour},
            {"text": detail_text, "colour": orientation_colour},
        ]

    def show_next_page(self):
        if not self.last_reading:
            return

        pages = self.build_display_pages(self.last_reading)
        page = pages[self.display_page_index % len(pages)]
        self.sense.show_message(
            page["text"],
            text_colour=page["colour"],
            scroll_speed=MESSAGE_SCROLL_SPEED,
        )
        self.display_page_index += 1

    def handle_joystick(self):
        for event in self.sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                self.paused = not self.paused

    def run(self):
        self.next_poll_time = 0.0
        self.next_display_time = 0.0

        try:
            while True:
                self.handle_joystick()

                if self.paused:
                    time.sleep(LOOP_SLEEP_SECONDS)
                    continue

                now = time.monotonic()

                if self.last_reading is None or now >= self.next_poll_time:
                    self.poll_once()
                    self.next_poll_time = time.monotonic() + self.config["poll_interval_seconds"]

                if self.last_reading is not None and now >= self.next_display_time:
                    self.show_next_page()
                    self.next_display_time = time.monotonic() + self.config["display_interval_seconds"]

                time.sleep(LOOP_SLEEP_SECONDS)
        except KeyboardInterrupt:
            self.database.close()
            self.sense.clear()


def parse_arguments():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Monitor Sense HAT environment readings.")
    parser.add_argument(
        "--config",
        default=os.path.join(base_dir, "enviro_config.json"),
        help="Path to enviro_config.json",
    )
    parser.add_argument(
        "--db",
        default=os.path.join(base_dir, "envirotrack.db"),
        help="Path to SQLite database file",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    try:
        monitor = SensorMonitor(args.config, args.db)
    except ValueError as exc:
        print("Configuration error: {0}".format(exc), file=sys.stderr)
        return 1

    monitor.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
