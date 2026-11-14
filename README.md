# 🛡️ Container Guardian – Smart Docker Health Monitor

**A Python-based Docker monitoring and recovery system with automated alerts, Gmail notifications, and a real-time web dashboard.**

Container Guardian monitors Docker containers, tracks CPU and memory usage, detects stopped containers, and helps maintain container health through configurable recovery actions.

It also provides a Flask-based web dashboard with resource usage charts and alert history.

## 🚀 Key Features

### V1 – Docker Health Monitoring
- Monitor Docker containers using Python Docker SDK.
- Track CPU and memory usage.
- Detect stopped containers.
- Automatically restart only authorized containers.
- Generate CSV monitoring reports.
- Configurable CPU and memory thresholds.

### V2 – Continuous Monitoring & Email Alerts
- Continuous monitoring with configurable intervals.
- CPU and memory threshold alerts.
- Gmail SMTP notifications.
- Smart alert deduplication.
- Recovery notifications when resource usage returns to normal.
- Graceful shutdown using Ctrl+C.
- Allowlisted container restart protection.

### V3 – Web Dashboard
- Flask-based web dashboard.
- Live Docker container status.
- CPU and RAM usage overview.
- CPU and memory usage history charts.
- Alert history with HIGH and RECOVERED events.
- Automatic dashboard refresh every 5 seconds.

## 🖥️ Dashboard Preview

The dashboard displays:
- Container names and statuses.
- Container IDs.
- CPU usage percentage.
- Memory usage in MB.
- RAM utilization percentage.
- Resource usage history.
- Alert history.

## 🏗️ Project Architecture

```text
             Docker Engine
                   |
                   v
          Python Docker SDK
                   |
                   v
          Container Guardian
                   |
          +--------+--------+
          |                 |
          v                 v
    monitor.py           app.py
          |                 |
          v                 v
   CPU/RAM Monitor     Flask Dashboard
          |                 |
          v                 v
    Alert Engine       Charts & History
          |
     +----+----+
     |         |
     v         v
   Gmail      CSV
 Notifications Reports
```

## 🛠️ Technologies Used

- Python 3
- Docker
- Docker SDK for Python
- Flask
- Plotly
- HTML and CSS
- Gmail SMTP
- Ubuntu Linux / WSL2
- Git and GitHub

## 📂 Project Structure

```text
container-guardian/
│
├── app.py
├── monitor.py
├── requirements.txt
├── container_report.csv
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/uttam9124/container-guardian.git
cd container-guardian
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Docker

Make sure Docker Engine or Docker Desktop is running and accessible from your Ubuntu terminal.

### 5. Configure environment variables

Configure your Gmail SMTP credentials using a local `.env` file, following the variable names expected by `monitor.py`.

**Security:** Never commit `.env`, Gmail App Passwords, or other credentials to GitHub.

## ▶️ Running the Project

### Start the monitoring system

```bash
python monitor.py
```

The monitoring system continuously checks Docker containers and generates alerts when configured thresholds are exceeded.

### Start the web dashboard

Open another Ubuntu terminal, activate the virtual environment, navigate to the project directory, and run:

```bash
python app.py
```

Open the dashboard in your browser:

http://localhost:5000

The dashboard refreshes automatically every 5 seconds.

## 📊 Monitoring Configuration

The monitoring system uses configurable settings in `monitor.py`.

Example configuration:

```python
CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 80.0
```

Only explicitly authorized containers should be allowed to restart automatically.

## 🧪 Testing Performed

- Docker container status monitoring.
- CPU usage stress testing.
- Memory usage stress testing.
- High CPU alert generation.
- High memory alert generation.
- Gmail notification delivery.
- Recovery notification testing.
- Automatic restart testing for authorized containers.
- Protection of unauthorized containers.
- CSV report generation.
- Flask dashboard functionality.
- Dashboard resource usage updates.
- Alert history verification.

## 🔒 Safety Features

- Authorized-container restart allowlist.
- Configurable resource thresholds.
- Environment-based email credentials.
- `.env` excluded from Git tracking.
- No automatic restart of unauthorized containers.

## 🔮 Future Improvements

- Docker health-check integration.
- Historical metrics storage.
- Advanced monitoring analytics.
- Authentication for the web dashboard.
- Production deployment using a WSGI server.
- Docker Compose deployment.

## 👨‍💻 Author

**Uttam Kumar Behera**

Computer Science Graduate

GitHub: https://github.com/uttam9124

---

⭐ If you find this project useful, consider giving it a star on GitHub.
