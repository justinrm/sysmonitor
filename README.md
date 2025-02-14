# System Monitoring Script

This script monitors various system metrics at regular intervals and detects anomalies such as CPU spikes, high memory usage, elevated load averages, rapid disk I/O or network error increases, and high temperatures. These conditions may indicate potential issues that could lead to system freezes.

## Features

- **Configurable Thresholds**: Set custom thresholds for CPU usage, memory usage, load average, disk I/O, network errors, and temperature.
- **Anomaly Detection**: Detects and logs anomalies based on the configured thresholds.
- **Detailed Logging**: Logs system metrics and detected anomalies to a rotating log file.
- **Temperature Monitoring**: Monitors temperature readings from available sensors.
- **Delta Calculation**: Calculates deltas for disk I/O and network errors to detect rapid increases.
- **Command-Line Arguments**: Configure the script using command-line arguments.

## Usage

1.  Save the script as `sysmonitor.py`.
2.  Run the script from the command line, optionally providing custom thresholds:

    ```bash
    python sysmonitor.py [--cpu_threshold CPU_THRESHOLD] [--memory_threshold MEMORY_THRESHOLD] ...
    ```

    For example:

    ```bash
    python sysmonitor.py --cpu_threshold 95 --memory_threshold 95 --interval 60 --log_file system_monitor.log
    ```

## Command-Line Arguments

| Argument             | Description                                                              | Default Value           |
| -------------------- | ------------------------------------------------------------------------ | ----------------------- |
| `--cpu_threshold`    | CPU usage percentage threshold.                                          | `90.0`                  |
| `--memory_threshold` | Memory usage percentage threshold.                                       | `90.0`                  |
| `--load_multiplier`  | Load average multiplier relative to CPU cores.                           | `1.5`                   |
| `--disk_io_threshold`| Disk I/O threshold in bytes per interval.                               | `100 * 1024 * 1024` (100MB) |
| `--net_error_threshold`| Network error threshold in one interval.                               | `10`                    |
| `--temp_threshold`   | Temperature threshold in Celsius.                                        | `80.0`                  |
| `--interval`         | Interval in seconds between metric checks.                               | `10.0`                  |
| `--log_file`         | Log file path.                                                           | `sysmonitor.log` |

## Dependencies

-   psutil: A cross-platform library for retrieving information on running processes and system utilization.

    ```bash
    pip install psutil
    ```

## Logging

The script logs system metrics and detected anomalies to a rotating log file. The log file is configured to rotate when it reaches 5 MB, with up to 5 backup files.
