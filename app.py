#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
from monitor import NetworkMonitor

app = Flask(__name__)
monitor = NetworkMonitor()

# Enterprise NOC / SOC dashboard — single-file Flask template
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OVS-Vision | Enterprise SDN NOC</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        /* ── Base & Typography ─────────────────────────────────────── */
        *, *::before, *::after { box-sizing: border-box; }

        body {
            background-color: #121214;
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 16px 20px 24px;
            min-height: 100vh;
        }

        /* ── Header ────────────────────────────────────────────────── */
        header {
            border-bottom: 1px solid #2d2d34;
            padding-bottom: 16px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 12px;
        }

        .header-brand h1 {
            margin: 0;
            font-size: 26px;
            font-weight: 600;
            color: #e2e8f0;
            letter-spacing: 0.3px;
        }

        .header-brand .subtitle {
            color: #94a3b8;
            margin: 4px 0 0 0;
            font-size: 13px;
        }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .meta-item {
            text-align: right;
        }

        .meta-label {
            display: block;
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .meta-value {
            font-size: 13px;
            color: #e2e8f0;
            font-family: 'Segoe UI', monospace;
        }

        /* System status badge */
        .status-badge {
            display: inline-block;
            padding: 5px 14px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.3px;
            border: 1px solid transparent;
        }

        .status-healthy {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border-color: rgba(16, 185, 129, 0.35);
        }

        .status-warning {
            background-color: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border-color: rgba(245, 158, 11, 0.35);
        }

        .status-critical {
            background-color: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border-color: rgba(239, 68, 68, 0.35);
        }

        /* ── Layout ────────────────────────────────────────────────── */
        .grid-container {
            display: grid;
            grid-template-columns: 65fr 35fr;
            gap: 16px;
            align-items: start;
        }

        @media (max-width: 1100px) {
            .grid-container {
                grid-template-columns: 1fr;
            }
        }

        .right-column {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* ── Panels ────────────────────────────────────────────────── */
        .panel {
            background-color: #1e1e24;
            border: 1px solid #2d2d34;
            border-radius: 6px;
            padding: 16px;
            transition: border-color 0.15s ease;
        }

        .panel:hover {
            border-color: #3d3d48;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2d2d34;
        }

        .panel-title {
            margin: 0;
            font-size: 13px;
            font-weight: 600;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .panel-count {
            font-size: 11px;
            color: #94a3b8;
            background-color: #121214;
            padding: 2px 8px;
            border-radius: 3px;
            border: 1px solid #2d2d34;
        }

        /* ── Tables ───────────────────────────────────────────────── */
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }

        .data-table th,
        .data-table td {
            text-align: left;
            padding: 8px 10px;
            border-bottom: 1px solid #2d2d34;
            font-size: 12px;
        }

        .data-table th {
            color: #94a3b8;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .data-table tbody tr:hover {
            background-color: rgba(59, 130, 246, 0.04);
        }

        .data-table tbody tr:last-child td {
            border-bottom: none;
        }

        .val-healthy  { color: #10b981; font-weight: 600; }
        .val-warning  { color: #f59e0b; font-weight: 600; }
        .val-critical { color: #ef4444; font-weight: 600; }
        .val-info     { color: #3b82f6; font-weight: 600; }

        /* ── Alert Cards ────────────────────────────────────────────── */
        .alerts-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 280px;
            overflow-y: auto;
        }

        .alert-card {
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-left-width: 3px;
            border-radius: 4px;
            padding: 10px 12px;
        }

        .alert-card:hover {
            border-color: #3d3d48;
        }

        .alert-card.sev-critical { border-left-color: #ef4444; }
        .alert-card.sev-high     { border-left-color: #f59e0b; }
        .alert-card.sev-medium   { border-left-color: #eab308; }
        .alert-card.sev-info     { border-left-color: #3b82f6; }

        .alert-severity {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .alert-severity.critical { color: #ef4444; }
        .alert-severity.high     { color: #f59e0b; }
        .alert-severity.medium   { color: #eab308; }
        .alert-severity.info     { color: #3b82f6; }

        .alert-title {
            font-size: 13px;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 4px;
        }

        .alert-desc {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 6px;
            line-height: 1.4;
        }

        .alert-meta {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #64748b;
        }

        .no-alerts {
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            padding: 24px 12px;
            border: 1px dashed #2d2d34;
            border-radius: 4px;
        }

        /* ── Network Summary ────────────────────────────────────────── */
        .summary-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .summary-item {
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-radius: 4px;
            padding: 10px 12px;
        }

        .summary-item:hover {
            border-color: #3d3d48;
        }

        .summary-label {
            font-size: 10px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 4px;
        }

        .summary-value {
            font-size: 16px;
            font-weight: 600;
            color: #e2e8f0;
        }

        .summary-value.small {
            font-size: 12px;
            font-weight: 500;
        }

        /* ── Topology ───────────────────────────────────────────────── */
        .topology-panel {
            min-height: 600px;
        }

        #topology-map {
            width: 100%;
            height: 560px;
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }

        .node circle {
            stroke: #2d2d34;
            stroke-width: 1.5px;
            transition: fill 0.4s ease;
            cursor: grab;
        }

        .node circle:active { cursor: grabbing; }

        .link {
            stroke: #3d3d48;
            stroke-opacity: 0.7;
            stroke-width: 1.5px;
        }

        .text-labels {
            font-size: 10px;
            fill: #94a3b8;
            font-family: 'Segoe UI', sans-serif;
            pointer-events: none;
            user-select: none;
        }

        /* Scrollbar styling for alert panel */
        .alerts-container::-webkit-scrollbar { width: 5px; }
        .alerts-container::-webkit-scrollbar-track { background: #121214; }
        .alerts-container::-webkit-scrollbar-thumb { background: #2d2d34; border-radius: 3px; }

        .loading-text {
            color: #94a3b8;
            font-size: 12px;
            font-style: italic;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-brand">
            <h1>OVS-Vision</h1>
            <p class="subtitle">Enterprise SDN Network Operations &amp; Security Monitoring Platform</p>
        </div>
        <div class="header-meta">
            <div class="meta-item">
                <span class="meta-label">System Status</span>
                <span id="system-status-badge" class="status-badge status-healthy">Healthy</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Last Updated</span>
                <span id="last-updated" class="meta-value">--</span>
            </div>
        </div>
    </header>

    <!-- Two-column layout -->
    <div class="grid-container">

        <!-- LEFT: D3 Topology (65%) -->
        <div class="panel topology-panel">
            <div class="panel-header">
                <h3 class="panel-title">Network Topology</h3>
                <span class="panel-count" id="topology-node-count">17 nodes</span>
            </div>
            <div id="topology-map"></div>
        </div>

        <!-- RIGHT: Stacked panels (35%) -->
        <div class="right-column">

            <!-- 1. Host Latency -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Host Latency</h3>
                </div>
                <div id="latency-panel">
                    <span class="loading-text">Connecting to telemetry stream...</span>
                </div>
            </div>

            <!-- 2. OVS Switch Statistics -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">OVS Switch Statistics</h3>
                </div>
                <div id="switch-panel">
                    <span class="loading-text">Parsing OpenFlow pipeline...</span>
                </div>
            </div>

            <!-- 3. Active Security Alerts -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Active Security Alerts</h3>
                    <span class="panel-count" id="alert-count">0</span>
                </div>
                <div id="alerts-panel">
                    <span class="loading-text">Scanning security events...</span>
                </div>
            </div>

            <!-- 4. Network Summary -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Network Summary</h3>
                </div>
                <div id="summary-panel">
                    <span class="loading-text">Aggregating metrics...</span>
                </div>
            </div>

        </div>
    </div>

    <script>
        /* ================================================================
           Color constants — enterprise NOC palette
           ================================================================ */
        const COLORS = {
            healthy:  '#10b981',
            warning:  '#f59e0b',
            critical: '#ef4444',
            info:     '#3b82f6',
            neutral:  '#64748b'
        };

        const PACKET_LOSS_THRESHOLD = 5.0;
        const LATENCY_THRESHOLD     = 5.0;

        /* ================================================================
           Topology data — preserved from original force-directed graph
           ================================================================ */
        const topologyData = {
            nodes: [
                { id: "Internet", group: "wan" },
                { id: "fw1",      group: "firewall" },
                { id: "s1",       group: "core" },
                { id: "s2",       group: "switch" }, { id: "s3", group: "switch" },
                { id: "s4",       group: "switch" }, { id: "s5", group: "switch" },
                { id: "h1",       group: "eng" },    { id: "h2", group: "eng" },
                { id: "h3",       group: "eng" },
                { id: "h4",       group: "hr" },     { id: "h5", group: "hr" },
                { id: "h6",       group: "finance" },{ id: "h7", group: "finance" },
                { id: "h8",       group: "server" }, { id: "h9", group: "server" }
            ],
            links: [
                { source: "Internet", target: "fw1" },
                { source: "fw1",      target: "s1" },
                { source: "s1",       target: "s2" }, { source: "s1", target: "s3" },
                { source: "s1",       target: "s4" }, { source: "s1", target: "s5" },
                { source: "s2",       target: "h1" }, { source: "s2", target: "h2" },
                { source: "s2",       target: "h3" },
                { source: "s3",       target: "h4" }, { source: "s3", target: "h5" },
                { source: "s4",       target: "h6" }, { source: "s4", target: "h7" },
                { source: "s5",       target: "h8" }, { source: "s5", target: "h9" }
            ]
        };

        /* ================================================================
           D3 Topology — created once, colors updated on each refresh
           ================================================================ */
        const topoContainer = document.getElementById('topology-map');
        let topoWidth  = topoContainer.clientWidth;
        let topoHeight = 560;

        const svg = d3.select("#topology-map")
            .append("svg")
            .attr("width", topoWidth)
            .attr("height", topoHeight);

        const simulation = d3.forceSimulation(topologyData.nodes)
            .force("link", d3.forceLink(topologyData.links).id(d => d.id).distance(90))
            .force("charge", d3.forceManyBody().strength(-280))
            .force("center", d3.forceCenter(topoWidth / 2, topoHeight / 2))
            .force("collision", d3.forceCollide().radius(22));

        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(topologyData.links)
            .enter().append("line")
            .attr("class", "link");

        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(topologyData.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", 10)
            .attr("fill", COLORS.healthy);

        node.append("text")
            .attr("class", "text-labels")
            .attr("dx", 13)
            .attr("dy", 4)
            .text(d => d.id);

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
        }
        function dragged(event, d) {
            d.fx = event.x; d.fy = event.y;
        }
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
        }

        // Responsive resize — adjust SVG dimensions without recreating graph
        window.addEventListener('resize', () => {
            topoWidth  = topoContainer.clientWidth;
            topoHeight = Math.max(480, topoContainer.clientHeight || 560);
            svg.attr("width", topoWidth).attr("height", topoHeight);
            simulation.force("center", d3.forceCenter(topoWidth / 2, topoHeight / 2));
            simulation.alpha(0.2).restart();
        });

        /* ================================================================
           Helper utilities
           ================================================================ */

        /** Normalize severity string for consistent comparison */
        function normalizeSeverity(sev) {
            return (sev || '').toUpperCase();
        }

        /** Map severity to CSS class suffix */
        function severityClass(sev) {
            const s = normalizeSeverity(sev);
            if (s === 'CRITICAL') return 'critical';
            if (s === 'HIGH')     return 'high';
            if (s === 'MEDIUM')   return 'medium';
            return 'info';
        }

        /** Compute overall system status from active alerts */
        function computeSystemStatus(alerts) {
            if (!alerts || alerts.length === 0) return 'Healthy';
            const severities = alerts.map(a => normalizeSeverity(a.severity));
            if (severities.includes('CRITICAL')) return 'Critical';
            if (severities.includes('HIGH') || severities.includes('MEDIUM')) return 'Warning';
            return 'Healthy';
        }

        /** Format ISO timestamp for display */
        function formatTimestamp(iso) {
            if (!iso) return '--';
            try {
                const d = new Date(iso);
                return d.toLocaleString('en-US', {
                    month: 'short', day: 'numeric',
                    year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
                });
            } catch (e) {
                return iso;
            }
        }

        /** Build per-node health color map from metrics payload */
        function buildNodeColorMap(data) {
            const colors = {};
            topologyData.nodes.forEach(n => { colors[n.id] = COLORS.healthy; });

            // Firewall alert → red on fw1
            const fw = data.firewall || {};
            if (fw.status !== 'Active / Enforcing') {
                colors['fw1'] = COLORS.critical;
            }

            // Packet loss on switches → orange
            const switchStats = data.switch_stats || {};
            Object.entries(switchStats).forEach(([sw, ports]) => {
                const hasLoss = ports.some(p =>
                    p.port !== 'LOCAL' && p.packet_loss_pct > PACKET_LOSS_THRESHOLD
                );
                if (hasLoss) colors[sw] = COLORS.warning;
            });

            // Latency alerts on hosts → yellow
            const latencyStats = data.latency_stats || {};
            Object.entries(latencyStats).forEach(([host, val]) => {
                if (val.includes('Timeout') || val.includes('Unavailable')) {
                    colors[host] = COLORS.critical;
                    return;
                }
                const num = parseFloat(val);
                if (!isNaN(num) && num > LATENCY_THRESHOLD) {
                    colors[host] = '#eab308'; // yellow for latency
                }
            });

            // Override from explicit alert affected_device entries
            (data.alerts || []).forEach(alert => {
                const dev = alert.affected_device;
                if (!dev || !colors.hasOwnProperty(dev)) return;
                const sev = normalizeSeverity(alert.severity);
                if (sev === 'CRITICAL')      colors[dev] = COLORS.critical;
                else if (sev === 'HIGH')     colors[dev] = COLORS.warning;
                else if (sev === 'MEDIUM')   colors[dev] = '#eab308';
            });

            return colors;
        }

        /* ================================================================
           Panel update functions — each updates one section of the UI
           ================================================================ */

        /** Update header system status badge */
        function updateStatus(data) {
            const status  = computeSystemStatus(data.alerts);
            const badge   = document.getElementById('system-status-badge');
            badge.textContent = status;
            badge.className = 'status-badge status-' + status.toLowerCase();
        }

        /** Update last-updated timestamp in header */
        function updateLastUpdated(data) {
            document.getElementById('last-updated').textContent =
                formatTimestamp(data.timestamp);
        }

        /** Update host latency table */
        function updateLatency(data) {
            const container = document.getElementById('latency-panel');
            const stats = data.latency_stats || {};

            if (Object.keys(stats).length === 0) {
                container.innerHTML = '<span class="loading-text">No latency data available.</span>';
                return;
            }

            let html = '<table class="data-table"><thead><tr>' +
                '<th>Host</th><th>Latency</th></tr></thead><tbody>';

            for (const [host, val] of Object.entries(stats)) {
                let cls = 'val-healthy';
                if (val.includes('Timeout') || val.includes('Unavailable')) {
                    cls = 'val-critical';
                } else {
                    const num = parseFloat(val);
                    if (!isNaN(num) && num > LATENCY_THRESHOLD) cls = 'val-warning';
                }
                html += `<tr><td>${host}</td><td class="${cls}">${val}</td></tr>`;
            }

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        /** Update OVS switch statistics table */
        function updateSwitchStats(data) {
            const container = document.getElementById('switch-panel');
            const stats = data.switch_stats || {};

            let html = '<table class="data-table"><thead><tr>' +
                '<th>Switch</th><th>Port</th><th>RX Packets</th>' +
                '<th>TX Packets</th><th>Packet Loss %</th></tr></thead><tbody>';

            let hasRows = false;
            for (const [sw, ports] of Object.entries(stats)) {
                ports.forEach(p => {
                    if (p.port === 'LOCAL') return;
                    hasRows = true;
                    const lossCls = p.packet_loss_pct > PACKET_LOSS_THRESHOLD
                        ? 'val-critical' : 'val-healthy';
                    html += `<tr>
                        <td>${sw}</td>
                        <td>${p.port}</td>
                        <td>${p.rx_packets.toLocaleString()}</td>
                        <td>${p.tx_packets.toLocaleString()}</td>
                        <td class="${lossCls}">${p.packet_loss_pct}%</td>
                    </tr>`;
                });
            }

            html += '</tbody></table>';
            container.innerHTML = hasRows
                ? html
                : '<span class="loading-text">No switch data available.</span>';
        }

        /** Update active security alerts panel */
        function updateAlerts(data) {
            const container  = document.getElementById('alerts-panel');
            const countBadge = document.getElementById('alert-count');
            const alerts     = data.alerts || [];

            countBadge.textContent = alerts.length;

            if (alerts.length === 0) {
                container.innerHTML =
                    '<div class="no-alerts">No Active Security Alerts</div>';
                return;
            }

            let html = '<div class="alerts-container">';
            alerts.forEach(alert => {
                const cls = severityClass(alert.severity);
                html += `<div class="alert-card sev-${cls}">
                    <div class="alert-severity ${cls}">${alert.severity}</div>
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-desc">${alert.description}</div>
                    <div class="alert-meta">
                        <span>Device: ${alert.affected_device || 'N/A'}</span>
                        <span>${formatTimestamp(alert.timestamp)}</span>
                    </div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        /** Update network summary panel */
        function updateSummary(data) {
            const container = document.getElementById('summary-panel');
            const latencyStats = data.latency_stats || {};
            const switchStats  = data.switch_stats || {};
            const alerts       = data.alerts || [];
            const fw           = data.firewall || {};

            const totalHosts    = Object.keys(latencyStats).length;
            const totalSwitches = Object.keys(switchStats).length;
            const fwStatus      = fw.status || 'Unknown';
            const fwCls         = fwStatus === 'Active / Enforcing'
                ? 'val-healthy' : 'val-critical';

            container.innerHTML = `
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Total Hosts</div>
                        <div class="summary-value">${totalHosts}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Switches</div>
                        <div class="summary-value">${totalSwitches}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Firewall Status</div>
                        <div class="summary-value small ${fwCls}">${fwStatus}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Active Alerts</div>
                        <div class="summary-value ${alerts.length > 0 ? 'val-warning' : ''}">${alerts.length}</div>
                    </div>
                    <div class="summary-item" style="grid-column: span 2;">
                        <div class="summary-label">Last Refresh Time</div>
                        <div class="summary-value small">${formatTimestamp(data.timestamp)}</div>
                    </div>
                </div>`;
        }

        /** Update D3 node colors without recreating the graph */
        function updateTopology(data) {
            const colorMap = buildNodeColorMap(data);
            node.selectAll('circle')
                .attr('fill', d => colorMap[d.id] || COLORS.healthy);
        }

        /* ================================================================
           Main polling orchestrator — fetches /api/metrics every 3 s
           ================================================================ */
        function updateMetrics() {
            fetch('/api/metrics')
                .then(res => res.json())
                .then(data => {
                    updateStatus(data);
                    updateLastUpdated(data);
                    updateLatency(data);
                    updateSwitchStats(data);
                    updateAlerts(data);
                    updateSummary(data);
                    updateTopology(data);
                })
                .catch(err => {
                    console.error('Metrics fetch failed:', err);
                });
        }

        // Poll every 3 seconds — no WebSockets
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
    # Port 5000 is reserved by macOS AirPlay Receiver; use 5001 instead
    app.run(host='0.0.0.0', port=5001, debug=True)
