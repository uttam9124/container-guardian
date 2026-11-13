import docker
import csv
import time
import os
import smtplib

from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

RESTART_ALLOWED = {"guardian-test"}

CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 80.0

MONITOR_INTERVAL = 5
REPORT_FILE = "container_report.csv"

active_alerts = set()


def send_email(subject, body):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not sender or not password or not receiver:
        print("EMAIL ERROR: Gmail configuration missing.")
        return False

    message = EmailMessage()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, timeout=15
        ) as server:

            server.login(sender, password.replace(" ", ""))
            server.send_message(message)

        print("EMAIL SENT: Notification delivered successfully.")
        return True

    except Exception as error:
        print(f"EMAIL ERROR: {error}")
        return False


def check_alert(container_name, alert_type, condition, usage):
    alert_key = (container_name, alert_type)

    if condition and alert_key not in active_alerts:
        print(
            f"ALERT: High {alert_type} usage detected "
            f"in {container_name}!"
        )

        active_alerts.add(alert_key)

        send_email(
            f"Container Guardian Alert: High {alert_type}",
            f"""
Container Guardian detected high resource usage.

Container: {container_name}
Alert Type: {alert_type}
Current Usage: {usage:.2f}%
Threshold: 80%

Please investigate your Docker container.
"""
        )

    elif not condition and alert_key in active_alerts:
        print(
            f"RECOVERY: {alert_type} usage back to normal "
            f"in {container_name}."
        )

        active_alerts.remove(alert_key)

        send_email(
            f"Container Guardian Recovery: {alert_type}",
            f"""
Container Guardian detected that resource usage is back to normal.

Container: {container_name}
Resource: {alert_type}
Current Usage: {usage:.2f}%

The issue appears to be resolved.
"""
        )


def monitor_containers():
    client = docker.from_env()

    print("\n" + "=" * 50)
    print("          CONTAINER GUARDIAN V2")
    print("=" * 50)

    try:
        containers = client.containers.list(all=True)
        report_data = []

        if not containers:
            print("No Docker containers found.")
            return

        for container in containers:
            container.reload()

            name = container.name
            status = container.status.upper()

            cpu_percent = 0.0
            memory_mb = 0.0
            memory_percent = 0.0

            print(f"\nContainer Name : {name}")
            print(f"Status         : {status}")

            if status != "RUNNING":
                if name in RESTART_ALLOWED:
                    try:
                        print("ALERT: Container is stopped!")
                        print("Action: Attempting automatic restart...")

                        container.restart()
                        container.reload()

                        status = container.status.upper()
                        print(f"Recovery Status: {status}")

                    except Exception as error:
                        print(f"Restart Failed: {error}")
                        status = container.status.upper()

                else:
                    print("Automatic restart: Not authorized")

            if status == "RUNNING":
                try:
                    stats = container.stats(stream=False)

                    cpu_stats = stats["cpu_stats"]
                    precpu_stats = stats["precpu_stats"]

                    cpu_delta = (
                        cpu_stats["cpu_usage"]["total_usage"]
                        - precpu_stats["cpu_usage"]["total_usage"]
                    )

                    system_delta = (
                        cpu_stats["system_cpu_usage"]
                        - precpu_stats["system_cpu_usage"]
                    )

                    online_cpus = cpu_stats.get(
                        "online_cpus",
                        len(
                            cpu_stats["cpu_usage"].get(
                                "percpu_usage", []
                            )
                        )
                    )

                    if cpu_delta > 0 and system_delta > 0:
                        cpu_percent = (
                            cpu_delta / system_delta
                        ) * online_cpus * 100.0

                    memory = stats["memory_stats"]
                    memory_usage = memory["usage"]
                    memory_limit = memory["limit"]

                    memory_mb = memory_usage / (1024 * 1024)

                    if memory_limit:
                        memory_percent = (
                            memory_usage / memory_limit
                        ) * 100

                    print(f"CPU Usage      : {cpu_percent:.2f}%")
                    print(f"Memory Usage   : {memory_mb:.2f} MB")
                    print(f"Memory Percent : {memory_percent:.2f}%")

                    check_alert(
                        name,
                        "CPU",
                        cpu_percent > CPU_THRESHOLD,
                        cpu_percent
                    )

                    check_alert(
                        name,
                        "Memory",
                        memory_percent > MEMORY_THRESHOLD,
                        memory_percent
                    )

                except Exception as error:
                    print(f"Monitoring Error: {error}")

            report_data.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name,
                status,
                round(cpu_percent, 2),
                round(memory_mb, 2),
                round(memory_percent, 2)
            ])

            print("-" * 50)

        file_exists = os.path.exists(REPORT_FILE)

        with open(REPORT_FILE, "a", newline="") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Timestamp",
                    "Container Name",
                    "Status",
                    "CPU Usage (%)",
                    "Memory Usage (MB)",
                    "Memory Usage (%)"
                ])

            writer.writerows(report_data)

        print(f"\nReport saved successfully: {REPORT_FILE}")

    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 50)
    print("     CONTAINER GUARDIAN V2 STARTING")
    print("=" * 50)
    print(f"Monitoring interval: {MONITOR_INTERVAL} seconds")
    print("Press Ctrl+C to stop monitoring.")

    try:
        while True:
            monitor_containers()

            print(
                f"\nNext monitoring cycle in "
                f"{MONITOR_INTERVAL} seconds..."
            )

            time.sleep(MONITOR_INTERVAL)

    except KeyboardInterrupt:
        print("\nContainer Guardian stopped safely.")
