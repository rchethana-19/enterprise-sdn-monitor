#!/usr/bin/env python3
"""
OVS-Vision SOAR Engine

Receives security alerts from monitor.py and generates
incident playbooks with recommended response actions.
"""

from datetime import datetime
import uuid


class SOAREngine:

    def __init__(self):
        pass

    def generate_incident_id(self):
        """
        Generate a unique incident ID.
        Example:
        INC-7A2C9F1B
        """
        return "INC-" + uuid.uuid4().hex[:8].upper()

    def generate_playbook(self, alert):
        """
        Convert a security alert into an incident playbook.
        """

        incident = {
            "incident_id": self.generate_incident_id(),
            "timestamp": datetime.now().isoformat(),
            "status": "Open",
            "severity": alert.get("severity", "Unknown"),
            "category": alert.get("category", "General"),
            "title": alert.get("title", ""),
            "affected_device": alert.get("affected_device", ""),
            "description": alert.get("description", ""),
            "playbook": "",
            "recommended_actions": [],
            "mitre": alert.get("mitre", {})
        }
        

        category = alert.get("category", "").lower()

        # -------------------------
        # Firewall Playbook
        # -------------------------

        if category == "firewall":

            incident["playbook"] = "Firewall Recovery"
            incident["summary"] = (
                "Potential defense evasion activity detected. "
                "Review firewall integrity and security controls."
            )

            incident["recommended_actions"] = [
                "Verify firewall service is running",
                "Inspect firewall rules",
                "Review recent configuration changes",
                "Check system logs",
                "Notify SOC analyst"
            ]

        # -------------------------
        # Network Playbook
        # -------------------------

        elif category == "network":

            incident["playbook"] = "Network Investigation"
            incident["summary"] = (
                "Traffic patterns indicate a possible denial-of-service event."
            )
            incident["recommended_actions"] = [
                "Inspect switch interfaces",
                "Review OpenFlow statistics",
                "Capture network traffic",
                "Check interface utilization",
                "Escalate if packet loss persists"
            ]

        # -------------------------
        # Performance Playbook
        # -------------------------

        elif category == "performance":

            incident["playbook"] = "Performance Investigation"
            incident["summary"] = (
                "Performance degradation detected. Verify resource utilization and connectivity."
            )
            incident["recommended_actions"] = [
                "Verify host connectivity",
                "Inspect routing path",
                "Review system load",
                "Check bandwidth utilization",
                "Continue monitoring"
            ]

        else:

            incident["playbook"] = "General Investigation"

            incident["recommended_actions"] = [
                "Collect additional logs",
                "Review telemetry",
                "Notify administrator"
            ]

        return incident
