# Banana

Banana monitors the [NY Urban](https://www.nyurban.com/) Brandeis open-gym schedule and sends email alerts when availability changes. It is designed to make it easier to catch newly released Sunday sessions and spots that reopen after a cancellation.

## How it works

On each polling cycle, Banana:

1. requests the Brandeis schedule from NY Urban;
2. parses each session into a date, start time, court, and availability;
3. compares the result with an in-memory snapshot; and
4. sends an email from whichever email specified in `.env`.

The application in [`main.py`](main.py) uses just one check:

- **Quarter-Daily Check** runs on every poll and emails when there are any changes (slots opening/closing, new dates added). Future work may involve specific court/time/day filters.

The first run establishes a baseline and does not send a change notification. By default, the schedule is polled every six hours.

## Requirements

- Python 3.14 or newer
- A Gmail account that can authenticate to `smtp.gmail.com`
- [`uv`](https://docs.astral.sh/uv/) (recommended) or another Python package installer

## Setup

Clone the repository and install the project with its development dependencies:

```bash
git clone <repository-url>
cd banana
uv sync --dev
```

Create a `.env` file in the project root:

```dotenv
EMAIL_NAME=your-address@gmail.com
EMAIL_PASSWORD=your-app-password
```

`EMAIL_PASSWORD` should be a Gmail app password when the account uses two-step verification. The `.env` file is ignored by Git; do not commit credentials.

Before running the monitor, update the recipient addresses and, if needed, the subjects and polling interval in [`main.py`](main.py):

```python
recipients=["you@example.com"]

# Six hours between schedule requests
poll_interval_seconds=60 * 60 * 6
```

## Running the monitor

Start the long-running process with:

```bash
uv run python main.py
```

Keep the process running for continuous monitoring. Stop it with <kbd>Ctrl</kbd>+<kbd>C</kbd>.

The current snapshot stores are in memory, so restarting the process clears both comparison baselines. After a restart, the first check at each cadence establishes a fresh baseline.

## Running the tests

```bash
uv run python -m pytest
```

The test suite covers schedule parsing and diffing, baseline behavior, notification filtering, and the monitor's two cadences.

## Project structure

```text
.
├── main.py                         # Production wiring and configuration
├── pyproject.toml                  # Package metadata and dependencies
├── src/banana/
│   ├── AvailabilityMonitor.py      # Single-check monitor
│   ├── DualCadenceAvailabilityMonitor.py
│   ├── RolloverTracker.py          # Current cadence helper
│   ├── ScheduleChecker.py          # Snapshot/diff/notify orchestration
│   ├── models/Schedule.py          # Parsed schedule and update models
│   └── primitives/                 # Fetcher, parser, differencer, notifier,
│                                   # and snapshot-store implementations
└── tests/                          # Pytest suite and test fakes
```

The components under `primitives/` use small protocols, so fetching, parsing, persistence, comparison, and notification behavior can be replaced independently.

## TODO

- Add a persistent snapshot store, such as SQLite or a file-backed implementation, so comparison baselines survive restarts.
- Abstract the monitor into a general schedule and notification filtering engine, rather than centering the design around an explicit rollover tracker.
- Move schedule source, session, sport, recipient, notification filter, and polling settings out of `main.py` and into configuration.
- Treat the Brandeis open-gym behavior as one configured filter: a daily availability-change summary plus a six-hour check for newly released dates.
- Support additional NY Urban sessions and sports.
- Add fetchers and parsers for schedules hosted on other websites.

## Current limitations

- Recipient addresses and polling settings are configured in code rather than through environment variables.
- Snapshots are not persisted across process restarts.
- The parser depends on the current structure and wording of NY Urban's schedule HTML.

This project is an independent utility and is not affiliated with NY Urban.
