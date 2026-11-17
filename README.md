# `/clockify-logger` — Enduring Planet Weekly Clockify Time Reconstruction & Client Hour Tracking

An intelligent time reconstruction engine, CLI tool, and Antigravity agent skill built for **Abdul Hannan** (`abdul@enduringplanet.com`), Lead Accountant at **Enduring Planet**.

It reconstructs **strictly actual** work hours across four primary communication and scheduling sources—**Google Calendar**, **Gmail Gemini Meeting Notes**, **Slack (`from:me`)**, and **Gmail Sent Emails**—pushes verified entries to Clockify, and automatically aggregates and updates the **"Client List for hour tracking"** Google Sheet (`Weekly`, `Monthly`, and `Source Data` tabs).

---

## Key Features

1. **4-Source Multi-Channel Reconstruction**:
   - **Google Calendar**: Evaluates scheduled events, focus time, and recurring internal meetings.
   - **Gmail Gemini Meeting Notes**: Captures exact call end times from email arrival timestamps (~2–4 minutes after Meet ends) and uncovers untitled ad-hoc meetings.
   - **Slack Activity (`from:me`)**: Detects unscheduled book/SOP reviews, troubleshooting threads, and ad-hoc Meet links.
   - **Gmail Sent Emails**: Validates close deliverables and client communications.

2. **Strict Factual Audit (Anti-Padding & Anti-Conflation)**:
   - **Zero Padding**: Never artificially inflates durations to pad a workday to 8+ hours.
   - **Independent Groupings**: Never conflates unrelated Slack threads or skipped check-ins.
   - **Recurring Sync Verification**: Dynamically validates weekly changes to baseline recurring calls (`Ledger Lounge - Alpha`, `Ledger Lounge`, `Manager's Sync`, `Team Alpha call`, `Team lead call`).

3. **Sub-Client Consolidation**:
   - Consolidates work for all GFC entities (**Spark / SparkCharge**, **MK Properties**, **Stone Soup**, **Mobilus**, **Solo**, **Clever Carbon**, **Workmorphis**, **Marc & Marty**) under the primary **`GFC`** (`B&A Retainer Services`) project ID.

4. **Clockify REST & Reports API Precision**:
   - **Literal Calendar Date Strings**: Passes unshifted `YYYY-MM-DDT00:00:00.000Z` to `YYYY-MM-DDT23:59:59.999Z` to prevent Clockify Reports API from double-shifting queries by `-5h`.
   - **Late-Night Rollover Safety**: Normalizes entries ending at midnight (`23:40–00:00`) to `23:39–23:59 PKT` so Clockify retains them on the intended workday.

5. **Client Hour Tracking Sheet Automation**:
   - Updates **Weekly Tab** (`Saturday – Friday` periods).
   - Updates **Monthly Tab** post-21st (`22nd prior month – 21st current month`).
   - Populates **Source Data Tab** with raw CSV-compatible audit breakdowns.
   - Strictly scopes updates to **Abdul's Pod** (`Ramish`, `Hamza`, `Alyan` — Rows `2–8`, `10–13`, `18–19`).
   - Strictly excludes FP&A/Modelling buckets and `Understanding system/Correcting EP mistake`.

---

## Repository Structure

```text
clockify-logger/
├── run_logger.py                   # Standalone Python CLI entry point
├── setup.py                        # Python package configuration
├── requirements.txt                # Dependencies
├── SKILL.md                        # Antigravity AI Agent Skill & audit rules
├── scripts/
│   ├── __init__.py
│   ├── clockify_client.py          # Clockify REST and Reports API wrapper
│   ├── time_reconstructor.py       # Multi-source time audit & markdown reporter
│   └── sheet_updater.py            # Pod row mapping & exclusion rules for Google Sheets
├── README.md                       # Comprehensive guide and documentation
└── .gitignore
```

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Hannan107/clockify-logger.git
cd clockify-logger
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install CLI Globally (Optional)
```bash
pip install -e .
```

---

## Usage

### 1. Verify Project Directory & Bucket Mappings
Inspect all 20+ active Enduring Planet client project IDs and their corresponding Clockify billing buckets:
```bash
python run_logger.py verify
```
Or with the installed package command:
```bash
clockify-logger verify
```

### 2. Pull and Aggregate Clockify Summary Report
Fetch hours for a weekly or monthly cycle and aggregate them specifically for Abdul's Pod rows in `"Client List for hour tracking"`:
```bash
python run_logger.py report --start 2026-10-17 --end 2026-10-23 --token YOUR_CLOCKIFY_TOKEN
```

### 3. As an Interactive Antigravity Skill
When operating inside Google Antigravity, invoke the skill directly in chat:
```text
/clockify-logger
```
Example prompt:
> *"Log my Clockify hours for Oct 17 - Oct 23 and update the Client List for hour tracking sheet."*

The skill will:
1. Scan your Google Calendar, Gemini Meeting Notes, Slack messages, and Sent emails.
2. Present a clean markdown artifact table for your review with `RequestFeedback: true`.
3. Await your approval before pushing any entry to Clockify.
4. Update the `Client List for hour tracking` Google Sheet (`Weekly`, `Monthly`, and `Source Data` tabs).

---

## Clockify Project & Bucket Reference Matrix

| Client / Project Name | Bucket (`clientName`) | Clockify `projectId` |
| :--- | :--- | :--- |
| **Enduring Planet - Accounting** | *(Internal — No Bucket)* | `6808d297762e83002bb17fa6` |
| **GFC** *(Spark, MK, Stone Soup, etc.)* | `B&A Retainer Services` | `68ed1012021cce63b89a5c97` |
| **Switch Maritime** | `B&A Retainer Services` | `68a5ee7a8802625f8119456f` |
| **Com-sec** | `B&A Retainer Services` | `6a9ea402bd88c3b07d48c2ed` |
| **Action Figure** | `B&A Retainer Services` | `69cd7320668874a429934189` |
| **Circ** | `B&A Retainer Services` | `6a678f08fafec6793207e9f0` |
| **Everfleet** | `B&A Retainer Services` | `6a0ae36892ac7d47e76e6a04` |
| **Guidewheel** | `B&A Retainer Services` | `69c4fe8f368afc35dd8c101e` |
| **GreenWealth** | `B&A Retainer Services` | `6957b1e397b626130b6ed145` |
| **Indow Windows** | `B&A Retainer Services` | `6960faf38e0a1a510e12397a` |
| **EkoabyLingrove** | `B&A Retainer Services` | `6a148db9c1e1b5ce82d7e1c9` |
| **Axiom Cloud** | `Monthly Bookkeeping` | `6659c08a30b50c70e1632b92` |
| **Channing Copper** | `Monthly Bookkeeping` | `68417662bfe455328cc2048d` |
| **capture6** | `Monthly Bookkeeping` | `68628aa1ccb8b35162173dbd` |
| **The Worker Agency** | `Modelling and Proforma` | `6ac7941d7afa036505f885f5` |
| **Propagate** | `B&A Retainer Services` | `6a0b1df35573c2819eae92f7` |
| **Altasea** | `B&A Retainer Services` | `69dcaf3e7617f51a95b6eca9` |
| **Agrology** | `B&A Retainer Services` | `6aa40a5fb921dda50aab4f3c` |
| **Conductor Collective** | `B&A Retainer Services` | `6ad7eac2072c5434747aaea9` |
| **Community Systems Solutions (CSS)** | `Monthly Bookkeeping` | `68dc3be0fb5b7c16f23555a9` |

---

## Google Sheet Row Mapping (Abdul's Pod)

| Row in Sheet | Client Name | Included Clockify Buckets | Excluded Buckets |
| :--- | :--- | :--- | :--- |
| **Rows 2–5** | GFC Crane / MK / Spark / Stone Soup | `B&A Retainer Services` + `Payroll Management` + `AP Management` | None |
| **Row 6** | CTRL-S | `CTRL-S Inc (B&A Retainer Services)` | None |
| **Row 7** | Circ | `Circ (B&A Retainer Services)` + `CIRC (AP Management)` | `Understanding system/Correcting EP mistake` |
| **Row 8** | Com-Sec | `Com-sec (B&A Retainer Services)` | None |
| **Row 10** | Copper | `Channing Copper (Monthly Bookkeeping)` + `Copper (AP Management)` | `Understanding system/Correcting EP mistake` |
| **Row 11** | NGON | `NGON (Monthly Bookkeeping)` + `NGON (B&A Retainer Services)` | None |
| **Row 12** | Switch Maritime | `Switch Maritime (B&A Retainer Services)` + `Switch (AP Management)` | None |
| **Row 13** | Everfleet | `Everfleet (B&A Retainer Services)` | None |
| **Row 18** | Capture6 | `capture6 (Monthly Bookkeeping)` | `Cash Budget`, `Understanding system/Correcting EP mistake` |
| **Row 19** | Greenwealth | `GreenWealth (B&A Retainer Services)` | None |

---

## License

Internal proprietary tool for Enduring Planet accounting operations. All rights reserved.
