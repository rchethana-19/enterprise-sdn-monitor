#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
from monitor import NetworkMonitor

app = Flask(__name__)
monitor = NetworkMonitor()

# Embedded layout configuration matching a Dark Enterprise NOC style
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Secure Enterprise SDN Monitoring Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        body {
            background-color: #121214;
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
        }
        header {
            border-bottom: 2px solid #1f2937;
            padding-bottom: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 { margin: 0; font-size: 24px; color: #3b82f6; }
        .grid-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .panel {
            background-color: #1e1e24;
            border: 1px solid #2d2d34;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status-badge {
            background-color: #10b981;
            color: #052e16;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #2d2d34;
            font-size: 13px;
        }
        th { color: #94a3b8; font-weight: 600; }
        #topology-map {
            width: 100%;
            height: 500px;
            background-color: #1a1a1e;
            border-radius: 6px;
            position: relative;
        }
        .node circle { stroke: #fff; stroke-width: 1.5px; }
        .link { stroke: #4b5563; stroke-opacity: 0.8; stroke-width: 2px; }
        .text-labels { font-size: 11px; fill: #cbd5e1; font-family: monospace; }
    </style>
</head>
<body>

    <header>
        <div>
            <h1>Secure Enterprise SDN Operations Control Center (NOC)</h1>
            <p style="color: #64748b; margin: 5px 0 0 0;">Real-time Open vSwitch Platform Metric Interface</p>
        </div>
        <div id="fw-indicator"><span class="status-badge">Firewall: Secured</span></div>
    </header>

    <div class="grid-container">
        <div class="panel">
            <h3>Live Topology & Dynamic Routing Matrix</h3>
            <div id="topology-map"></div>
        </div>

        <div>
            <div class="panel">
                <h3>Node Performance & Latency Logs</h3>
                <div id="telemetry-table">Data stream connecting...</div>
            </div>
            
            <div class="panel">
                <h3>Core Switching Metrics (OVS)</h3>
                <div id="switch-table">Parsing OpenFlow pipeline...</div>
            </div>
        </div>
    </div>

    <script>
        const topologyData = {
            nodes: [
                { id: "Internet", group: "wan" },
                { id: "fw1", group: "firewall" },
                { id: "s1", group: "core" },
                { id: "s2", group: "switch" }, { id: "s3", group: "switch" }, 
                { id: "s4", group: "switch" }, { id: "s5", group: "switch" },
                { id: "h1", group: "eng" }, { id: "h2", group: "eng" }, { id: "h3", group: "eng" },
                { id: "h4", group: "hr" }, { id: "h5", group: "hr" },
                { id: "h6", group: "finance" }, { id: "h7", group: "finance" },
                { id: "h8", group: "server" }, { id: "h9", group: "server" }
            ],
            links: [
                { source: "Internet", target: "fw1" },
                { source: "fw1", target: "s1" },
                { source: "s1", target: "s2" }, { source: "s1", target: "s3" },
                { source: "s1", target: "s4" }, { source: "s1", target: "s5" },
                { source: "s2", target: "h1" }, { source: "s2", target: "h2" }, { source: "s2", target: "h3" },
                { source: "s3", target: "h4" }, { source: "s3", target: "h5" },
                { source: "s4", target: "h6" }, { source: "s4", target: "h7" },
                { source: "s5", target: "h8" }, { source: "s5", target: "h9" }
            ]
        };

        const width = document.getElementById('topology-map').clientWidth;
        const height = 500;

        const svg = d3.select("#topology-map")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const simulation = d3.forceSimulation(topologyData.nodes)
            .force("link", d3.forceLink(topologyData.links).id(d => d.id).distance(70))
            .force("charge", d3.forceManyBody().strength(-220))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(topologyData.links)
            .enter().append("line")
            .attr("class", "link");

        const colorScale = d3.scaleOrdinal()
            .domain(["wan", "firewall", "core", "switch", "eng", "hr", "finance", "server"])
            .range(["#ef4444", "#f59e0b", "#3b82f6", "#10b981", "#a855f7", "#ec4899", "#6366f1", "#14b8a6"]);

        const node = svg.append("g")
            .selectAll("circle")
            .data(topologyData.nodes)
            .enter().append("circle")
            .attr("r", 10)
            .attr("fill", d => colorScale(d.group))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = svg.append("g")
            .selectAll("text")
            .data(topologyData.nodes)
            .enter().append("text")
            .attr("class", "text-labels")
            .attr("dx", 14)
            .attr("dy", 4)
            .text(d => d.id);

        simulation.on("tick", () => {
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label.attr("x", d => d.x)
                 .attr("y", d => d.y);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
        }
        function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
        }

        function updateMetrics() {
            fetch('/api/metrics')
                .then(res => res.json())
                .then(data => {
                    let latencyHtml = `<table><tr><th>Host Asset</th><th>Latency RTT</th></tr>`;
                    for (const [host, val] of Object.entries(data.latency_stats)) {
                        let color = val.includes("Timeout") ? "#ef4444" : "#10b981";
                        latencyHtml += `<tr><td><strong>${host}</strong></td><td style="color:${color}; font-weight:bold;">${val}</td></tr>`;
                    }
                    latencyHtml += `</table>`;
                    document.getElementById('telemetry-table').innerHTML = latencyHtml;

                    let swHtml = `<table><tr><th>Switch Interface</th><th>Rx Packets</th><th>Tx Packets</th><th>Loss Rate</th></tr>`;
                    for (const [sw, ports] of Object.entries(data.switch_stats)) {
                        ports.forEach(p => {
                            if(p.port !== 'LOCAL') {
                                swHtml += `<tr><td>${sw} (Port ${p.port})</td><td>${p.rx_packets}</td><td>${p.tx_packets}</td><td>${p.packet_loss_pct}%</td></tr>`;
                            }
                        });
                    }
                    swHtml += `</table>`;
                    document.getElementById('switch-table').innerHTML = swHtml;
                });
        }

        setInterval(updateMetrics, 3000);
        updateMetrics();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard_home():
    return render_template_string(HTML_DASHBOARD)

@app.route('/api/metrics')
def network_metrics_api():
    return jsonify(monitor.get_complete_metrics())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
