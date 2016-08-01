# Wingspan Statistics
Statistics calculation script.

## Overview
- Configuration stored in `config/statsconfig.py`.
- `CORPORATION_IDS` are corporations to check against.
- `OTHER_CORPS_IDS` are corporations to check against only then they were in `ALLIANCE_IDS`.
- Please change `HEADERS` to represent yourself.
- Currently implemented backends:
    - DB create:
        - JSON,
        - MongoDB.
    - DB parse:
        - JSON,
        - MongoDB.
- By default, scripts uses both backends. Edit `wingspanstats.py` for different results.

## Usage
```bash
$ python wingspanstats.py
```

## Thanks
- farshield/wingspanstats
