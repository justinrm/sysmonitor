#!/usr/bin/env python3
"""System Monitoring Script.

This script logs various system metrics at regular intervals and detects anomalies such as CPU spikes,
high memory usage, elevated load averages, rapid disk I/O or network error increases, and high temperatures.
These conditions may indicate potential issues that could lead to system freezes.

Usage:
    python sysmonitor.py [--cpu_threshold CPU_THRESHOLD] [--memory_threshold MEMORY_THRESHOLD] ...
"""

import argparse
import logging
import logging.handlers
import os
import sys
import time
from typing import Dict, Optional

import psutil


class SystemMonitor:
    """Monitors system metrics and logs anomalies based on configurable thresholds.

    Attributes:
        cpu_threshold (float): CPU usage percentage threshold.
        memory_threshold (float): Memory usage percentage threshold.
        load_multiplier (float): Multiplier applied to CPU count to derive load average threshold.
        disk_io_threshold (int): Disk I/O delta threshold in bytes.
        net_error_threshold (int): Network error count threshold for delta.
        temp_threshold (float): Temperature threshold in Celsius.
        interval (float): Interval in seconds between metric checks.
        previous_metrics (Dict[str, Optional[float]]): Storage for previous metric values to calculate deltas.
    """

    def __init__(
        self,
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        load_multiplier: float = 1.5,
        disk_io_threshold: int = 100 * 1024 * 1024,
        net_error_threshold: int = 10,
        temp_threshold: float = 80.0,
        interval: float = 10.0,
        log_file: str = "sysmonitor.log",
    ) -> None:
        """Initializes the SystemMonitor with thresholds and logging configuration.

        Args:
            cpu_threshold (float): CPU usage percentage threshold.
            memory_threshold (float): Memory usage percentage threshold.
            load_multiplier (float): Load average multiplier relative to CPU count.
            disk_io_threshold (int): Disk I/O threshold in bytes.
            net_error_threshold (int): Network error threshold.
            temp_threshold (float): Temperature threshold in Celsius.
            interval (float): Time between metric checks.
            log_file (str): Path to the log file.
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.load_multiplier = load_multiplier
        self.disk_io_threshold = disk_io_threshold
        self.net_error_threshold = net_error_threshold
        self.temp_threshold = temp_threshold
        self.interval = interval
        self.previous_metrics: Dict[str, Optional[float]] = {
            "disk_read_bytes": None,
            "disk_write_bytes": None,
            "net_errin": None,
            "net_errout": None,
        }
        self._configure_logging(log_file)

    def _configure_logging(self, log_file: str) -> None:
        """Configures logging with a rotating file handler.

        Args:
            log_file (str): Path to the log file.
        """
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Set up a rotating file handler: 5 MB per file, up to 5 backups.
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def get_load_average(self) -> Optional[float]:
        """Returns the system's 1-minute load average.

        Returns:
            Optional[float]: The 1-minute load average, or None if unavailable.
        """
        try:
            return os.getloadavg()[0]
        except (AttributeError, OSError) as e:
            logging.debug("Load average not available: %s", e)
            return None

    def get_temperatures(self) -> Dict[str, float]:
        """Retrieves temperature readings from available sensors.

        Returns:
            Dict[str, float]: A mapping of sensor names to the highest recorded temperature.
        """
        temp_readings: Dict[str, float] = {}
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return temp_readings
            for sensor, entries in temps.items():
                if entries:
                    # Choose the highest temperature from all entries for this sensor.
                    max_temp = max(entry.current for entry in entries)
                    temp_readings[sensor] = max_temp
        except Exception as e:
            logging.debug("Failed to get temperatures: %s", e)
        return temp_readings

    def log_system_metrics(self) -> None:
        """Captures, analyzes, and logs system metrics along with any detected anomalies."""
        start_time = time.time()

        # Collect metrics. Note that cpu_percent blocks for 1 second.
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        load_avg = self.get_load_average()
        temperatures = self.get_temperatures()

        anomalies = []

        # Detect high CPU usage.
        if cpu_usage > self.cpu_threshold:
            anomalies.append(f"High CPU usage: {cpu_usage:.1f}%")

        # Detect high memory usage.
        if mem.percent > self.memory_threshold:
            anomalies.append(f"High Memory usage: {mem.percent:.1f}%")

        # Detect high load average relative to CPU count.
        if load_avg is not None:
            cpu_count = psutil.cpu_count() or 1  # Avoid division by zero
            if load_avg > cpu_count * self.load_multiplier:
                anomalies.append(f"High Load Average: {load_avg:.2f} (CPU count: {cpu_count})")

        # Detect high temperatures.
        for sensor, temp in temperatures.items():
            if temp > self.temp_threshold:
                anomalies.append(f"High temperature on {sensor}: {temp:.1f}°C")

        # Calculate disk I/O deltas.
        if self.previous_metrics["disk_read_bytes"] is not None:
            disk_read_delta = disk_io.read_bytes - self.previous_metrics["disk_read_bytes"]
            disk_write_delta = disk_io.write_bytes - self.previous_metrics["disk_write_bytes"]
            if disk_read_delta > self.disk_io_threshold:
                anomalies.append(f"High Disk Read: {disk_read_delta} bytes in interval")
            if disk_write_delta > self.disk_io_threshold:
                anomalies.append(f"High Disk Write: {disk_write_delta} bytes in interval")
        # Update disk I/O baseline.
        self.previous_metrics["disk_read_bytes"] = disk_io.read_bytes
        self.previous_metrics["disk_write_bytes"] = disk_io.write_bytes

        # Calculate network error deltas.
        if self.previous_metrics["net_errin"] is not None:
            net_errin_delta = net_io.errin - self.previous_metrics["net_errin"]
            net_errout_delta = net_io.errout - self.previous_metrics["net_errout"]
            if net_errin_delta > self.net_error_threshold:
                anomalies.append(f"High Incoming Network Errors: {net_errin_delta} in interval")
            if net_errout_delta > self.net_error_threshold:
                anomalies.append(f"High Outgoing Network Errors: {net_errout_delta} in interval")
        # Update network error baseline.
        self.previous_metrics["net_errin"] = net_io.errin
        self.previous_metrics["net_errout"] = net_io.errout

        # Compose the log message.
        log_message = (
            f"CPU: {cpu_usage:.1f}% | "
            f"Memory: {mem.percent:.1f}% used (Total: {mem.total} bytes) | "
            f"Disk Read: {disk_io.read_bytes} bytes, Write: {disk_io.write_bytes} bytes | "
            f"Net Sent: {net_io.bytes_sent} bytes, Recv: {net_io.bytes_recv} bytes | "
            f"Load Avg (1m): {load_avg if load_avg is not None else 'N/A'} | "
            f"Temperatures: {temperatures}"
        )

        if anomalies:
            log_message += " | Anomalies: " + "; ".join(anomalies)
            logging.warning(log_message)
        else:
            logging.info(log_message)

        # Adjust sleep to maintain consistent intervals despite measurement time.
        elapsed = time.time() - start_time
        sleep_time = max(0, self.interval - elapsed)
        time.sleep(sleep_time)

    def run(self) -> None:
        """Starts the continuous monitoring loop until interrupted."""
        logging.info("Starting system monitoring with interval: %s seconds.", self.interval)
        try:
            while True:
                self.log_system_metrics()
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user.")


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments to configure the system monitor.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Enhanced System Monitoring Script"
    )
    parser.add_argument(
        "--cpu_threshold",
        type=float,
        default=90.0,
        help="CPU usage percentage threshold (default: 90)",
    )
    parser.add_argument(
        "--memory_threshold",
        type=float,
        default=90.0,
        help="Memory usage percentage threshold (default: 90)",
    )
    parser.add_argument(
        "--load_multiplier",
        type=float,
        default=1.5,
        help="Load average multiplier relative to CPU cores (default: 1.5)",
    )
    parser.add_argument(
        "--disk_io_threshold",
        type=int,
        default=100 * 1024 * 1024,
        help="Disk I/O threshold in bytes per interval (default: 100 MB)",
    )
    parser.add_argument(
        "--net_error_threshold",
        type=int,
        default=10,
        help="Network error threshold in one interval (default: 10)",
    )
    parser.add_argument(
        "--temp_threshold",
        type=float,
        default=80.0,
        help="Temperature threshold in Celsius (default: 80°C)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10.0,
        help="Interval in seconds between metric checks (default: 10)",
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default="enhanced_system_monitor.log",
        help="Log file path (default: enhanced_system_monitor.log)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: parse arguments and start system monitoring."""
    args = parse_arguments()
    monitor = SystemMonitor(
        cpu_threshold=args.cpu_threshold,
        memory_threshold=args.memory_threshold,
        load_multiplier=args.load_multiplier,
        disk_io_threshold=args.disk_io_threshold,
        net_error_threshold=args.net_error_threshold,
        temp_threshold=args.temp_threshold,
        interval=args.interval,
        log_file=args.log_file,
    )
    monitor.run()


if __name__ == "__main__":
    main()
