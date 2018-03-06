# Wingspan Statistics
## Overview
- Configuration stored in `config/statsconfig.py`.
- `CORPORATION_IDS` are corporations to check for.
- `ALLIANCE_IDS` are alliances to check for.
- Make sure to change:
  - `ENDPOINT_CORPORATION` for correct corporation lookup endTime (`endTime/201508260400/`).
  - `EARLIEST` for starting point in time.
  - `HEADERS` to represent yourself.
- Currently implemented backends:
    - DB create:
        - JSON.
    - DB parse:
        - JSON2MongoDB.

## Usage
```bash
$ nano config/statsconfig.py
$ python wingspanstats.py
```

## Thanks
- farshield/wingspanstats
