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
| `--log_file`         | Log file path.                                                           | `enhanced_system_monitor.log` |

## Dependencies

-   psutil: A cross-platform library for retrieving information on running processes and system utilization.

    ```bash
    pip install psutil
    ```

## Logging

The script logs system metrics and detected anomalies to a rotating log file. The log file is configured to rotate when it reaches 5 MB, with up to 5 backup files.

## Class: SystemMonitor

### Attributes

-   [cpu_threshold](http://_vscodecontentref_/0) (*float*): CPU usage percentage threshold.
-   [memory_threshold](http://_vscodecontentref_/1) (*float*): Memory usage percentage threshold.
-   [load_multiplier](http://_vscodecontentref_/2) (*float*): Multiplier applied to CPU count to derive load average threshold.
-   [disk_io_threshold](http://_vscodecontentref_/3) (*int*): Disk I/O delta threshold in bytes.
-   [net_error_threshold](http://_vscodecontentref_/4) (*int*): Network error count threshold for delta.
-   [temp_threshold](http://_vscodecontentref_/5) (*float*): Temperature threshold in Celsius.
-   [interval](http://_vscodecontentref_/6) (*float*): Interval in seconds between metric checks.
-   [previous_metrics](http://_vscodecontentref_/7) (*Dict\[str, Optional\[float]]*): Storage for previous metric values to calculate deltas.

### Methods

-   [__init__(self, cpu_threshold: float = 90.0, memory_threshold: float = 90.0, load_multiplier: float = 1.5, disk_io_threshold: int = 100 * 1024 * 1024, net_error_threshold: int = 10, temp_threshold: float = 80.0, interval: float = 10.0, log_file: str = "enhanced\_system\_monitor.log") -> None](http://_vscodecontentref_/8): Initializes the SystemMonitor with thresholds and logging configuration.
-   [_configure_logging(self, log_file: str) -> None](http://_vscodecontentref_/9): Configures logging with a rotating file handler.
-   [get_load_average(self) -> Optional[float]](http://_vscodecontentref_/10): Returns the system's 1-minute load average.
-   [get_temperatures(self) -> Dict[str, float]](http://_vscodecontentref_/11): Retrieves temperature readings from available sensors.
-   [log_system_metrics(self) -> None](http://_vscodecontentref_/12): Captures, analyzes, and logs system metrics along with any detected anomalies.
-   [run(self) -> None](http://_vscodecontentref_/13): Starts the continuous monitoring loop until interrupted.

## Functions

-   [parse_arguments() -> argparse.Namespace](http://_vscodecontentref_/14): Parses command-line arguments to configure the system monitor.
-   [main() -> None](http://_vscodecontentref_/15): Entry point: parse arguments and start system monitoring.
