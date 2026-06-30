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
            grid-template-columns: 1fr 380px;
            gap: 18px;
            align-items: start;
        }

        @media (max-width: 1200px) {
            .grid-container {
                grid-template-columns: 1fr 340px;
            }
        }

        @media (max-width: 1024px) {
            .grid-container {
                grid-template-columns: 1fr;
            }
        }

        .left-column,
        .right-column {
            display: flex;
            flex-direction: column;
            gap: 16px;
            min-width: 0;
        }

        .right-column {
            position: sticky;
            top: 16px;
        }

        @media (max-width: 1024px) {
            .right-column {
                position: static;
            }
        }

        /* ── Panels ────────────────────────────────────────────────── */
        .panel {
            background-color: #1e1e24;
            border: 1px solid #2d2d34;
            border-radius: 8px;
            padding: 18px;
            transition: border-color 0.15s ease;
        }

        .panel:hover {
            border-color: #3d3d48;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            padding-bottom: 12px;
            border-bottom: 1px solid #2d2d34;
        }

        .panel-title {
            margin: 0;
            font-size: 12px;
            font-weight: 700;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .panel-count {
            font-size: 11px;
            color: #94a3b8;
            background-color: #121214;
            padding: 3px 10px;
            border-radius: 4px;
            border: 1px solid #2d2d34;
            font-variant-numeric: tabular-nums;
        }

        /* ── Status Indicators ──────────────────────────────────────── */
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            flex-shrink: 0;
        }

        .status-dot.healthy  { background-color: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.4); }
        .status-dot.warning  { background-color: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.4); }
        .status-dot.critical { background-color: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.4); }
        .status-dot.info     { background-color: #3b82f6; box-shadow: 0 0 6px rgba(59, 130, 246, 0.4); }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid transparent;
        }

        .status-pill.healthy  { color: #10b981; background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.25); }
        .status-pill.warning  { color: #f59e0b; background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.25); }
        .status-pill.critical { color: #ef4444; background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.25); }

        /* ── Tables ───────────────────────────────────────────────── */
        .table-wrapper {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border: 1px solid #2d2d34;
            border-radius: 6px;
            background-color: #121214;
        }

        .table-wrapper::-webkit-scrollbar { height: 5px; }
        .table-wrapper::-webkit-scrollbar-track { background: #121214; }
        .table-wrapper::-webkit-scrollbar-thumb { background: #2d2d34; border-radius: 3px; }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 280px;
        }

        .data-table th,
        .data-table td {
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid #2d2d34;
            font-size: 12px;
            line-height: 1.4;
        }

        .data-table th {
            color: #94a3b8;
            font-weight: 600;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            background-color: #1a1a1f;
            white-space: nowrap;
        }

        .data-table tbody tr:nth-child(even) {
            background-color: rgba(30, 30, 36, 0.5);
        }

        .data-table tbody tr:hover {
            background-color: rgba(59, 130, 246, 0.07);
        }

        .data-table tbody tr:last-child td {
            border-bottom: none;
        }

        .cell-with-status {
            display: inline-flex;
            align-items: center;
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
            display: flex;
            align-items: center;
            gap: 6px;
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

        /* ── SOAR Response ──────────────────────────────────────────── */
        .soar-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 420px;
            overflow-y: auto;
        }

        .soar-card {
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-left: 4px solid #3b82f6;
            border-radius: 4px;
            padding: 12px 14px;
        }

        .soar-card:hover {
            border-color: #3d3d48;
        }

        .soar-card.sev-critical { border-left-color: #ef4444; }
        .soar-card.sev-high     { border-left-color: #f59e0b; }
        .soar-card.sev-medium   { border-left-color: #eab308; }
        .soar-card.sev-info     { border-left-color: #3b82f6; }

        .soar-playbook {
            font-size: 13px;
            font-weight: 600;
            color: #3b82f6;
            margin-bottom: 8px;
        }

        .soar-summary {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2d2d34;
        }

        .soar-mitre {
            margin-top: 10px;
            padding: 10px 12px;
            background-color: rgba(59, 130, 246, 0.06);
            border: 1px solid #2d2d34;
            border-radius: 4px;
        }

        .soar-mitre-title {
            font-size: 10px;
            font-weight: 700;
            color: #3b82f6;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 8px;
        }

        .soar-mitre-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 4px;
            font-size: 12px;
        }

        .soar-mitre-row:last-child {
            margin-bottom: 0;
        }

        .soar-mitre-label {
            color: #94a3b8;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            flex-shrink: 0;
        }

        .soar-mitre-value {
            color: #e2e8f0;
            text-align: right;
            font-weight: 500;
        }

        .soar-mitre-id {
            color: #64748b;
            font-weight: 400;
        }

        .soar-field {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 5px;
            font-size: 12px;
        }

        .soar-field-label {
            color: #94a3b8;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            flex-shrink: 0;
        }

        .soar-field-value {
            color: #e2e8f0;
            text-align: right;
            font-weight: 500;
        }

        .soar-field-value.sev-critical { color: #ef4444; font-weight: 600; }
        .soar-field-value.sev-high     { color: #f59e0b; font-weight: 600; }
        .soar-field-value.sev-medium   { color: #eab308; font-weight: 600; }
        .soar-field-value.sev-info     { color: #3b82f6; font-weight: 600; }
        .soar-field-value.status-open  { color: #3b82f6; font-weight: 600; }

        .soar-actions {
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid #2d2d34;
        }

        .soar-actions-label {
            font-size: 10px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }

        .soar-actions-list {
            margin: 0;
            padding: 0 0 0 16px;
            list-style: disc;
        }

        .soar-actions-list li {
            font-size: 12px;
            color: #cbd5e1;
            line-height: 1.5;
            margin-bottom: 3px;
        }

        .soar-timestamp {
            margin-top: 8px;
            font-size: 11px;
            color: #64748b;
            text-align: right;
        }

        .no-soar {
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            padding: 24px 12px;
            border: 1px dashed #2d2d34;
            border-radius: 4px;
        }

        .soar-container::-webkit-scrollbar { width: 5px; }
        .soar-container::-webkit-scrollbar-track { background: #121214; }
        .soar-container::-webkit-scrollbar-thumb { background: #2d2d34; border-radius: 3px; }

        /* ── Enterprise Summary ───────────────────────────────────── */
        .summary-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .summary-item {
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-radius: 6px;
            padding: 12px 14px;
        }

        .summary-item:hover {
            border-color: #3d3d48;
        }

        .summary-label {
            font-size: 10px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .summary-value {
            font-size: 18px;
            font-weight: 600;
            color: #e2e8f0;
            line-height: 1.3;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .summary-value.small {
            font-size: 12px;
            font-weight: 500;
            line-height: 1.4;
        }

        /* ── Topology ───────────────────────────────────────────────── */
        .topology-panel {
            flex-shrink: 0;
        }

        #topology-map {
            width: 100%;
            height: 480px;
            background-color: #121214;
            border: 1px solid #2d2d34;
            border-radius: 6px;
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
            stroke-opacity: 0.75;
            stroke-width: 1.5px;
            transition: stroke 0.4s ease, stroke-width 0.4s ease;
        }

        .text-labels {
            font-size: 11px;
            fill: #cbd5e1;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 500;
            pointer-events: none;
            user-select: none;
        }

        .topology-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 12px 18px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #2d2d34;
        }

        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #94a3b8;
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

    <!-- Main dashboard layout -->
    <div class="grid-container">

        <!-- LEFT: Topology + telemetry tables -->
        <div class="left-column">

            <!-- Network Topology -->
            <div class="panel topology-panel">
                <div class="panel-header">
                    <h3 class="panel-title">Network Topology</h3>
                    <span class="panel-count" id="topology-node-count">17 nodes</span>
                </div>
                <div id="topology-map"></div>
                <div class="topology-legend">
                    <span class="legend-item"><span class="status-dot healthy"></span> Healthy</span>
                    <span class="legend-item"><span class="status-dot warning"></span> Packet Loss</span>
                    <span class="legend-item"><span class="status-dot critical"></span> Critical / Firewall</span>
                    <span class="legend-item"><span class="status-dot" style="background:#eab308;box-shadow:0 0 6px rgba(234,179,8,0.4);"></span> Latency Alert</span>
                </div>
            </div>

            <!-- Host Latency -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Host Latency</h3>
                </div>
                <div id="latency-panel">
                    <span class="loading-text">Connecting to telemetry stream...</span>
                </div>
            </div>

            <!-- OVS Switch Statistics -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">OVS Switch Statistics</h3>
                </div>
                <div id="switch-panel">
                    <span class="loading-text">Parsing OpenFlow pipeline...</span>
                </div>
            </div>

        </div>

        <!-- RIGHT: Security & response sidebar -->
        <div class="right-column">

            <!-- Active Security Alerts -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Active Security Alerts</h3>
                    <span class="panel-count" id="alert-count">0</span>
                </div>
                <div id="alerts-panel">
                    <span class="loading-text">Scanning security events...</span>
                </div>
            </div>

            <!-- SOAR Response -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">SOAR Response</h3>
                    <span class="panel-count" id="soar-count">0</span>
                </div>
                <div id="soar-panel">
                    <span class="loading-text">Loading incident playbooks...</span>
                </div>
            </div>

            <!-- Enterprise Summary -->
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Enterprise Summary</h3>
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
        const DEFAULT_LINK_COLOR    = '#3d3d48';
        const DEFAULT_LINK_WIDTH    = 1.5;
        const ALERT_LINK_WIDTH      = 2.5;

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
        let topoHeight = 480;

        const svg = d3.select("#topology-map")
            .append("svg")
            .attr("width", topoWidth)
            .attr("height", topoHeight);

        const simulation = d3.forceSimulation(topologyData.nodes)
            .force("link", d3.forceLink(topologyData.links).id(d => d.id).distance(130))
            .force("charge", d3.forceManyBody().strength(-420))
            .force("center", d3.forceCenter(topoWidth / 2, topoHeight / 2))
            .force("collision", d3.forceCollide().radius(30))
            .force("x", d3.forceX(topoWidth / 2).strength(0.04))
            .force("y", d3.forceY(topoHeight / 2).strength(0.04));

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
            .attr("r", 11)
            .attr("fill", COLORS.healthy);

        node.append("text")
            .attr("class", "text-labels")
            .attr("dx", 15)
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
            topoHeight = Math.max(420, topoContainer.clientHeight || 480);
            svg.attr("width", topoWidth).attr("height", topoHeight);
            simulation.force("center", d3.forceCenter(topoWidth / 2, topoHeight / 2));
            simulation.force("x", d3.forceX(topoWidth / 2).strength(0.04));
            simulation.force("y", d3.forceY(topoHeight / 2).strength(0.04));
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

        /** Map numeric health state to status-dot CSS class */
        function statusLevel(cls) {
            if (cls === 'val-critical') return 'critical';
            if (cls === 'val-warning')  return 'warning';
            if (cls === 'val-info')     return 'info';
            return 'healthy';
        }

        /** Render inline status dot */
        function statusDot(level) {
            return `<span class="status-dot ${level}"></span>`;
        }

        /** Resolve link endpoint id (handles post-simulation object refs) */
        function linkNodeId(endpoint) {
            return typeof endpoint === 'object' ? endpoint.id : endpoint;
        }

        /** True when firewall is in alert state */
        function isFirewallAlert(data) {
            const fw = data.firewall || {};
            if (fw.status !== 'Active / Enforcing') return true;
            return (data.alerts || []).some(alert =>
                alert.affected_device === 'fw1' &&
                normalizeSeverity(alert.severity) === 'CRITICAL'
            );
        }

        /** True when link is part of the firewall ingress/egress path */
        function isFirewallLink(d) {
            const src = linkNodeId(d.source);
            const tgt = linkNodeId(d.target);
            return (src === 'Internet' && tgt === 'fw1') ||
                   (src === 'fw1' && tgt === 's1');
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

            let html = '<div class="table-wrapper"><table class="data-table"><thead><tr>' +
                '<th>Host</th><th>Status</th><th>Latency</th></tr></thead><tbody>';

            for (const [host, val] of Object.entries(stats)) {
                let cls = 'val-healthy';
                if (val.includes('Timeout') || val.includes('Unavailable')) {
                    cls = 'val-critical';
                } else {
                    const num = parseFloat(val);
                    if (!isNaN(num) && num > LATENCY_THRESHOLD) cls = 'val-warning';
                }
                const level = statusLevel(cls);
                html += `<tr>
                    <td><span class="cell-with-status">${statusDot(level)}${host}</span></td>
                    <td><span class="status-pill ${level}">${level.charAt(0).toUpperCase() + level.slice(1)}</span></td>
                    <td class="${cls}">${val}</td>
                </tr>`;
            }

            html += '</tbody></table></div>';
            container.innerHTML = html;
        }

        /** Update OVS switch statistics table */
        function updateSwitchStats(data) {
            const container = document.getElementById('switch-panel');
            const stats = data.switch_stats || {};

            let html = '<div class="table-wrapper"><table class="data-table"><thead><tr>' +
                '<th>Switch</th><th>Port</th><th>RX Packets</th>' +
                '<th>TX Packets</th><th>Packet Loss</th></tr></thead><tbody>';

            let hasRows = false;
            for (const [sw, ports] of Object.entries(stats)) {
                ports.forEach(p => {
                    if (p.port === 'LOCAL') return;
                    hasRows = true;
                    const lossCls = p.packet_loss_pct > PACKET_LOSS_THRESHOLD
                        ? 'val-critical' : 'val-healthy';
                    const level = statusLevel(lossCls);
                    html += `<tr>
                        <td><span class="cell-with-status">${statusDot(level)}${sw}</span></td>
                        <td>${p.port}</td>
                        <td>${p.rx_packets.toLocaleString()}</td>
                        <td>${p.tx_packets.toLocaleString()}</td>
                        <td class="${lossCls}">
                            <span class="status-pill ${level}">${p.packet_loss_pct}%</span>
                        </td>
                    </tr>`;
                });
            }

            html += '</tbody></table></div>';
            container.innerHTML = hasRows
                ? html
                : '<span class="loading-text">No OpenFlow statistics available</span>';
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
                    <div class="alert-severity ${cls}">
                        ${statusDot(cls === 'info' ? 'info' : cls)}${alert.severity}
                    </div>
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

        /** Format MITRE ATT&CK tactic/technique with ID */
        function formatMitreEntry(name, id) {
            if (!name && !id) return 'N/A';
            if (name && id) return `${name} <span class="soar-mitre-id">(${id})</span>`;
            return name || id;
        }

        /** Build MITRE ATT&CK section HTML for an incident */
        function buildMitreSection(mitre) {
            if (!mitre || typeof mitre !== 'object') {
                return `<div class="soar-mitre">
                    <div class="soar-mitre-title">MITRE ATT&amp;CK</div>
                    <div class="soar-mitre-row">
                        <span class="soar-mitre-label">Tactic</span>
                        <span class="soar-mitre-value">N/A</span>
                    </div>
                    <div class="soar-mitre-row">
                        <span class="soar-mitre-label">Technique</span>
                        <span class="soar-mitre-value">N/A</span>
                    </div>
                </div>`;
            }
            return `<div class="soar-mitre">
                <div class="soar-mitre-title">MITRE ATT&amp;CK</div>
                <div class="soar-mitre-row">
                    <span class="soar-mitre-label">Tactic</span>
                    <span class="soar-mitre-value">${formatMitreEntry(mitre.tactic, mitre.tactic_id)}</span>
                </div>
                <div class="soar-mitre-row">
                    <span class="soar-mitre-label">Technique</span>
                    <span class="soar-mitre-value">${formatMitreEntry(mitre.technique, mitre.technique_id)}</span>
                </div>
            </div>`;
        }

        /** Update SOAR incident playbooks panel */
        function updateSOAR(incidents) {
            const container  = document.getElementById('soar-panel');
            const countBadge = document.getElementById('soar-count');
            const items      = incidents || [];

            countBadge.textContent = items.length;

            if (items.length === 0) {
                container.innerHTML =
                    '<div class="no-soar">No Active Playbooks</div>';
                return;
            }

            let html = '<div class="soar-container">';
            items.forEach(incident => {
                const sevCls  = severityClass(incident.severity);
                const actions = incident.recommended_actions || [];
                const summary = incident.summary || incident.description || '';

                html += `<div class="soar-card sev-${sevCls}">
                    <div class="soar-field">
                        <span class="soar-field-label">Incident ID</span>
                        <span class="soar-field-value">${incident.incident_id || 'N/A'}</span>
                    </div>
                    <div class="soar-field">
                        <span class="soar-field-label">Severity</span>
                        <span class="soar-field-value sev-${sevCls}">${incident.severity || 'Unknown'}</span>
                    </div>
                    <div class="soar-field">
                        <span class="soar-field-label">Status</span>
                        <span class="soar-field-value status-open">${incident.status || 'Open'}</span>
                    </div>
                    <div class="soar-field">
                        <span class="soar-field-label">Playbook</span>
                        <span class="soar-field-value" style="color:#3b82f6;font-weight:600;">${incident.playbook || 'General Investigation'}</span>
                    </div>
                    ${summary ? `<div class="soar-summary"><span class="soar-field-label" style="display:block;margin-bottom:4px;">Summary</span>${summary}</div>` : ''}
                    ${buildMitreSection(incident.mitre)}
                    <div class="soar-actions">
                        <div class="soar-actions-label">Recommended Actions</div>
                        <ul class="soar-actions-list">
                            ${actions.length
                                ? actions.map(action => `<li>${action}</li>`).join('')
                                : '<li>No actions defined</li>'}
                        </ul>
                    </div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        /** Update enterprise summary panel */
        function updateSummary(data) {
            const container = document.getElementById('summary-panel');
            const latencyStats = data.latency_stats || {};
            const switchStats  = data.switch_stats || {};
            const alerts       = data.alerts || [];
            const incidents    = data.incidents || [];
            const fw           = data.firewall || {};

            const totalHosts    = Object.keys(latencyStats).length;
            const totalSwitches = Object.keys(switchStats).length;
            const fwStatus      = fw.status || 'Unknown';
            const fwHealthy     = fwStatus === 'Active / Enforcing';
            const fwCls         = fwHealthy ? 'healthy' : 'critical';
            const alertCls      = alerts.length > 0 ? 'warning' : 'healthy';

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
                        <div class="summary-value small">
                            ${statusDot(fwCls)}
                            <span class="${fwHealthy ? 'val-healthy' : 'val-critical'}">${fwStatus}</span>
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Active Alerts</div>
                        <div class="summary-value">
                            ${statusDot(alertCls)}
                            <span class="${alerts.length > 0 ? 'val-warning' : ''}">${alerts.length}</span>
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">SOAR Incidents</div>
                        <div class="summary-value">
                            ${statusDot(incidents.length > 0 ? 'info' : 'healthy')}
                            ${incidents.length}
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Last Refresh</div>
                        <div class="summary-value small">${formatTimestamp(data.timestamp)}</div>
                    </div>
                </div>`;
        }

        /** Update D3 node and link colors without recreating the graph */
        function updateTopology(data) {
            const colorMap = buildNodeColorMap(data);
            const fwAlert  = isFirewallAlert(data);

            node.selectAll('circle')
                .attr('fill', d => colorMap[d.id] || COLORS.healthy);

            link
                .attr('stroke', d => (fwAlert && isFirewallLink(d))
                    ? COLORS.critical : DEFAULT_LINK_COLOR)
                .attr('stroke-width', d => (fwAlert && isFirewallLink(d))
                    ? ALERT_LINK_WIDTH : DEFAULT_LINK_WIDTH);
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
                    updateSOAR(data.incidents);
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
