# 25	Frigate
# 26	Cruiser
# 27	Battleship
# 28	Industrial
# 29	Capsule
# 30	Titan
# 31	Shuttle
# 237	Corvette
# 358	HAC
# 419	Combat BC
# 420	Destroyer
# 485	Dreadnought
# 540	Command Ship
# 541	Interdictor
# 547	Supercarrier
# 659	Carrier
# 830	CovOps
# 832	Logistics
# 833	Force Recon
# 834	Bomber
# 894	HIC
# 898	BLOPs
# 900	Maradeur
# 906	Combat Recon
# 963	T3C
# 1201  Attack BC
# 1305	T3D
# 1534	Command Destroyer
# 1538	AUX

# 311 Reprocessing Array
# 363 Ship Maintenance Array
# 365 Control Tower
# 397 Assembly Array
# 404 Silo
# 413 Laboratory
# 416 Moon Mining
# 417 Mobile Missile Sentry
# 426 Mobile Projectile Sentry
# 430 Mobile Laser Sentry
# 439 Electronic Warfare Battery
# 440 Sensor Dampening Battery
# 441 Stasis Webification Battery
# 443 Warp Scrambling Battery
# 444 Shield Hardening Array
# 449 Mobile Hybrid Sentry
# 471 Corporate Hangar Array
# 707 Jump Portal Array
# 837 Energy Neutralizing Battery
# 838 Cynosural Generator Array
# 839 Cynosural System Jammer
# 1212  Personal Hangar Array
# 1405  Laboratory

# 1003	Territorial Claim Unit
# 1025  Orbital Infrastructure
# 1404	Engineering Complex
# 1406	Refinery
# 1657	Citadel

# 1246	Mobile Depot
# 1250	Mobile Tractor Unit

# 16240	Catalyst
# 32840	Catalyst
# 32842	Catalyst
# 32844	Catalyst
# 32846	Catalyst
# 32848	Catalyst
# 33877	Catalyst

# 16242	Thrasher
# 33883	Thrasher


class Achievements(object):
  ACHIEVEMENTS = [
    {
      'id': 'solo_cruiser_in_bomber',
      'name': 'Larger Means Easier To Hit!',
      'description': 'Perform delivery to customer in cruiser-size ship flying stealth bomber alone',
      'rule': {
        'attacker': {
          'solo': True,
          'ship_group_id': [
            834,  # Bomber
          ]
        },
        'victim': {
          'ship_group_id': [
            26,  # Cruiser
            833,  # Force Recon
            906,  # Combat Recon
            358,  # HAC
            894,  # HIC
            832,  # Logistics
            963,  # T3C
          ]
        }
      }
    },
    {
      'id': 'solo_battlecruiser_up_in_bomber',
      'name': 'Caldari Navy Logic Inhibitors',
      'description': 'Perform delivery to customer in ship larger or equal to battlecruiser-size flying stealth bomber alone',
      'rule': {
        'attacker': {
          'solo': True,
          'ship_group_id': [
            834, # Bomber
          ]
        },
        'victim': {
          'ship_group_id': [
            419,  # Combat BC
            1201,  # Attack BC
            540,  # Command Ship
            27,  # Battleship
            898,  # BLOPs
            900,  # Maradeur
            485,  # Dreadnought
            659,  # Carrier
            547,  # Supercarrier
            30,  # Titan
          ]
        }
      }
    },
    {
      'id': 'solo_battleship_up_in_covops_cruiser',
      'name': '',
      'description': 'Perform delivery to customer in ship larger or equal to battleship-size flying CovOps cruiser alone',
      'rule': {
        'attacker': {
          'solo': True,
          'ship_group_id': [
            833,  # Recon
            963,  # T3C
          ],
          'ship_type_id': [
            33470,  # Stratios
          ]
        },
        'victim': {
          'ship_group_id': [
            27,  # Battleship
            898,  # BLOPs
            900,  # Maradeur
            485,  # Dreadnought
            659,  # Carrier
            547,  # Supercarrier
            30,  # Titan
          ]
        }
      }
    }
  ]


  @staticmethod
  def check(database, achievement):
    query = Achievements._construct_query(achievement['rule'])

    res = database.parser_killmails.find(query)

    return res

  @staticmethod
  def _construct_query(rule):
    query = {}

    Achievements._check_attacker(rule, query)
    Achievements._check_victim(rule, query)

    return query

  @staticmethod
  def _check_attacker(rule, query):
    Achievements._check_solo(rule, query)
    Achievements._check_attacker_ship(rule, query)

  @staticmethod
  def _check_solo(rule, query):
    if 'solo' in rule['attacker'] and rule['attacker']['solo']:
      query['zkb.solo'] = True

  @staticmethod
  def _check_attacker_ship(rule, query):
    Achievements._check_ship(rule, query, 'attacker', 'attackers_processed.wingspan')

  @staticmethod
  def _check_ship(rule, query, side, db_path):
    if 'ship_group_id' in rule[side] and 'ship_type_id' in rule[side]:
      query['$or'] = [
        Achievements._shard_ship_group_id(rule, side, db_path),
        Achievements._shard_ship_type_id(rule, side, db_path),
      ]
      return

    if 'ship_group_id' in rule[side]:
      query.update(Achievements._shard_ship_group_id(rule, side, db_path))
      return

    if 'ship_type_id' in rule[side]:
      query.update(Achievements._shard_ship_type_id(rule, side, db_path))
      return

  @staticmethod
  def _shard_ship_group_id(rule, side, db_path):
    tmp = {}
    tmp[db_path + '.ship_group_id'] = {'$in': rule[side]['ship_group_id']}
    return tmp

  @staticmethod
  def _shard_ship_type_id(rule, side, db_path):
    tmp = {}
    tmp[db_path + '.ship_type_id'] = {'$in': rule[side]['ship_type_id']}
    return tmp

  @staticmethod
  def _check_victim(rule, query):
    Achievements._check_ship(rule, query, 'victim', 'victim')
