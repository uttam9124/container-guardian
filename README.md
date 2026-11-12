# Container Guardian – Smart Docker Health Monitor

Container Guardian is a Python-based Docker monitoring tool built using Python and Docker SDK.

It monitors Docker containers, detects stopped containers, tracks CPU and memory usage, generates alerts, and saves monitoring data in CSV format.

## Features

- Monitor all Docker containers.
- Detect stopped containers.
- Automatically restart authorized containers.
- Monitor CPU usage.
- Monitor memory usage.
- Generate alerts when CPU usage exceeds 80%.
- Generate alerts when memory usage exceeds 80%.
- Generate CSV monitoring reports.
- Protect unauthorized containers from automatic restart.

## Technologies Used

- Python 3
- Docker
- Docker SDK for Python
- Ubuntu Linux
- CSV
- Git and GitHub

## Project Structure

    container-guardian/
    ├── monitor.py
    ├── requirements.txt
    ├── container_report.csv
    ├── README.md
    └── .gitignore

## Installation

Clone the repository:

    git clone YOUR_REPOSITORY_URL
    cd container-guardian

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Make sure Docker is installed and running.

## Configuration

Configure the following values in monitor.py:

    RESTART_ALLOWED = {"guardian-test"}
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 80.0

Only authorized containers can be automatically restarted.

## Run the Project

    python monitor.py

## Monitoring Report

The program generates container_report.csv.

The report includes:

- Timestamp
- Container Name
- Container Status
- CPU Usage
- Memory Usage
- Memory Percentage

## Testing Performed

- Container status monitoring
- Automatic restart testing
- CPU alert testing above 80%
- Memory alert testing above 80%
- CSV report generation
- Memory cleanup testing

## Future Improvements

- Continuous monitoring
- Email notifications
- Web-based dashboard
- Docker health check integration

## Author

Uttam Kumar Behera

Computer Science Graduate
