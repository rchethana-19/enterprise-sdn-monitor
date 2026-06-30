#!/usr/bin/env python3
"""
MITRE ATT&CK Mapper

Maps detected security alerts to the corresponding
MITRE ATT&CK tactic and technique.
"""


class MITREMapper:

    def __init__(self):

        self.mapping = {

            "Firewall": {
                "tactic": "Defense Evasion",
                "tactic_id": "TA0005",
                "technique": "Impair Defenses",
                "technique_id": "T1562"
            },

            "Network": {
                "tactic": "Impact",
                "tactic_id": "TA0040",
                "technique": "Network Denial of Service",
                "technique_id": "T1498"
            },

            "Performance": {
                "tactic": "Impact",
                "tactic_id": "TA0040",
                "technique": "Endpoint Denial of Service",
                "technique_id": "T1499"
            },

            "Reconnaissance": {
                "tactic": "Reconnaissance",
                "tactic_id": "TA0043",
                "technique": "Active Scanning",
                "technique_id": "T1595"
            },

            "Credential Access": {
                "tactic": "Credential Access",
                "tactic_id": "TA0006",
                "technique": "Brute Force",
                "technique_id": "T1110"
            }

        }

    def enrich(self, alert):

        category = alert.get("category", "")

        mitre = self.mapping.get(category)

        if mitre:
            alert["mitre"] = mitre

        else:
            alert["mitre"] = {
                "tactic": "Unknown",
                "tactic_id": "-",
                "technique": "Unknown",
                "technique_id": "-"
            }

        return alert
