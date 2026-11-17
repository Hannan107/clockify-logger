"""
Clockify API Client for Enduring Planet
Handles authentication, time entry logging, and summary report pulling.
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

# Default Enduring Planet Configuration
DEFAULT_WORKSPACE_ID = "664b8b436c802f03913c146b"  # Daim Ashraf's workspace
DEFAULT_USER_ID = "6784f10c3fb6a444eea050f1"       # Abdul Hannan
DEFAULT_TIMEZONE_OFFSET = "+05:00"                  # Asia/Karachi (PKT, UTC+5)

# Clockify Project Reference
PROJECT_DIRECTORY = {
    "Enduring Planet - Accounting": {
        "projectId": "6808d297762e83002bb17fa6",
        "bucket": "Internal — No Bucket",
        "is_billable": False,
    },
    "GFC": {
        "projectId": "68ed1012021cce63b89a5c97",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": [
            "gfc", "spark", "sparkcharge", "spark media", "mk properties", "mk",
            "stone soup", "mobilus", "solo", "clever carbon", "workmorphis", "marc & marty"
        ],
    },
    "Switch Maritime": {
        "projectId": "68a5ee7a8802625f8119456f",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["switch maritime", "switch"],
    },
    "Com-sec": {
        "projectId": "6a9ea402bd88c3b07d48c2ed",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["com-sec", "comsec"],
    },
    "Action Figure": {
        "projectId": "69cd7320668874a429934189",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["action figure"],
    },
    "Circ": {
        "projectId": "6a678f08fafec6793207e9f0",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["circ"],
    },
    "Everfleet": {
        "projectId": "6a0ae36892ac7d47e76e6a04",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["everfleet"],
    },
    "Guidewheel": {
        "projectId": "69c4fe8f368afc35dd8c101e",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["guidewheel"],
    },
    "GreenWealth": {
        "projectId": "6957b1e397b626130b6ed145",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["greenwealth", "green wealth"],
    },
    "Indow Windows": {
        "projectId": "6960faf38e0a1a510e12397a",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["indow windows", "indow"],
    },
    "EkoabyLingrove": {
        "projectId": "6a148db9c1e1b5ce82d7e1c9",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["ekoabylingrove", "lingrove", "ekoa"],
    },
    "Axiom Cloud": {
        "projectId": "6659c08a30b50c70e1632b92",
        "bucket": "Monthly Bookkeeping",
        "is_billable": True,
        "aliases": ["axiom cloud", "axiom"],
    },
    "Channing Copper": {
        "projectId": "68417662bfe455328cc2048d",
        "bucket": "Monthly Bookkeeping",
        "is_billable": True,
        "aliases": ["channing copper", "copper"],
    },
    "capture6": {
        "projectId": "68628aa1ccb8b35162173dbd",
        "bucket": "Monthly Bookkeeping",
        "is_billable": True,
        "aliases": ["capture6", "capture 6"],
    },
    "The Worker Agency": {
        "projectId": "6ac7941d7afa036505f885f5",
        "bucket": "Modelling and Proforma",
        "is_billable": True,
        "aliases": ["the worker agency", "worker agency"],
    },
    "Propagate": {
        "projectId": "6a0b1df35573c2819eae92f7",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["propagate"],
    },
    "Altasea": {
        "projectId": "69dcaf3e7617f51a95b6eca9",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["altasea"],
    },
    "Agrology": {
        "projectId": "6aa40a5fb921dda50aab4f3c",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["agrology"],
    },
    "Conductor Collective": {
        "projectId": "6ad7eac2072c5434747aaea9",
        "bucket": "B&A Retainer Services",
        "is_billable": True,
        "aliases": ["conductor collective", "conductor"],
    },
    "Community Systems Solutions (CSS)": {
        "projectId": "68dc3be0fb5b7c16f23555a9",
        "bucket": "Monthly Bookkeeping",
        "is_billable": True,
        "aliases": ["community systems solutions", "css"],
    },
}


class ClockifyClient:
    def __init__(self, api_token=None, workspace_id=DEFAULT_WORKSPACE_ID, user_id=DEFAULT_USER_ID):
        self.api_token = api_token or os.environ.get("CLOCKIFY_API_TOKEN")
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.base_url = "https://global.api.clockify.me"
        self.reports_url = "https://reports.api.clockify.me/v1"

    def _get_headers(self):
        if not self.api_token:
            raise ValueError(
                "Clockify API token is not set. Provide it directly or set the CLOCKIFY_API_TOKEN environment variable."
            )
        return {
            "X-Auth-Token": self.api_token,
            "X-Api-Key": self.api_token,
            "Content-Type": "application/json",
        }

    def resolve_project(self, query):
        """
        Resolves project name, alias, or GFC sub-client to the exact Clockify projectId.
        """
        query_norm = query.strip().lower()
        for proj_name, meta in PROJECT_DIRECTORY.items():
            if query_norm == proj_name.lower():
                return proj_name, meta["projectId"], meta["bucket"]
            for alias in meta.get("aliases", []):
                if query_norm == alias or alias in query_norm:
                    return proj_name, meta["projectId"], meta["bucket"]
        return None, None, None

    def get_time_entries(self, page=0, limit=50):
        """
        Fetches existing time entries for the user from Clockify REST API.
        """
        url = f"{self.base_url}/workspaces/{self.workspace_id}/timeEntries/user/{self.user_id}/full"
        params = {"page": page, "limit": limit}
        res = requests.get(url, headers=self._get_headers(), params=params)
        res.raise_for_status()
        return res.json()

    def create_time_entry(self, date_str, start_pkt, end_pkt, project_id, description, billable=True):
        """
        Pushes a new time entry to Clockify with proper PKT (+05:00) ISO strings.
        Handles midnight rollover (e.g. 23:40-00:00 -> 23:39-23:59) so entry stays on same workday.
        """
        # Midnight adjustment
        if end_pkt in ["00:00", "24:00"]:
            end_time_str = f"{date_str}T23:59:00{DEFAULT_TIMEZONE_OFFSET}"
        else:
            end_time_str = f"{date_str}T{end_pkt}:00{DEFAULT_TIMEZONE_OFFSET}"

        start_time_str = f"{date_str}T{start_pkt}:00{DEFAULT_TIMEZONE_OFFSET}"

        # Parse and convert to UTC ISO string
        start_dt = datetime.fromisoformat(start_time_str)
        end_dt = datetime.fromisoformat(end_time_str)

        start_iso = start_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_iso = end_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f"{self.base_url}/workspaces/{self.workspace_id}/timeEntries"
        payload = {
            "description": description,
            "projectId": project_id,
            "taskId": None,
            "billable": billable,
            "start": start_iso,
            "end": end_iso,
            "tagIds": [],
            "customFields": [],
        }

        res = requests.post(url, headers=self._get_headers(), json=payload)
        res.raise_for_status()
        return res.json()

    def get_summary_report(self, start_date, end_date):
        """
        Pulls Clockify Summary Report using literal calendar date strings.
        CRITICAL: Never shift by -5h for Reports API, as Clockify backend already
        applies the profile timezone (Asia/Karachi).
        Format: YYYY-MM-DDT00:00:00.000Z to YYYY-MM-DDT23:59:59.999Z
        """
        url = f"{self.reports_url}/workspaces/{self.workspace_id}/reports/summary"
        payload = {
            "dateRangeStart": f"{start_date}T00:00:00.000Z",
            "dateRangeEnd": f"{end_date}T23:59:59.999Z",
            "summaryFilter": {
                "groups": ["PROJECT", "CLIENT", "USER"]
            }
        }
        res = requests.post(url, headers=self._get_headers(), json=payload)
        res.raise_for_status()
        return res.json()
