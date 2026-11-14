from flask import Flask, jsonify, render_template_string
import docker
from collections import deque
from datetime import datetime
import threading

app = Flask(__name__)

CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 80.0

history = deque(maxlen=20)
alerts = deque(maxlen=20)
active_alerts = set()
lock = threading.Lock()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Container Guardian V3</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            margin: 0;
            padding: 25px;
            background: #101827;
            color: white;
            font-family: Arial, sans-serif;
        }

        h1 { color: #38bdf8; }

        .subtitle { color: #94a3b8; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }

        .card {
            background: #1e293b;
            padding: 22px;
            border-radius: 12px;
            border: 1px solid #334155;
            overflow: hidden;
        }

        .metric {
            font-size: 25px;
            font-weight: bold;
        }

        .running { color: #4ade80; }
        .stopped { color: #f87171; }
        .warning { color: #facc15; }

        .chart-card {
            margin-top: 25px;
        }

        .chart-container {
            height: 260px;
        }

        .footer {
            margin-top: 30px;
            color: #94a3b8;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }

        .table-wrap {
            overflow-x: auto;
        }
    </style>
</head>

<body>

<h1>Container Guardian V3</h1>
<p class="subtitle">Smart Docker Health Monitoring Dashboard</p>
<p class="subtitle">Live updates every 5 seconds</p>

<div id="error" class="card warning" style="display:none"></div>

<h2>Container Overview</h2>
<div class="grid" id="containers"></div>

<div class="card chart-card">
    <h2>CPU Usage History</h2>
    <div class="chart-container">
        <canvas id="cpuChart"></canvas>
    </div>
</div>

<div class="card chart-card">
    <h2>RAM Usage History</h2>
    <div class="chart-container">
        <canvas id="ramChart"></canvas>
    </div>
</div>

<div class="card chart-card">
    <h2>Alert History</h2>
    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Container</th>
                    <th>Alert</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody id="alerts">
                <tr><td colspan="4">No alerts yet</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="footer">
    Container Guardian V3 | Python | Flask | Docker SDK | Chart.js
</div>

<script>
let cpuChart;
let ramChart;

function createCharts() {
    cpuChart = new Chart(document.getElementById("cpuChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "CPU %",
                data: [],
                borderColor: "#38bdf8",
                backgroundColor: "rgba(56,189,248,0.15)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    ramChart = new Chart(document.getElementById("ramChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "RAM %",
                data: [],
                borderColor: "#4ade80",
                backgroundColor: "rgba(74,222,128,0.15)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

async function updateDashboard() {
    try {
        const response = await fetch("/api/data");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Dashboard request failed");
        }

        document.getElementById("error").style.display = "none";

        const containerArea = document.getElementById("containers");
        containerArea.innerHTML = "";

        data.containers.forEach(c => {
            const card = document.createElement("div");
            card.className = "card";

            const status = document.createElement("p");
            status.textContent = "Status: " + c.status.toUpperCase();
            status.className = c.status === "running" ? "running" : "stopped";

            const name = document.createElement("h2");
            name.textContent = c.name;

            const id = document.createElement("p");
            id.textContent = "Container ID: " + c.id;

            const cpu = document.createElement("p");
            cpu.className = "metric";
            cpu.textContent = "CPU: " + c.cpu + "%";

            const memory = document.createElement("p");
            memory.className = "metric";
            memory.textContent = "Memory: " + c.memory;

            const percent = document.createElement("p");
            percent.className = "metric";
            percent.textContent = "RAM: " + c.memory_percent + "%";

            card.append(name, status, id, cpu, memory, percent);
            containerArea.appendChild(card);
        });

        const labels = data.history.map(x => x.time);

        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data =
            data.history.map(x => x.cpu);
        cpuChart.update();

        ramChart.data.labels = labels;
        ramChart.data.datasets[0].data =
            data.history.map(x => x.memory_percent);
        ramChart.update();

        const alertArea = document.getElementById("alerts");
        alertArea.innerHTML = "";

        if (data.alerts.length === 0) {
            alertArea.innerHTML =
                '<tr><td colspan="4">No alerts yet</td></tr>';
        } else {
            data.alerts.forEach(a => {
                const tr = document.createElement("tr");

                [a.time, a.container, a.type, a.value].forEach(value => {
                    const td = document.createElement("td");
                    td.textContent = value;
                    tr.appendChild(td);
                });

                alertArea.appendChild(tr);
            });
        }

    } catch (error) {
        const errorBox = document.getElementById("error");
        errorBox.textContent = "Dashboard Error: " + error.message;
        errorBox.style.display = "block";
    }
}

createCharts();
updateDashboard();
setInterval(updateDashboard, 5000);
</script>

</body>
</html>
"""


def get_container_data():
    client = docker.from_env()
    containers = []

    try:
        for container in client.containers.list(all=True):
            cpu = 0.0
            memory = "Not available"
            memory_percent = 0.0

            if container.status == "running":
                stats = container.stats(stream=False)

                cpu_stats = stats["cpu_stats"]
                previous_cpu = stats["precpu_stats"]

                cpu_delta = (
                    cpu_stats["cpu_usage"]["total_usage"]
                    - previous_cpu["cpu_usage"]["total_usage"]
                )

                system_delta = (
                    cpu_stats.get("system_cpu_usage", 0)
                    - previous_cpu.get("system_cpu_usage", 0)
                )

                online_cpus = cpu_stats.get(
                    "online_cpus",
                    len(cpu_stats["cpu_usage"].get("percpu_usage", []))
                )

                if system_delta > 0 and cpu_delta >= 0:
                    cpu = round(
                        (cpu_delta / system_delta) * online_cpus * 100,
                        2
                    )

                memory_stats = stats["memory_stats"]
                usage = memory_stats.get("usage", 0)
                limit = memory_stats.get("limit", 0)

                memory = f"{usage / (1024 * 1024):.2f} MB"

                if limit > 0:
                    memory_percent = round(
                        (usage / limit) * 100, 2
                    )

            containers.append({
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "cpu": cpu,
                "memory": memory,
                "memory_percent": memory_percent
            })

        return containers

    finally:
        client.close()


def record_monitoring(containers):
    now = datetime.now().strftime("%H:%M:%S")

    for c in containers:
        if c["status"] != "running":
            continue

        with lock:
            history.append({
                "time": now,
                "container": c["name"],
                "cpu": c["cpu"],
                "memory_percent": c["memory_percent"]
            })

            checks = [
                ("CPU", c["cpu"]),
                ("RAM", c["memory_percent"])
            ]

            for resource, value in checks:
                key = (c["name"], resource)

                if value >= 80:
                    if key not in active_alerts:
                        alerts.append({
                            "time": now,
                            "container": c["name"],
                            "type": resource + " HIGH",
                            "value": f"{value}%"
                        })
                        active_alerts.add(key)

                elif key in active_alerts:
                    alerts.append({
                        "time": now,
                        "container": c["name"],
                        "type": resource + " RECOVERED",
                        "value": f"{value}%"
                    })
                    active_alerts.remove(key)


@app.route("/")
def dashboard():
    return render_template_string(HTML)


@app.route("/api/data")
def api_data():
    try:
        containers = get_container_data()
        record_monitoring(containers)

        with lock:
            return jsonify({
                "containers": containers,
                "history": list(history),
                "alerts": list(reversed(alerts))
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
