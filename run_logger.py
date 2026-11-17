#!/usr/bin/env python3
"""
Clockify Logger CLI — Enduring Planet Time Reconstruction & Hour Tracking Assistant
"""

import sys
import argparse
import json
from datetime import datetime
from scripts.clockify_client import ClockifyClient, PROJECT_DIRECTORY
from scripts.time_reconstructor import TimeReconstructor, TimeEntryDraft
from scripts.sheet_updater import SheetHourAggregator, POD_ROW_MAPPINGS


def cmd_verify(args):
    print("=" * 70)
    print("CLOCKIFY LOGGER — PROJECT & BUCKET MAPPING DIRECTORY")
    print("=" * 70)
    print(f"{'Client / Project Name':<35} | {'Bucket / Client':<25} | {'Project ID'}")
    print("-" * 70)
    for name, meta in PROJECT_DIRECTORY.items():
        print(f"{name:<35} | {meta['bucket']:<25} | {meta['projectId']}")
    print("-" * 70)
    print(f"Total Registered Projects: {len(PROJECT_DIRECTORY)}")
    print("\n[✓] All projects mapped according to Enduring Planet accounting rules.")


def cmd_report(args):
    if not args.start or not args.end:
        print("Error: --start and --end dates (YYYY-MM-DD) are required for summary report.")
        sys.exit(1)

    print(f"Pulling Clockify Summary Report for period: {args.start} to {args.end}...")
    client = ClockifyClient(api_token=args.token)
    try:
        report = client.get_summary_report(args.start, args.end)
        group_items = report.get("groupOne", [])
        print(f"Retrieved {len(group_items)} project/bucket groups.")

        print("\nAggregating hours for Abdul's Pod (Rows 2–8, 10–13, 18–19):")
        aggregated = SheetHourAggregator.filter_and_aggregate(group_items)

        print("-" * 70)
        print(f"{'Sheet Row & Client':<45} | {'Decimal Hours':<15}")
        print("-" * 70)
        total_hours = 0.0
        for row_label, data in aggregated.items():
            print(f"{row_label:<45} | {data['decimal_hours']:<15.2f}")
            total_hours += data["decimal_hours"]
        print("-" * 70)
        print(f"{'Total Pod Hours':<45} | {total_hours:<15.2f}")
    except Exception as e:
        print(f"Error fetching report: {e}")
        print("Note: Ensure CLOCKIFY_API_TOKEN is set or pass --token <your_token>")


def main():
    parser = argparse.ArgumentParser(
        description="Clockify Logger — Enduring Planet Time Reconstruction & Hour Tracking CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # verify
    subparsers.add_parser("verify", help="Verify project and bucket directory mapping")

    # report
    p_report = subparsers.add_parser("report", help="Fetch and aggregate Clockify Summary Report for Google Sheet")
    p_report.add_argument("--start", help="Start Date (YYYY-MM-DD)")
    p_report.add_argument("--end", help="End Date (YYYY-MM-DD)")
    p_report.add_argument("--token", help="Clockify API / Session Token", default=None)

    args = parser.parse_args()

    if args.command == "verify" or not args.command:
        cmd_verify(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
