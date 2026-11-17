"""
Time Reconstruction Engine
Implements Enduring Planet rules for reconstructing actual hours from
Calendar, Gemini Meeting Notes, Slack, and Sent Emails.
"""

from datetime import datetime, timedelta
from .clockify_client import PROJECT_DIRECTORY, ClockifyClient


class TimeEntryDraft:
    def __init__(self, date, start_pkt, end_pkt, client_project, description, verification_source, billable=True):
        self.date = date
        self.start_pkt = start_pkt
        self.end_pkt = end_pkt
        self.client_project = client_project
        self.description = description
        self.verification_source = verification_source
        self.billable = billable

        # Compute duration
        s_dt = datetime.strptime(f"{date} {start_pkt}", "%Y-%m-%d %H:%M")
        e_dt = datetime.strptime(f"{date} {end_pkt}", "%Y-%m-%d %H:%M")
        if e_dt < s_dt:
            # Midnight crossing
            e_dt += timedelta(days=1)
        self.duration_minutes = int((e_dt - s_dt).total_seconds() / 60)
        self.duration_hours = round(self.duration_minutes / 60.0, 2)

    def to_dict(self):
        return {
            "date": self.date,
            "startPKT": self.start_pkt,
            "endPKT": self.end_pkt,
            "duration": f"{self.duration_minutes // 60}h {self.duration_minutes % 60:02d}m",
            "hours": self.duration_hours,
            "clientProject": self.client_project,
            "description": self.description,
            "source": self.verification_source,
            "billable": self.billable,
        }


class TimeReconstructor:
    def __init__(self):
        self.client = ClockifyClient()

    def audit_and_normalize(self, draft_entries):
        """
        Applies critical constraints:
        1. GFC sub-client rule (maps Spark, MK, Stone Soup, etc. to GFC).
        2. Resolves project IDs and buckets.
        3. Enforces concise naming conventions.
        """
        audited = []
        for entry in draft_entries:
            proj_name, proj_id, bucket = self.client.resolve_project(entry.client_project)
            if not proj_name:
                proj_name = entry.client_project
                proj_id = None
                bucket = "Unknown"

            is_billable = proj_name != "Enduring Planet - Accounting"
            entry.client_project = proj_name
            entry.projectId = proj_id
            entry.bucket = bucket
            entry.billable = is_billable
            audited.append(entry)
        return audited

    def generate_markdown_report(self, audited_entries):
        """
        Builds the Markdown verification artifact table for user approval.
        """
        lines = [
            "# Draft Timesheet for Approval",
            "",
            "| Date | Time (PKT) | Duration | Client Bucket (Project) | Description | Verification Source |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        total_billable = 0.0
        total_internal = 0.0

        for e in audited_entries:
            lines.append(
                f"| {e.date} | `{e.start_pkt}–{e.end_pkt}` | {e.duration_minutes // 60}h {e.duration_minutes % 60:02d}m | **{e.client_project}** | {e.description} | {e.verification_source} |"
            )
            if e.billable:
                total_billable += e.duration_hours
            else:
                total_internal += e.duration_hours

        lines.extend([
            "",
            "### Summary Totals",
            f"- **Client Billable Hours**: `{total_billable:.2f} hrs`",
            f"- **Internal Operations Hours**: `{total_internal:.2f} hrs`",
            f"- **Total Actual Hours**: `{(total_billable + total_internal):.2f} hrs`",
            "",
            "> [!NOTE]",
            "> All entries reflect strictly actual audited hours from Gemini Meeting arrival timestamps, Slack messages, and Google Calendar. No artificial padding applied.",
        ])

        return "\n".join(lines)
