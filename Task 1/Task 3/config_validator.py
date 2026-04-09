from __future__ import division

import json


def _require_mapping(container, key):
    value = container.get(key)
    if not isinstance(value, dict):
        raise ValueError("'{0}' must be an object.".format(key))
    return value


def _require_number(container, key):
    if key not in container:
        raise ValueError("Missing required key: '{0}'.".format(key))

    value = container[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("'{0}' must be a number.".format(key))
    return float(value)


def _validate_range(section_name, section, min_key="min", max_key="max"):
    minimum = _require_number(section, min_key)
    maximum = _require_number(section, max_key)
    if minimum > maximum:
        raise ValueError(
            "'{0}.{1}' cannot be greater than '{0}.{2}'.".format(section_name, min_key, max_key)
        )
    return minimum, maximum


def load_and_validate_config(path):
    try:
        with open(path, "r") as handle:
            config = json.load(handle)
    except ValueError as exc:
        raise ValueError("Invalid JSON in config file: {0}".format(exc))
    except OSError as exc:
        raise ValueError("Could not read config file: {0}".format(exc))

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a JSON object at the top level.")

    poll_interval = _require_number(config, "poll_interval_seconds")
    display_interval = _require_number(config, "display_interval_seconds")

    if poll_interval <= 0:
        raise ValueError("'poll_interval_seconds' must be greater than 0.")
    if display_interval <= 0:
        raise ValueError("'display_interval_seconds' must be greater than 0.")

    temperature = _require_mapping(config, "temperature")
    humidity = _require_mapping(config, "humidity")
    pressure = _require_mapping(config, "pressure")
    orientation = _require_mapping(config, "orientation")

    temp_min, temp_max = _validate_range("temperature", temperature)
    humidity_min, humidity_max = _validate_range("humidity", humidity)
    pressure_min, pressure_max = _validate_range("pressure", pressure)
    temp_offset = _require_number(temperature, "offset")

    pitch_min = _require_number(orientation, "pitch_min")
    pitch_max = _require_number(orientation, "pitch_max")
    roll_min = _require_number(orientation, "roll_min")
    roll_max = _require_number(orientation, "roll_max")
    yaw_min = _require_number(orientation, "yaw_min")
    yaw_max = _require_number(orientation, "yaw_max")

    if pitch_min > pitch_max:
        raise ValueError("'orientation.pitch_min' cannot be greater than 'orientation.pitch_max'.")
    if roll_min > roll_max:
        raise ValueError("'orientation.roll_min' cannot be greater than 'orientation.roll_max'.")
    if yaw_min > yaw_max:
        raise ValueError("'orientation.yaw_min' cannot be greater than 'orientation.yaw_max'.")
    if yaw_min < 0 or yaw_max > 360:
        raise ValueError("'orientation.yaw_min' and 'orientation.yaw_max' must stay within 0..360.")

    return {
        "poll_interval_seconds": poll_interval,
        "display_interval_seconds": display_interval,
        "temperature": {
            "min": temp_min,
            "max": temp_max,
            "offset": temp_offset,
        },
        "humidity": {
            "min": humidity_min,
            "max": humidity_max,
        },
        "pressure": {
            "min": pressure_min,
            "max": pressure_max,
        },
        "orientation": {
            "pitch_min": pitch_min,
            "pitch_max": pitch_max,
            "roll_min": roll_min,
            "roll_max": roll_max,
            "yaw_min": yaw_min,
            "yaw_max": yaw_max,
        },
    }
