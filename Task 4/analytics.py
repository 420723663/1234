from __future__ import division

import argparse
import os
import sqlite3
import sys
from datetime import datetime


def import_plot_libraries():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as exc:
        print("Missing plotting library: {0}".format(exc), file=sys.stderr)
        sys.exit(1)

    return plt, sns


def parse_arguments():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_db = os.path.normpath(os.path.join(base_dir, "..", "Task3", "envirotrack.db"))

    parser = argparse.ArgumentParser(description="Create analytics charts from Task 3 data.")
    parser.add_argument(
        "--db",
        default=default_db,
        help="Path to envirotrack.db",
    )
    parser.add_argument(
        "--outdir",
        default=base_dir,
        help="Directory to save PNG files",
    )
    return parser.parse_args()


def get_connection(db_path):
    return sqlite3.connect(db_path)


def fetch_readings(connection):
    try:
        rows = connection.execute(
            """
            SELECT timestamp, temperature, humidity
            FROM sensor_readings
            ORDER BY timestamp ASC
            """
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return rows


def fetch_status_counts(connection):
    try:
        rows = connection.execute(
            """
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
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return rows


def create_empty_chart(plt, title, output_path):
    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.set_title(title)
    axis.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14)
    axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def create_trend_chart(plt, readings, output_path):
    if not readings:
        create_empty_chart(plt, "Temperature And Humidity Trends", output_path)
        return

    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in readings]
    temperatures = [row[1] for row in readings]
    humidities = [row[2] for row in readings]

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.plot(timestamps, temperatures, marker="o", label="Temperature (C)", color="#d1495b")
    axis.plot(timestamps, humidities, marker="s", label="Humidity (%)", color="#00798c")
    axis.set_title("Temperature And Humidity Trends")
    axis.set_xlabel("Timestamp")
    axis.set_ylabel("Reading")
    axis.tick_params(axis="x", rotation=30)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def create_status_chart(plt, sns, status_counts, output_path):
    if not status_counts:
        create_empty_chart(plt, "Status Counts", output_path)
        return

    labels = [row[0] for row in status_counts]
    totals = [row[1] for row in status_counts]

    figure, axis = plt.subplots(figsize=(8, 4.5))
    sns.barplot(x=labels, y=totals, palette="Set2", ax=axis)
    axis.set_title("Status Counts")
    axis.set_xlabel("Status")
    axis.set_ylabel("Count")
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def main():
    args = parse_arguments()
    output_dir = os.path.abspath(args.outdir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    plt, sns = import_plot_libraries()

    if not os.path.exists(args.db):
        readings = []
        status_counts = []
    else:
        connection = get_connection(args.db)
        try:
            readings = fetch_readings(connection)
            status_counts = fetch_status_counts(connection)
        finally:
            connection.close()

    trend_path = os.path.join(output_dir, "environment_trends.png")
    status_path = os.path.join(output_dir, "status_counts.png")

    create_trend_chart(plt, readings, trend_path)
    create_status_chart(plt, sns, status_counts, status_path)

    print("Saved: {0}".format(trend_path))
    print("Saved: {0}".format(status_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
