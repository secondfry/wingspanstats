# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2018-10-06
### Added
- `zkb_points` category.

### Changed
- Killmail is considered invalid if victim has no `character_id` with exception for anchorable structures.
- Using Python 3 now.

### Fixed
- Adapts to 2018-10-02 zKillboard change. Now uses ESI to fetch extended killmail information.

## [2.1.1] - 2018-03-18
### Fixed
- Added missing attack battlecruiser and combat recons `ship_group_id`s.

## [2.1.0] - 2018-03-18
### Added
- Achievments!
- Dedication and diversity leaderboards.  
Dedication index calculated by counting killmails done in same ship with same weapon type.  
Diversity index calculated by counting killmails done in various ships with differentweapon types.
- Local copy of pilot names.
- Added flag `solo_bomber` indicating deliveries done while flying stealth bomber alone.
- Added some new ships to categories (AT, CONCORD ships).
- Each attacker now also gets weapon type flags like `bomb_user`.

### Changed
- Leaderboards no longer include pilots with zero deliveries in leaderboard category.
- Now each category uses it's own MongoDB collection.
- `industrial` category renamed to `transport`.
- Introduced new `industrial` category which is merged `transport` and `miner` categories.
- Upsert killmails instead of silently failing to insert them.
- `fleet` now expects more than 1 capsuleer attacker.
- `awox` now uses it's own recognition system in addition to zKillboard one.

### Fixed
- Added missing count, value and damage from leaderboards.
- Fixed place change not being calculated in subsequent script launches.
- Fixed FW deliveries not being recognized.

## [2.0.0] - 2018-03-06
### Added
- Entity fetch state. Contains last fetched page.  
File: `database/:entity/state.json`.  
Example:
```json
{"page": 306}
```
- Result state. Contains last processed page for each entity and last processed leaderboard month.  
File: `result/state.json`.
Example:
```json
{"99006319": {"page": 306}, "leaderboard": "2018-03"}
```
- `DbParserJSON2Mongo`.  
  - Processes killmails from GZIPed pages located at `database/:entity`:
    - Adds flags.
      - General flags like `solo`, `fw`.
      - Space type flags like `lowsec`, `anoikis`.
      - Each attacker gets ship type flags like `dictor_driver`, `astero_killer`.
    - Assigns `group_id` to each `ship_type_id` of killmail.
    - Decides if killmail is legitimate or not.
      - Must have at least one capsuller pilot.
      - Fleet ratio of target corporation should be more than configured (default 25%).
    - Stores result in MongoDB.
  - Aggregates killmails to pilot monthly data in `months` MongoDB collection.  
  ```json
  {
    '_id': {'date': {'year': 2014, 'month': 7}, 'character_id': 93980583}},
    'solo_count': 1,
    'solo_value': 430095,
    ...
  }
  ```
  - Creates leaderboards.
  - Creates alltime data.

### Changed
- zKillboard pages are now saved in continuos manner (previously were separated by months).

### Removed
- Removed zKillboard unified fetcher. zKillboard no longer accepts multiple entity ids in paged requests.
- Removed `DbCreateZkillboardMongo` as 
- Removed `DbParseJSON`.
- Removed `DbParseMongo`.
