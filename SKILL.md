---
name: clockify-logger
description: Enduring Planet Weekly Clockify Time Reconstruction, Logging & Client Hour Tracking Sheet Assistant. Use this skill whenever Abdul Hannan wants to update or reconstruct his Clockify hours for a past day, week, or multi-week period from Google Calendar, Gmail (Gemini Meeting Notes & Sent emails), and Slack messages (including unscheduled book/SOP/workpaper reviews), push approved entries to Clockify, and update the "Client List for hour tracking" Google Sheet (Weekly and post-21st Monthly tabs).
---

# Enduring Planet Clockify Reconstruction & Client Hour Tracking Skill

## Overview
This skill reconstructs **actual** work hours for **Abdul Hannan** (`abdul@enduringplanet.com`, Lead Accountant at Enduring Planet) across four sources—**Google Calendar**, **Gmail Gemini Meeting Notes**, **Slack (`from:me`)**, and **Gmail Sent Emails**—pushes approved entries to Clockify, and then updates the **"Client List for hour tracking"** Google Sheet (`Weekly` tab every week, plus the `Monthly` tab on the week ending after the 21st of the month).

---

## Critical Rules & Constraints

1. **Strictly Actual Hours Only (NEVER Pad to 8 Hours/Day)**:
   - Client hours are used to bill clients directly against retainer or hourly buckets.
   - **Never** artificially inflate durations or pad a day to reach 8+ hours.
   - Calculate durations strictly from:
     - **Gemini Meeting Notes arrival timestamps** in Gmail (Gemini emails arrive ~2–4 minutes after a Google Meet call ends, providing the exact end time of both scheduled meetings and ad-hoc `meet.google.com/...` calls).
     - **Slack start/finish messages** (e.g., *"I am starting the review of..."* -> *"I have reviewed the..."*).
     - **Realistic actual time spent** on Slack threads, QBO checks, and email deliverables.

2. **Strict Factual Audit (No Hallucinated or Conflated Groupings)**:
   - Do **not** combine unrelated Slack messages with different team members into a single entry.
   - Verify whether a scheduled meeting actually happened before logging it:
     - Check Slack for cancellations, reschedules, or out-of-office messages (e.g., if a team member had an emergency, or if another lead covered a client call).
     - Note that receiving a Gemini Meeting Notes email with *"You are receiving this email because you are part of a group that was invited"* does **not** prove attendance—cross-check Slack activity during that window.

3. **Recurring Internal Meetings Baseline (ALWAYS Verify Against Calendar Every Week)**:
   - **Baseline Default Schedule**:
     - **Monday**: `Ledger Lounge - Alpha` (`15:30–16:30` PKT)
     - **Tuesday**: `Ledger Lounge` (`15:30–17:00` PKT)
     - **Wednesday**: `Manager's Sync` (`16:00–17:00` PKT)
     - **Friday**: `Team Alpha call` (`15:30–16:00` PKT) and `Team lead call` (`16:00–17:15/17:30` PKT)
   - **Mandatory Calendar Verification**:
     - Always verify these recurring meetings against the user's **Google Calendar** for that specific week, because recurring meetings can be rescheduled, moved to a different day/time, or cancelled in a given week.
     - Cross-check Gemini Meeting Notes arrival times and Slack messages to confirm actual attendance and actual duration.

4. **GFC Sub-Client Rule**:
   - All work for **GFC**, **Spark / SparkCharge**, **MK Properties**, **Stone Soup**, **Mobilus**, **Solo**, **Clever Carbon**, **Workmorphis**, and **Marc & Marty** is logged under the **`GFC`** (`B&A Retainer Services`) project (`68ed1012021cce63b89a5c97`).

5. **Always Present an Artifact for Approval Before Pushing to Clockify**:
   - Generate a clean day-by-day markdown artifact table showing `Time (PKT)`, `Duration`, `Client Bucket (Project)`, `Description`, and `Verification Source`, plus a summary table of daily totals (`Client Billable` vs `Internal`).
   - Wait for explicit user approval before calling the Clockify API.

---

## Step-by-Step Workflow

### Step 1: Check Last Logged Date in Clockify
In the browser (`https://app.clockify.me/tracker`), inspect existing entries via the Clockify API using the active session token (`localStorage.getItem('token')`):
- **Workspace ID**: `664b8b436c802f03913c146b` (`Daim Ashraf's workspace`)
- **User ID**: `6784f10c3fb6a444eea050f1` (`Abdul Hannan`, Timezone: `Asia/Karachi` UTC+5)
- **Endpoint**:
  ```javascript
  GET https://global.api.clockify.me/workspaces/664b8b436c802f03913c146b/timeEntries/user/6784f10c3fb6a444eea050f1/full?page=0&limit=50
  ```

### Step 2: Gather Raw Activity from All 4 Sources
For the target date range (`YYYY-MM-DD` to `YYYY-MM-DD`):
1. **Google Calendar (`https://calendar.google.com`)**:
   - Extract all accepted/scheduled events and Focus Time blocks for each weekday.
   - Verify whether any recurring internal meetings (`Ledger Lounge - Alpha`, `Ledger Lounge`, `Manager's Sync`, `Team Alpha call`, `Team lead call`) moved days or times.
2. **Gmail Gemini Meeting Notes (`https://mail.google.com`)**:
   - Search: `after:YYYY/MM/DD before:YYYY/MM/DD ("Notes by Gemini" OR "Meeting notes" OR from:gemini-notes@google.com)`
   - Record the **email arrival timestamp** for every meeting note—this gives the exact minute the Google Meet ended! Also look for untitled ad-hoc meetings (`"Meeting Oct XX at HH:MM PM PKT"`), which reveal unscheduled Google Meet calls.
3. **Slack Sent Messages (`https://app.slack.com`)**:
   - Search: `from:me after:YYYY-MM-DD before:YYYY-MM-DD`
   - Extract all messages with exact timestamps and channel/DM names. Look specifically for:
     - Unscheduled **Month-End Close / Book Reviews** and **Process Document / SOP Reviews**
     - Ad-hoc Google Meet links (`meet.google.com/...`)
     - Rescheduled or skipped check-ins (`Ramish`, `Hamza & Alyan`, `Waseem`, `Arham`, `Nauman`)
     - Client workpaper/QBO/Bill.com/Maxio/Ramp/Gusto troubleshooting
4. **Gmail Sent Folder (`https://mail.google.com`)**:
   - Search: `in:sent after:YYYY/MM/DD before:YYYY/MM/DD`
   - Capture client emails, close reports, and follow-ups.

### Step 3: Build & Audit the Draft Timesheet Artifact
- Match each item to the user's concise naming style:
  - Client meetings: `"Meeting with [Client]"`
  - Internal 1:1s: `"Check in with Hamza and Alyan"`, `"Check-in with Ramish"`, `"Check-in with Waseem"`, `"Weekly check-in with Arham"`, `"Check-in with Nauman"`
  - Reviews & tasks: `"Review of [Client] Process Document and SOPs"`, `"Axiom [Month] Close Review with Waseem"`, etc.
- Present the artifact to the user with `RequestFeedback: true`.

### Step 4: Push Approved Entries to Clockify
Once approved, run a browser script on `https://app.clockify.me/tracker` using `localStorage.getItem('token')`:
```javascript
POST https://global.api.clockify.me/workspaces/664b8b436c802f03913c146b/timeEntries
Headers: {
  "X-Auth-Token": localStorage.getItem("token"),
  "Content-Type": "application/json"
}
Body: {
  "description": entry.description,
  "projectId": entry.projectId,
  "taskId": null,
  "billable": true,
  "start": new Date(`${entry.date}T${entry.startPKT}:00+05:00`).toISOString(),
  "end": new Date(`${entry.date}T${entry.endPKT}:00+05:00`).toISOString(),
  "tagIds": [],
  "customFields": []
}
```
> **Note on Late-Night Entries**: If an entry ends around midnight PKT (e.g., `23:40–00:00`), use `23:39:00+05:00` to `23:59:00+05:00` so Clockify groups it under the intended PKT workday rather than spilling into the next calendar day.

---

### Step 5: Update "Client List for hour tracking" Google Sheet (`Weekly`, `Monthly`, and `Source Data` Tabs)
After pushing the user's Clockify hours, update the Google Sheet (`G:\My Drive\Client List for hour tracking.gsheet`):
- **Spreadsheet ID**: `1N4Efs53vgQy53XdA2JRXVQdnBDK3L6R7J6a3rMvN3Vc`
- **Weekly Tab (`gid=0`)**:
  - URL: `https://docs.google.com/spreadsheets/d/1N4Efs53vgQy53XdA2JRXVQdnBDK3L6R7J6a3rMvN3Vc/edit?gid=0#gid=0`
  - **Period Format**: Each weekly column runs **Saturday – Friday** (e.g., `Oct 10 - Oct 16`, `Oct 17 - Oct 23`).
- **Monthly Tab (`gid=738345283`)**:
  - URL: `https://docs.google.com/spreadsheets/d/1N4Efs53vgQy53XdA2JRXVQdnBDK3L6R7J6a3rMvN3Vc/edit?gid=738345283#gid=738345283`
  - **When to Update**: Update on the **week ending after the 21st of the month**.
  - **Period Format**: Runs from the **22nd of the prior month to the 21st of the current month** (e.g., `Sep 22 - Oct 21`, `Oct 22 - Nov 21`).
- **Source Data Tab (`gid=1724263041`)**:
  - URL: `https://docs.google.com/spreadsheets/d/1N4Efs53vgQy53XdA2JRXVQdnBDK3L6R7J6a3rMvN3Vc/edit?gid=1724263041#gid=1724263041`
  - **Always update `Source Data` alongside `Weekly`/`Monthly`**: Log the raw Clockify Summary Report breakdown (Project, Clockify Client Bucket, `INCL`/`EXCL` status, `h:mm`, Decimal Hours, and User Breakdown) in the `Source Data` tab so the user can verify every number against their Clockify CSV export.
- **How Hours Are Calculated from Clockify Summary Report (CRITICAL DATE & BUCKET RULES)**:
  1. **Literal Calendar Date Strings (Do NOT Shift by `-5h` for Reports API)**:
     - Unlike the `/timeEntries` REST endpoint, Clockify's Summary Report endpoint (`POST https://reports.api.clockify.me/v1/workspaces/664b8b436c802f03913c146b/reports/summary` or `/report/workspaces/664b8b436c802f03913c146b/async/reports/summary`) **already applies the user's profile timezone (`Asia/Karachi`, UTC+5) on the backend**.
     - Always pass **literal calendar strings**:
       - `dateRangeStart: "YYYY-MM-DDT00:00:00.000Z"`
       - `dateRangeEnd: "YYYY-MM-DDT23:59:59.999Z"`
     - Never construct `new Date("YYYY-MM-DDT00:00:00+05:00").toISOString()` (`T19:00:00.000Z`) for the Reports API, or Clockify will double-shift the query window by 5 hours (querying Friday 7:00 PM PKT to Friday 7:00 PM PKT)!
  2. **Strict Bucket Exclusion Rules**:
     - **NEVER include `Understanding system/Correcting EP mistake`** in any client total in `"Client List for hour tracking"`.
     - **NEVER include FP&A / Modelling buckets** (`Cash Budget`, `FP&A Retainer Services`, `Modelling and Proforma`, `KPI Dashboard`).
  3. **Scope of Rows to Update (Abdul's Pod Only)**:
     - Only update the rows belonging to Abdul's team (**Bookkeepers: `Ramish`, `Hamza`, and `Alyan`** — i.e., **Rows `2–8`, `10–13`, and `18–19`**). Leave the rows for `Atif` (`Rows 15–16`) and `Nauman & Asif/Atif` (`Rows 21–23`) untouched.
  4. **Exact Row-to-Clockify Project & Bucket Mapping (Rows `2–8`, `10–13`, `18–19`)**:
     - `Rows 2–5` (**GFC Crane / MK Properties / Spark Media / Stone Soup** — vertically merged cell): Sum of `GFC (B&A Retainer Services)` + `GFC (Payroll Management)` + `GFC (AP Management)`
     - `Row 6` (**CTRL-S**): `CTRL-S Inc (B&A Retainer Services)`
     - `Row 7` (**Circ**): `Circ (B&A Retainer Services)` + `CIRC (AP Management)` *(Strictly EXCLUDE `Circ | Understanding system/Correcting EP mistake`)*
     - `Row 8` (**Com-Sec**): `Com-sec (B&A Retainer Services)`
     - `Row 10` (**Copper**): `Channing Copper (Monthly Bookkeeping)` + `Copper (AP Management)` *(Strictly EXCLUDE `Channing Copper | Understanding system/Correcting EP mistake`)*
     - `Row 11` (**NGON**): `NGON (Monthly Bookkeeping)` + `NGON (B&A Retainer Services)`
     - `Row 12` (**Switch Maritime**): `Switch Maritime (B&A Retainer Services)` + `Switch (AP Management)`
     - `Row 13` (**Everfleet**): `Everfleet (B&A Retainer Services)`
     - `Row 18` (**Capture6**): `capture6 (Monthly Bookkeeping)` only *(Strictly EXCLUDE `Capture 6 | Cash Budget`)*
     - `Row 19` (**Greenwealth**): `GreenWealth (B&A Retainer Services)`

---

## Clockify Project & Bucket Reference (`projectId`)

| Client / Project Name | Bucket (`clientName` in Clockify) | `projectId` |
| :--- | :--- | :--- |
| **Enduring Planet - Accounting** | *(Internal — No Bucket)* | `6808d297762e83002bb17fa6` |
| **GFC** *(includes Spark, MK, Stone Soup, Mobilus, Solo, Clever Carbon, Workmorphis, Marc & Marty)* | `B&A Retainer Services` | `68ed1012021cce63b89a5c97` |
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
