"""
Google Sheet Hour Tracking Sync Module
Maps Clockify Summary Reports to the "Client List for hour tracking" Google Sheet.
"""

SPREADSHEET_ID = "1N4Efs53vgQy53XdA2JRXVQdnBDK3L6R7J6a3rMvN3Vc"
WEEKLY_GID = "0"
MONTHLY_GID = "738345283"
SOURCE_DATA_GID = "1724263041"

# Target Rows for Abdul's Pod (Bookkeepers: Ramish, Hamza, Alyan)
POD_ROW_MAPPINGS = {
    "Rows 2–5 (GFC Crane / MK / Spark / Stone Soup)": {
        "projects": ["GFC"],
        "included_buckets": ["B&A Retainer Services", "Payroll Management", "AP Management"],
        "excluded_buckets": [],
    },
    "Row 6 (CTRL-S)": {
        "projects": ["CTRL-S", "CTRL-S Inc"],
        "included_buckets": ["B&A Retainer Services"],
        "excluded_buckets": [],
    },
    "Row 7 (Circ)": {
        "projects": ["Circ"],
        "included_buckets": ["B&A Retainer Services", "AP Management"],
        "excluded_buckets": ["Understanding system/Correcting EP mistake"],
    },
    "Row 8 (Com-Sec)": {
        "projects": ["Com-sec", "Com-Sec"],
        "included_buckets": ["B&A Retainer Services"],
        "excluded_buckets": [],
    },
    "Row 10 (Copper)": {
        "projects": ["Channing Copper", "Copper"],
        "included_buckets": ["Monthly Bookkeeping", "AP Management"],
        "excluded_buckets": ["Understanding system/Correcting EP mistake"],
    },
    "Row 11 (NGON)": {
        "projects": ["NGON"],
        "included_buckets": ["Monthly Bookkeeping", "B&A Retainer Services"],
        "excluded_buckets": [],
    },
    "Row 12 (Switch Maritime)": {
        "projects": ["Switch Maritime", "Switch"],
        "included_buckets": ["B&A Retainer Services", "AP Management"],
        "excluded_buckets": [],
    },
    "Row 13 (Everfleet)": {
        "projects": ["Everfleet"],
        "included_buckets": ["B&A Retainer Services"],
        "excluded_buckets": [],
    },
    "Row 18 (Capture6)": {
        "projects": ["capture6", "Capture 6"],
        "included_buckets": ["Monthly Bookkeeping"],
        "excluded_buckets": ["Cash Budget", "Understanding system/Correcting EP mistake"],
    },
    "Row 19 (Greenwealth)": {
        "projects": ["GreenWealth", "Greenwealth"],
        "included_buckets": ["B&A Retainer Services"],
        "excluded_buckets": [],
    },
}

GLOBAL_EXCLUDED_BUCKETS = [
    "Understanding system/Correcting EP mistake",
    "Cash Budget",
    "FP&A Retainer Services",
    "Modelling and Proforma",
    "KPI Dashboard",
]


class SheetHourAggregator:
    @staticmethod
    def filter_and_aggregate(summary_report_items):
        """
        Processes Clockify summary report data items, applies pod row mappings and exclusion rules,
        and returns aggregated decimal hours per client row for Abdul's pod.
        """
        results = {}
        for row_label, config in POD_ROW_MAPPINGS.items():
            results[row_label] = {
                "total_seconds": 0,
                "decimal_hours": 0.0,
                "included_entries": [],
            }

        for item in summary_report_items:
            project_name = item.get("name") or item.get("projectName", "")
            client_bucket = item.get("clientName", "")
            duration = item.get("duration", 0)  # in seconds

            # Check global exclusions
            if any(excl.lower() in client_bucket.lower() for excl in GLOBAL_EXCLUDED_BUCKETS):
                continue

            # Match against row mappings
            for row_label, config in POD_ROW_MAPPINGS.items():
                project_match = any(p.lower() in project_name.lower() for p in config["projects"])
                bucket_match = any(b.lower() in client_bucket.lower() for b in config["included_buckets"])
                bucket_excluded = any(eb.lower() in client_bucket.lower() for eb in config["excluded_buckets"])

                if project_match and bucket_match and not bucket_excluded:
                    results[row_label]["total_seconds"] += duration
                    results[row_label]["included_entries"].append({
                        "project": project_name,
                        "bucket": client_bucket,
                        "duration_hours": round(duration / 3600.0, 2),
                    })

        for row_label, data in results.items():
            data["decimal_hours"] = round(data["total_seconds"] / 3600.0, 2)

        return results
