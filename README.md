# Wingspan Statistics
## Overview
- Configuration stored in `config/statsconfig.py`.
- `CORPORATION_IDS` are corporations to check for.
- `ALLIANCE_IDS` are alliances to check for.
- Make sure to change:
  - `EARLIEST` for starting point in time.
  - `HEADERS` to represent yourself.
- Currently implemented backends:
  - DB fetcher:
    - zKillboard.
    - ESI.
  - DB parse:
    - MongoDB.

## Usage
```bash
$ nano config/statsconfig.py
$ python3 wingspanstats.py
```

## Thanks
- farshield/wingspanstats
