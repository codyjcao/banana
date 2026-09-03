# Banana

Banana monitors the [NY Urban](https://www.nyurban.com/) Brandeis open-gym schedule and sends email alerts when availability changes. It is designed to make it easier to catch newly released Sunday sessions and spots that reopen after a cancellation.

## How it works

On each polling cycle, Banana:

1. requests the Brandeis schedule from NY Urban;
2. parses each session into a date, start time, court, and availability;
3. compares the result with an in-memory snapshot; and
4. sends an email from whichever email specified in `.env`.

The application in [`main.py`](main.py) uses two checks with shared fetching,
parsing, and buffered notification infrastructure:

- **Schedule Check** runs daily and reports all currently open slots.
- **Schedule Update Check** runs every four hours and reports availability
  changes and newly added dates.

The first update check establishes a baseline and does not send a change
notification. Notifications generated within the buffer window are combined
into one email.

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
EMAIL_RECIPIENTS=first-recipient@example.com,second-recipient@example.com
EMAIL_SUBJECT=Brandeis Open Play Notification
```

`EMAIL_PASSWORD` should be a Gmail app password when the account uses two-step verification. The `.env` file is ignored by Git; do not commit credentials.

Multiple recipients can be supplied as a comma-separated list. The timing
defaults can optionally be overridden in `.env`:

```dotenv
SCHEDULE_CHECK_INTERVAL_SECONDS=86400
SCHEDULE_UPDATE_CHECK_INTERVAL_SECONDS=14400
NOTIFICATION_BUFFER_SECONDS=60
```

## Running the monitor

Start the long-running process with:

```bash
uv run python main.py
```

Keep the process running for continuous monitoring. Stop it with <kbd>Ctrl</kbd>+<kbd>C</kbd>.

The update-check snapshot is stored in memory. Restarting the process clears
that comparison baseline, so the first update check after a restart establishes
a new baseline.

## Running the tests

```bash
uv run python -m pytest
```

The test suite covers schedule parsing and diffing, baseline behavior,
notification filtering, buffering, checks, and periodic execution.

## Project structure

```text
.
├── main.py                         # Production composition and configuration
├── pyproject.toml                  # Package metadata and dependencies
├── src/banana/
│   ├── checks/                     # One-shot schedule operations
│   ├── formatters/                 # Schedule notification formatting
│   ├── models/                     # Schedule and update models
│   ├── primitives/                 # Fetching, parsing, policies, and delivery
│   ├── protocols/                  # Shared structural interfaces
│   ├── runners/                    # Periodic execution
│   └── util/                       # Timed buffering
└── tests/                          # Pytest suite and test fakes
```

The components under `primitives/` use small protocols, so fetching, parsing, persistence, comparison, and notification behavior can be replaced independently.

## TODO

- Add a persistent snapshot store, such as SQLite or a file-backed implementation, so comparison baselines survive restarts.
- Move schedule source, session, sport, recipient, notification filter, and polling settings out of `main.py` and into configuration.
- Treat the Brandeis open-gym behavior as one configured filter rather than
  hard-coding it in the composition root.
- Support additional NY Urban sessions and sports.
- Add fetchers and parsers for schedules hosted on other websites.

## Current limitations

- Recipient addresses and polling settings are configured in code rather than through environment variables.
- Snapshots are not persisted across process restarts.
- The parser depends on the current structure and wording of NY Urban's schedule HTML.

This project is an independent utility and is not affiliated with NY Urban.
