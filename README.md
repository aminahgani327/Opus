# Opus — Opportunity Pipeline Tracker

A Python backend tool for managing and validating commercial opportunity data within a technology services organisation. Opus ingests opportunity and resourcing data, validates records against defined business rules, flags pipeline gaps and staffing issues, and produces an actionable summary report.

---

## Business Context

Account managers in technology consulting organisations are responsible for tracking opportunities from initial identification through to signed and fully staffed delivery. This process often relies on manual cross-referencing of data across multiple systems, introducing risk of error and oversight. Opus automates this validation process, surfacing issues before they become operational problems.

---

## Features

- Reads opportunity data from a structured CSV file
- Validates all records against business rules (budget, staffing, status)
- Flags signed opportunities that are unstaffed, partially staffed, or missing budgets
- Outputs a formatted pipeline report to the console
- Saves a full report as a JSON file for downstream use
- Allows users to update opportunity statuses interactively during a session
- Includes a full unit test suite covering normal, edge, and invalid input cases

---

## Project Structure
opus/
│
├── main.py                  # Entry point — run this to start Opus
├── loader.py                # Reads and parses CSV input data
├── validator.py             # Validates opportunities against business rules
├── reporter.py              # Generates console and JSON output
├── updater.py               # Handles interactive status updates
│
├── data/
│   └── opportunities.csv    # Input data file
│
├── output/
│   └── report.json          # Generated report (created on first run)
│
├── tests/
│   └── test_validator.py    # Unit tests for validation logic
│
└── README.md

---

## Requirements

- Python 3.10 or higher
- No external libraries required — uses Python standard library only

---

## Setup & Usage

**1. Clone the repository**
```bash
git clone https://github.com/aminahgani327/opus.git
cd opus
```

**2. Run the application**
```bash
python main.py
```

**3. Run the unit tests**
```bash
python -m unittest tests/test_validator.py -v
```

---

## Input Data Format

The input CSV file (`data/opportunities.csv`) must contain the following headers:

| Column | Description | Example |
|---|---|---|
| opportunity_id | Unique identifier | OPP001 |
| name | Opportunity name | Project Alpha |
| status | pipeline / signed / closed | signed |
| budget | Numeric budget value | 50000 |
| required_roles | Pipe-separated role list | developer\|analyst |
| assigned_staff | Pipe-separated staff list | Jane Smith\|Tom Brown |

---

## Output

**Console** — formatted pipeline report with flagged issues and summary statistics

**JSON** — full report saved to `output/report.json` including timestamp, summary counts, and full opportunity detail
