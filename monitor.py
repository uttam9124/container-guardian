import docker
import csv
from datetime import datetime

RESTART_ALLOWED = {"guardian-test"}

CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 80.0

REPORT_FILE = "container_report.csv"


def monitor_containers():
    client = docker.from_env()

    print("=" * 50)
    print("          CONTAINER GUARDIAN")
    print("=" * 50)

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
                    len(cpu_stats["cpu_usage"].get("percpu_usage", []))
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

                if cpu_percent > CPU_THRESHOLD:
                    print("ALERT: High CPU usage detected!")

                if memory_percent > MEMORY_THRESHOLD:
                    print("ALERT: High Memory usage detected!")

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

    file_exists = False

    try:
        with open(REPORT_FILE, "r", newline=""):
            file_exists = True
    except FileNotFoundError:
        pass

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


if __name__ == "__main__":
    monitor_containers()
