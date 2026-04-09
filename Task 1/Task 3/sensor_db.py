from __future__ import division

import os
import sqlite3


class SensorDatabase(object):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            temperature_status TEXT NOT NULL,
            humidity REAL NOT NULL,
            humidity_status TEXT NOT NULL,
            pressure REAL NOT NULL,
            pressure_status TEXT NOT NULL,
            pitch REAL NOT NULL,
            roll REAL NOT NULL,
            yaw REAL NOT NULL,
            orientation_status TEXT NOT NULL
        )
        """
        self.connection.execute(query)
        self.connection.commit()

    def insert_reading(
        self,
        timestamp,
        temperature,
        temperature_status,
        humidity,
        humidity_status,
        pressure,
        pressure_status,
        pitch,
        roll,
        yaw,
        orientation_status,
    ):
        query = """
        INSERT INTO sensor_readings (
            timestamp,
            temperature,
            temperature_status,
            humidity,
            humidity_status,
            pressure,
            pressure_status,
            pitch,
            roll,
            yaw,
            orientation_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.connection.execute(
            query,
            (
                timestamp,
                temperature,
                temperature_status,
                humidity,
                humidity_status,
                pressure,
                pressure_status,
                pitch,
                roll,
                yaw,
                orientation_status,
            ),
        )
        self.connection.commit()

    def fetch_all_readings(self):
        rows = self.connection.execute(
            "SELECT * FROM sensor_readings ORDER BY timestamp ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    def fetch_status_counts(self):
        query = """
        SELECT status, COUNT(*) AS total
        FROM (
            SELECT temperature_status AS status FROM sensor_readings
            UNION ALL
            SELECT humidity_status AS status FROM sensor_readings
            UNION ALL
            SELECT pressure_status AS status FROM sensor_readings
            UNION ALL
            SELECT orientation_status AS status FROM sensor_readings
        )
        GROUP BY status
        ORDER BY total DESC, status ASC
        """
        rows = self.connection.execute(query).fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self.connection.close()
