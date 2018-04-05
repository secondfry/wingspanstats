#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from bson.objectid import ObjectId
from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
import unicodecsv as csv
import gzip
import json
import os
import requests
import sys

from config.statsconfig import StatsConfig
from scripts.achievements import Achievements
from scripts.alliance import Alliance
from scripts.corporation import Corporation
from scripts.log import log
from scripts.state import State


SHIP_RULES = [
  'astero',
  'stratios',
  'nestor',
  'blops',
  'bomber',
  'dictor',
  'recon',
  't3c',
  't3d',
  'capital',
  'transport',
  'miner',
  'industrial',
  'pod',
  'concord',
  'AT',
  'trash',
  'codegreen',
  'codered',
]

SHIPS = {}
SHIPS['astero'] = [33468]
SHIPS['stratios'] = [33470]
SHIPS['nestor'] = [33472]
SHIPS['blops'] = [
  22428, # Redeemer
  22430, # Sin
  22436, # Widow
  22440, # Panther

  44996, # Marshal, CONCORD, Black Ops
]
SHIPS['bomber'] = [
  11377, # Nemesis
  12032, # Manticore
  12034, # Hound
  12038, # Purifier

  45530, # Virtuoso, AT XV, Stealth Bomber
]
SHIPS['dictor'] = [
  22452, # Heretic
  22456, # Sabre
  22460, # Eris
  22464, # Flycatcher

  11995, # Onyx
  12013, # Broadsword
  12017, # Devoter
  12021, # Phobos

  35781, # Fiend, AT XIII, HIC
]
SHIPS['recon'] = [
  11957, # Falcon
  11963, # Rapier
  11965, # Pilgrim
  11969, # Arazu

  11961, # Huginn
  11971, # Lachesis
  11959, # Rook
  20125, # Curse

  33395, # Moracha, AT XI, Force Recon
  33675, # Chameleon, AT XII, Force Recon
  45531, # Victor, AT XV, Force Recon
  44995, # Enforcer, CONCORD, Force Recon
]
SHIPS['t3c'] = [
  29984, # Tengu
  29986, # Legion
  29988, # Proteus
  29990, # Loki
]
SHIPS['t3d'] = [
  34317, # Confessor
  34562, # Svipul
  34828, # Jackdaw
  35683, # Hecate
]
SHIPS['capital'] = [
  # Dreads
  19720, # Revelation
  19722, # Naglfar
  19724, # Moros
  19726, # Phoenix
  34339, # Moros Interbus Edition
  34341, # Naglfar Justice Edition
  34343, # Phoenix Wiyrkomi Edition
  34345, # Revelation Sarum Edition
  42124, # Vehement
  42243, # Chemosh
  45647, # Caiman

  # Carriers
  23757, # Archon
  23915, # Chimera
  24483, # Nidhoggur
  23911, # Thanatos
  42132, # Vanguard

  # Supers
  3514, # Revenant
  3628, # Nation, ???
  23919, # Aeon
  22852, # Hel
  23913, # Nyx
  23917, # Wyvern
  42125, # Vendetta

  # Titans
  671, # Erebus
  3764, # Leviathan
  11567, # Avatar
  23773, # Rangarok
  42126, # Vanquisher
  42241, # Molok
  45649, # Komodo

  # ORE
  28352, # Rorqual
  33687, # Rorqual ORE Development Edition
]
SHIPS['transport'] = [
  # Industrials
  648, # Badger
  649, # Tayra
  650, # Nereus
  651, # Hoarder
  652, # Mammoth
  653, # Wreathe
  654, # Kryos
  655, # Epithal
  656, # Miasmos
  657, # Iteron Mark V
  1944, # Bestower
  2863, # Primae
  2998, # Noctis
  4363, # Miasmos Quafe Ultra Edition
  4388, # Miasmos Quafe Ultramarine Edition
  19744, # Sigil
  32811, # Miasmos Amastris Edition
  33695, # Bestower Tash-Murkon Edition
  33689, # Iteron Inner Zone Shipping Edition
  33691, # Tayra Wiyrkomi Edition
  33693, # Mammoth Nefantar Edition

  # Blockade runners
  12729, # Crane
  12733, # Prorator
  12735, # Prowler
  12743, # Viator

  # DST
  12731, # Bustard
  12745, # Occator
  12747, # Mastodon
  12753, # Impel

  # Freighters
  20183, # Providence
  20185, # Charon
  20187, # Obelisk
  20189, # Fenrir
  34328, # Bowhead

  # Jump Freighters
  28844, # Rhea
  28846, # Nomad
  28848, # Anshar
  28850, # Ark

  # Industrial Command
  28606, # Orca
  28352, # Rorqual
  33685, # Orca ORE Development Edition
  33687, # Rorqual ORE Development Edition
]
SHIPS['miner'] = [
  # Frigates
  32880, # Venture

  # Expedition Frigates
  33697, # Prospect
  37135, # Endurance

  # Mining Barges
  17476, # Covetor
  17478, # Retriever
  17480, # Procurer

  # Exhumers
  22544, # Hulk
  22546, # Skiff
  22548, # Mackinaw
  33683, # Mackinaw ORE Development Edition
]
SHIPS['pod'] = [
  670, # Capsule
  33328, # Capsule - Genolution 'Auroral' 197-variant
]
SHIPS['concord'] = [
  44993, # Pacifier
  44995, # Enforcer, CONCORD, Force Recon
  44996, # Marshal, CONCORD, Black Ops
]
SHIPS['AT'] = [
  33397, # Chremoas, AT XI, Covert Ops
  33675, # Chameleon, AT XII, Force Recon
  35781, # Fiend, AT XIII, HIC
  42246, # Caedes, AT XIV, Covert Ops
  45530, # Virtuoso, AT XV, Stealth Bomber
]
SHIPS['trash'] = [
  33474, # Mobile Depo
  33520, # 'Wetu' Mobile Depo,
  33522, # 'Yurt' Mobile Depo,

  33475, # Mobile Tractor Unit
  33700, # 'Packrat' Mobile Tractor Unit
  33702, # 'Magpie' Mobile Tractor Unit
]
SHIPS['codegreen'] = [
  16240, # Catalyst
  32840, # Catalyst
  32842, # Catalyst
  32844, # Catalyst
  32846, # Catalyst
  32848, # Catalyst
  33877, # Catalyst
]
SHIPS['codered'] = [
  16242, # Thrasher
  33883, # Thrasher
]


WEAPON_RULES = [
  'bomb',
]

WEAPONS = {}
WEAPONS['bomb'] = [
  27912, # Concussion Bomb
  27916, # Scorch Bomb
  27918, # Shrapnel Bomb
  27920, # Electron Bomb
  27922, # Lockbreaker Bomb,
  27924, # Void Bomb,
  34264, # Focused Void Bomb
]

LOOKUP = {}
for ship_type, arr in SHIPS.iteritems():
  for ship_id in arr:
    LOOKUP[ship_id] = ship_type
for weapon_type, arr in WEAPONS.iteritems():
  for weapon_id in arr:
    LOOKUP[weapon_id] = weapon_type

FLAGS_SIMPLE = [
  'solo',
  'solo_bomber',
  'fleet',
  'explorer',
  'fw',
  'awox',
  'pure',
  'thera',
  'highsec',
  'lowsec',
  'nullsec',
  'anoikis',
]

FLAGS_ADVANCED = deepcopy(FLAGS_SIMPLE)
for ship in SHIP_RULES:
  FLAGS_ADVANCED.append(ship + '_killer')
  FLAGS_ADVANCED.append(ship + '_driver')
for weapon in WEAPON_RULES:
  FLAGS_ADVANCED.append(weapon + '_user')

CATEGORIES = ['count', 'value', 'damage', 'zkb_points']
CATEGORIES += [flag + '_count' for flag in FLAGS_ADVANCED]
CATEGORIES += [flag + '_value' for flag in FLAGS_ADVANCED]

PILOTLESS = [
  311, # Reprocessing Array
  363, # Ship Maintenance Array
  365, # Control Tower
  397, # Assembly Array
  404, # Silo
  413, # Laboratory
  416, # Moon Mining
  417, # Mobile Missile Sentry
  426, # Mobile Projectile Sentry
  430, # Mobile Laser Sentry
  439, # Electronic Warfare Battery
  440, # Sensor Dampening Battery
  441, # Stasis Webification Battery
  443, # Warp Scrambling Battery
  444, # Shield Hardening Array
  449, # Mobile Hybrid Sentry
  471, # Corporate Hangar Array
  707, # Jump Portal Array
  837, # Energy Neutralizing Battery
  838, # Cynosural Generator Array
  839, # Cynosural System Jammer
  1212, #  Personal Hangar Array
  1405, #  Laboratory

  1003, #  Territorial Claim Unit
  1025, #  Orbital Infrastructure
  1404, #  Engineering Complex
  1406, #  Refinery
  1657, #  Citadel
]

SPACE_TRASH = [
  1246, # Mobile Depot
  1250, # Mobile Tractor Unit
]


class DbParser(object):
  LOG_LEVEL = 1

  @staticmethod
  def factory(type):
    """
    Provides DB creator

    :param type Selects type of DB creator
    """
    if type == "json-mongo":
      log(DbParser.LOG_LEVEL, 'Creating JSON-to-MongoDB database parser')
      return DbParserJSON2Mongo()
    assert 0, "Source '" + type + "' is not defined"


class DbParserJSON2Mongo(DbParser):
  LOG_LEVEL = 2
  DEFAULT_STATE = {}
  DEDICATION_QUERY = [
    {'$unwind': '$attackers_processed.wingspan'},
    {
      '$group': {
        '_id': {
          'character_id': '$attackers_processed.wingspan.character_id',
          'ship_type_id': '$attackers_processed.wingspan.ship_type_id',
          'weapon_type_id': '$attackers_processed.wingspan.weapon_type_id',
        },
        'value': {'$sum': 1},
        'voptional': {'$sum': '$zkb.totalValue'}
      }
    },
    {
      '$project': {
        'voptional': {
          '$sum': [
            '$value',
            {'$divide': ['$voptional', 1000000000000]}
          ]
        },
        'value': 1,
      }
    },
    {
      '$group': {
        '_id': '$_id.character_id',
        'data': {
          '$addToSet': {
            'ship_type_id': '$_id.ship_type_id', 'weapon_type_id': '$_id.weapon_type_id', 'value': '$value',
            'voptional': '$voptional'
          }
        },
        'voptional': {'$max': '$voptional'}
      }
    },
    {
      '$project': {
        'match': {
          '$filter': {
            'input': '$data',
            'as': 'data',
            'cond': {
              '$eq': ['$$data.voptional', '$voptional']
            }
          }
        }
      }
    },
    {
      '$project': {
        'match': {
          '$arrayElemAt': ['$match', 0]
        }
      }
    },
    {'$unwind': '$match'},
    {
      '$project': {
        'character_id': '$_id',
        'value': '$match.value',
        'match': 1
      }
    },
    {'$sort': {'match.voptional': -1}},
  ]
  DIVERSITY_QUERY = [
    {'$unwind': '$attackers_processed.wingspan'},
    {
      '$group': {
        '_id': {
          'character_id': '$attackers_processed.wingspan.character_id',
          'flag': 'diversity'
        },
        'character_id': {'$first': '$attackers_processed.wingspan.character_id'},
        'ship_type_ids': {'$addToSet': '$attackers_processed.wingspan.ship_type_id'},
        'weapon_type_ids': {'$addToSet': '$attackers_processed.wingspan.weapon_type_id'},
        'voptional': {'$sum': 1},
      }
    },
    {
      '$project': {
        'character_id': 1,
        'ship_type_ids': 1,
        'weapon_type_ids': 1,
        'value': {'$sum': [{'$size': '$ship_type_ids'}, {'$size': '$weapon_type_ids'}]},
        'voptional': 1,
      }
    },
    {'$sort': {'value': -1, 'voptional': -1}}
  ]

  def __init__(self):
    DbParserJSON2Mongo.DEFAULT_STATE = {
      str(x): {'page': 1} for x in StatsConfig.ENTITY_IDS
    }
    DbParserJSON2Mongo.DEFAULT_STATE['leaderboard'] = StatsConfig.EARLIEST

    self._init_entities()
    self._init_directories()

    with open(os.path.join(StatsConfig.SCRIPTS_PATH, 'security.csv'), 'r') as f:
      reader = csv.reader(f)
      self.space_class = {int(rows[0]): rows[1] for rows in reader}

    with open(os.path.join(StatsConfig.SCRIPTS_PATH, 'typeIDs.csv'), 'r') as f:
      reader = csv.reader(f, encoding='utf-8')
      self.items = {int(row[0]): int(row[1]) for row in reader}

    self.DBClient = MongoClient('localhost', 27017)
    self.DB = self.DBClient.wingspan_statistics_new

    self.state = State(os.path.join(StatsConfig.RESULTS_PATH, 'state.json'), self.DEFAULT_STATE)

    self.dori_memory = {}

  def _init_entities(self):
    self.entities = {}
    self._init_alliances()
    self._init_corporations()

  def _init_alliances(self):
    for id in StatsConfig.ALLIANCE_IDS:
      self.entities[id] = Alliance(id)

  def _init_corporations(self):
    for id in StatsConfig.CORPORATION_IDS:
      self.entities[id] = Corporation(id)

  def _init_directories(self):
    self.dir = StatsConfig.RESULTS_PATH
    self._check_directory(self.dir)

  def _check_directory(self, dir):
    if not os.path.isdir(dir):
      os.mkdir(dir)
      log(self.LOG_LEVEL + 1, 'Directory ' + dir + ' created')

  def get_ship_group_id(self, ship_type_id):
    return self.items[ship_type_id]

  def run(self):
    self._read_pages()
    self._process_months()
    self._make_alltime()
    self._make_summary()
    self._process_pilots()

  def _read_pages(self):
    log(self.LOG_LEVEL, 'Reading pages')

    for key, alliance in self.entities.iteritems():
      local = self.state.get(str(key))
      while local['page'] <= alliance.state.get('page'):
        path = os.path.join(StatsConfig.DATABASE_PATH, str(key), str(local['page']) + '.json.gz')
        self._read_page(path)

        local['page'] += 1
        self.state.set(str(key), local)
        self.state.save()

      # We want to reread last page
      # So we need to reset state to previous page
      local['page'] -= 1
      self.state.set(str(key), local)
      self.state.save()

  def _read_page(self, path):
    log(self.LOG_LEVEL + 1, 'Reading page @ ' + path)
    with gzip.open(path, 'r') as f:
      data = json.load(f)

    for chunk in data:
      killmail = Killmail(self, chunk)
      killmail.process()

  def _process_months(self):
    log(self.LOG_LEVEL, 'Processing months')

    timestamp = datetime.strptime(self.state.get('leaderboard'), '%Y-%m')
    limit = datetime.now()

    self._reset_month(timestamp)

    while timestamp < limit:
      self._process_db_month(timestamp)
      timestamp += relativedelta(months=1)
      self.state.set('leaderboard', timestamp.strftime('%Y-%m'))
      self.state.save()

    # We want to reset last month
    # So we need to reset state to previous month
    timestamp -= relativedelta(months=1)
    self.state.set('leaderboard', timestamp.strftime('%Y-%m'))
    self.state.save()

  def _reset_month(self, timestamp):
    query = {'_id.date.year': {'$eq': timestamp.year}, '_id.date.month': {'$gte': timestamp.month}}
    self.DB.months.delete_many(query)

    query = {'_id.date.year': {'$gte': timestamp.year + 1}, '_id.date.month': {'$gte': 1}}
    self.DB.months.delete_many(query)

  def _process_db_month(self, timestamp):
    self._count_flags(timestamp)
    self._init_dori_memory(timestamp)
    self._make_month_leaderboards(timestamp)
    self._make_month_summary(timestamp)

  def _count_flags(self, timestamp):
    query = [
      {'$match': {'date.year': timestamp.year, 'date.month': timestamp.month}},
      {'$unwind': '$attackers_processed.wingspan'},
    ]
    group = {
      '$group': {
        '_id'  : {
          'date'        : '$date',
          'character_id': '$attackers_processed.wingspan.character_id'
        },
        'count': {'$sum': 1},
        'value': {'$sum': '$zkb.totalValue'},
        'zkb_points': {'$sum': '$zkb.points'},
        'damage': {'$sum': '$attackers_processed.wingspan.damage_done'}
        # 'killmails': {'$push': '$$ROOT'} # don't need them?
      }
    }

    for flag in FLAGS_SIMPLE:
      group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$flags.' + flag, 1, 0]}}
      group['$group'][flag + '_value'] = {'$sum': {'$cond': ['$flags.' + flag, '$zkb.totalValue', 0]}}

    for suffix in ['_killer', '_driver']:
      for ship in SHIP_RULES:
        flag = ship + suffix
        group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, 1, 0]}}
        group['$group'][flag + '_value'] = {
          '$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, '$zkb.totalValue', 0]}
        }

    for weapon in WEAPON_RULES:
      flag = weapon + '_user'
      group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, 1, 0]}}
      group['$group'][flag + '_value'] = {
        '$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, '$zkb.totalValue', 0]}
      }

    query.append(group)
    data = self.DB.killmails.aggregate(query)
    self.DB.months.insert_many(data)

  def _init_dori_memory(self, timestamp):
    doristamp = timestamp - relativedelta(months=1)
    doristamp_query = {
      '_id': str(doristamp.year) + '{:0>2}'.format(doristamp.month)
    }

    for category in CATEGORIES:
      data = self.DB['leaderboard_' + category].find_one(doristamp_query)

      if data:
        for pilot in data['places']:
          if pilot['character_id'] not in self.dori_memory:
            self.dori_memory[pilot['character_id']] = {}

          self.dori_memory[pilot['character_id']][category] = pilot['place']

  def _make_month_leaderboards(self, timestamp):
    timestamp_query = {
      '_id': str(timestamp.year) + '{:0>2}'.format(timestamp.month)
    }

    for category in CATEGORIES:
      data = self._make_month_category(timestamp, category)

      leaderboard = deepcopy(timestamp_query)
      leaderboard['places'] = self._parse_data_for_leaderboard(data, category)
      self.DB['leaderboard_' + category].replace_one(timestamp_query, leaderboard, upsert=True)

    leaderboard = deepcopy(timestamp_query)
    leaderboard['places'] = self._make_month_dedication(timestamp)
    self.DB.leaderboard_dedication.replace_one(timestamp_query, leaderboard, upsert=True)

    leaderboard = deepcopy(timestamp_query)
    leaderboard['places'] = self._make_month_diversity(timestamp)
    self.DB.leaderboard_diversity.replace_one(timestamp_query, leaderboard, upsert=True)

  def _make_month_category(self, timestamp, category):
    query = [
      {'$match': {'_id.date.year': timestamp.year, '_id.date.month': timestamp.month}},
      {'$project': {
        '_id': {
          'date': '$_id.date',
        },
        'character_id': '$_id.character_id',
        'value'       : '$' + category
      }},
      {
        '$sort': {
          'value': -1
        }
      }
    ]

    return self.DB.months.aggregate(query)

  def _parse_data_for_leaderboard(self, data, category):
    ret = []

    place = 0
    rem = 0

    for item in data:
      if item['value'] == 0:
        break

      if (item['value'] < rem or rem == 0):
        place += 1
        rem = item['value']

      item['place'] = place
      item['change'] = False

      if item['character_id'] in self.dori_memory and category in self.dori_memory[item['character_id']]:
        item['change'] = self.dori_memory[item['character_id']][category] - place

      if not item['character_id'] in self.dori_memory:
        self.dori_memory[item['character_id']] = {}

      self.dori_memory[item['character_id']][category] = place

      ret.append(item)

    return ret

  def _make_month_dedication(self, timestamp):
    query = deepcopy(self.DEDICATION_QUERY)
    query.insert(0, {'$match': {'date.year': timestamp.year, 'date.month': timestamp.month}})
    data = self.DB.killmails.aggregate(query)

    return self._parse_data_for_leaderboard(data, 'dedication')

  def _make_month_diversity(self, timestamp):
    query = deepcopy(self.DIVERSITY_QUERY)
    query.insert(0, {'$match': {'date.year': timestamp.year, 'date.month': timestamp.month}})
    data = self.DB.killmails.aggregate(query)

    return self._parse_data_for_leaderboard(data, 'diversity')

  def _make_month_summary(self, timestamp):
    data = self.DB.killmails.aggregate([
      {
        '$match': {
          'date.month': timestamp.month,
          'date.year': timestamp.year,
        }
      },
      {
        '$project': {
          'value': '$zkb.totalValue',
          'damage_done': {'$sum': '$attackers_processed.wingspan.damage_done'}
        }
      },
      {
        '$group': {
          '_id': timestamp.strftime('%Y%m'),
          'count': {'$sum': 1},
          'value': {'$sum': '$value'},
          'damage': {'$sum': '$damage_done'}
        }
      }
    ])

    for item in data:
      self.DB.summary.replace_one({'_id': item['_id']}, item, upsert=True)

  def _make_alltime(self):
    log(self.LOG_LEVEL, 'Making alltime categories')

    for category in CATEGORIES:
      self.DB['alltime_' + category].drop()
      self._make_category(category)

    self.DB.alltime_dedication.drop()
    self._make_dedication()

    self.DB.alltime_diversity.drop()
    self._make_diversity()

  def _make_category(self, category):
    query = [
      {'$group': {
        '_id': '$_id.character_id',
        'character_id': {'$first': '$_id.character_id'},
        'value': {'$sum': '$' + category}
      }},
      {
        '$sort': {
          'value': -1
        }
      },
      {'$out': 'alltime_' + category}
    ]
    self.DB.months.aggregate(query)

  def _make_dedication(self):
    query = deepcopy(self.DEDICATION_QUERY)
    query.append({'$out': 'alltime_dedication'})
    self.DB.killmails.aggregate(query)

  def _make_diversity(self):
    query = deepcopy(self.DIVERSITY_QUERY)
    query.append({'$out': 'alltime_diversity'})
    self.DB.killmails.aggregate(query)

  def _make_summary(self):
    log(self.LOG_LEVEL, 'Making overall summary')

    data = self.DB.killmails.aggregate([
      {
        '$project': {
          'value'     : '$zkb.totalValue',
          'damage_done': {'$sum': '$attackers_processed.wingspan.damage_done'}
        }
      },
      {
        '$group': {
          '_id'      : 'overall',
          'count'    : {'$sum': 1},
          'value'    : {'$sum': '$value'},
          'damage'   : {'$sum': '$damage_done'}
        }
      }
    ])

    for item in data:
      self.DB.summary.replace_one({'_id': item['_id']}, item, upsert=True)

  def _process_pilots(self):
    log(self.LOG_LEVEL, 'Processing pilots')

    self._populate_pilots()
    self._fetch_names()
    self._assign_medals()
    self._assign_achievements()

  def _populate_pilots(self):
    pilots = self.DB.killmails.aggregate([
      {'$unwind': '$attackers_processed.wingspan'},
      {
        '$group': {
          '_id': '$attackers_processed.wingspan.character_id'
        }
      }
    ])

    for pilot in pilots:
      try:
        self.DB.pilot_names.insert_one(pilot)
      except:
        pass

      try:
        self.DB.pilot_achievements.insert_one(pilot)
      except:
        pass

  def _fetch_names(self):
    url = 'https://esi.tech.ccp.is/latest/characters/names/?character_ids={}&datasource=tranquility'

    pilots = self.DB.pilot_names.find({'name': None})
    max = pilots.count() / 100

    for i in xrange(0, max + 1):
      arr = []
      for k in xrange(0, 100):
        obj = next(pilots, None)
        if not obj:
          if i == 0 and k == 0:
            return
          else:
            break

        arr.append(str(obj['_id']))

      res = requests.get(url.format(','.join(arr)))
      for pilot in res.json():
        self.DB.pilot_names.update_one({'_id': int(pilot['character_id'])}, {'$set': {'name': pilot['character_name']}})

  def _assign_medals(self):
    medals = {}

    categories = deepcopy(CATEGORIES)
    categories.extend(['dedication', 'diversity'])

    for category in categories:
      data = self.DB['leaderboard_' + category].find()
      for month in data:
        if month['_id'] == 'alltime':
          # TODO add super SWAG alltime medals
          continue

        for pilot in month['places']:
          place = pilot['place']
          id = pilot['character_id']

          if place > 4:
            break

          if id not in medals:
            medals[id] = {}

          if category not in medals[id]:
            medals[id][category] = {'1': 0, '2': 0, '3': 0, '4': 0}

          medals[id][category][str(place)] += 1

    for id in medals:
      if len(medals[id]) > 0:
        self.DB.pilot_medals.replace_one({'_id': id}, {'medals': medals[id]}, upsert=True)

  def _assign_achievements(self):
    pilots_db = {}

    for achievement in Achievements.ACHIEVEMENTS:
      killmails = Achievements.check(self.DB, achievement)

      for killmail in killmails:
        tmp = deepcopy(achievement)
        tmp.update({'killmail': killmail})
        for pilot in killmail['attackers_processed']['wingspan']:
          id = pilot['character_id']
          if id not in pilots_db:
            pilots_db[id] = self.DB.pilot_achievements.find_one({'_id': id})

          pilot_db = pilots_db[id]
          if 'achievement_ids' in pilot_db and achievement['id'] in pilot_db['achievement_ids']:
            continue

          if 'achievement_ids' not in pilot_db:
            pilot_db['achievement_ids'] = []

          pilot_db['achievement_ids'].append(achievement['id'])
          self.DB.pilot_achievements.update(
            {'_id': pilot_db['_id']},
            {
              '$addToSet': {
                'achievements': tmp,
                'achievement_ids': achievement['id']
              }
            }
          )


class Killmail(object):
  def __init__(self, parser, data):
    self.parser = parser
    self.data = data
    self.flags = []
    self.attackers = {'count': {'capsuleer': 0, 'npc': 0, 'wingspan': 0, 'NPSI': 0}, 'wingspan': [], 'others': []}
    self.isBroken = False
    self.isLegit = True
    self._check()

  def _check(self):
    if 'killmail_id' not in self.data:
      self.isBroken = True

  def process(self):
    if self.isBroken:
      return

    self.data['_id'] = self.data['killmail_id']

    self._prepare_attackers()
    self._process_space_class()
    self._process_flags()
    self._process_advanced_flags()
    self._prepare_flags_for_db()
    self._process_attackers()
    self._process_victim()
    self._process_time()

    self._check_legitimacy()
    self._save()

  def _prepare_attackers(self):
    for attacker in self.data['attackers']:
      if 'character_id' not in attacker:
        self.attackers['count']['npc'] += 1
        continue

      self.attackers['count']['capsuleer'] += 1

      attacker['flags'] = {}

      if 'ship_type_id' not in attacker:
        attacker['ship_type_id'] = 0

      if self.is_pilot_wingspan(attacker):
        self.attackers['count']['wingspan'] += 1
        self.attackers['wingspan'].append(attacker)
      else:
        self.attackers['count']['NPSI'] += 1
        self.attackers['others'].append(attacker)

  @staticmethod
  def is_pilot_wingspan(pilot):
    return ('alliance_id' in pilot and pilot['alliance_id'] in StatsConfig.ALLIANCE_IDS) or\
           ('corporation_id' in pilot and pilot['corporation_id'] in StatsConfig.CORPORATION_IDS)

  def _process_space_class(self):
    self.space_class = self.parser.space_class[self.data['solar_system_id']]

  def _process_flags(self):
    self._set_victim_ship_category_flags()

    if self._is_trash():
      return

    self._is_solo()
    self._is_fleet()
    self._is_explorer()
    self._is_fw()
    self._is_awox()
    self._is_pure()
    self._set_space_type_flag()
    self._is_thera()
    self._set_attacker_ship_category_flags()
    self._set_weapon_flags()

  def _is_trash(self):
    return self.get_ship_flag(self.data['victim']['ship_type_id']) == 'trash'

  def _is_solo(self):
    if self.data['zkb']['solo']:
      self.flags.append('solo')

  def _is_fleet(self):
    if not self.data['zkb']['solo'] and self.attackers['count']['wingspan'] > 1:
      self.flags.append('fleet')

  def _is_explorer(self):
    for item in self.data['victim']['items']:
      if self.is_analyzer(item['flag'], item['item_type_id']):
        self.flags.append('explorer')
        break

  @staticmethod
  def is_analyzer(flag, item_type_id):
    return {
      3581 : True,  # Purloined Sansha Data Analyzer
      22175: True,  # Data Analyzer I
      22177: True,  # Relic Analyzer I
      30832: True,  # Relic Analyzer II
      30834: True,  # Data Analyzer II
      41533: True,  # Ligature Integrated Analyzer
      41534: True,  # Zeugma Integrated Analyzer
    }.get(item_type_id, False) if 19 <= flag <= 26 else False

  def _is_fw(self):
    if 'faction_id' in self.data['victim'] and self.is_fw_faction(self.data['victim']['faction_id']):
      self.flags.append('fw')

  @staticmethod
  def is_fw_faction(factionID):
    return {
      500001: True,
      500002: True,
      500003: True,
      500004: True
    }.get(factionID, False)

  def _is_awox(self):
    if self.data['zkb']['awox']:
      self.flags.append('awox')
      return

    if\
      self.is_pilot_wingspan(self.data['victim']) and\
      self.attackers['count']['wingspan'] >= self.attackers['count']['NPSI']:

      self.flags.append('awox')
      return

  def _is_pure(self):
    if self.attackers['count']['wingspan'] == self.attackers['count']['capsuleer']:
      self.flags.append('pure')

  def _set_space_type_flag(self):
    self.flags.append(self.get_space_type(self.space_class))

  @staticmethod
  def get_space_type(security):
    return {
      'hs' : 'highsec',
      'ls' : 'lowsec',
      'ns' : 'nullsec',
      'c1' : 'anoikis',
      'c2' : 'anoikis',
      'c3' : 'anoikis',
      'c4' : 'anoikis',
      'c5' : 'anoikis',
      'c6' : 'anoikis',
      'c12': 'anoikis',
      'c13': 'anoikis',
      'c14': 'unknown',
      'c15': 'unknown',
      'c16': 'unknown',
      'c17': 'unknown',
      'c18': 'unknown'
    }.get(security, 'unknown')

  def _is_thera(self):
    if self.space_class == 'c12':
      self.flags.append('thera')

  def _set_victim_ship_category_flags(self):
    victim = self.get_ship_flag(self.data['victim']['ship_type_id'])
    for pilot in self.attackers['wingspan']:
      pilot['flags'][victim + '_killer'] = True

  def _set_attacker_ship_category_flags(self):
    for pilot in self.attackers['wingspan']:
      ship = self.get_ship_flag(pilot['ship_type_id'])
      pilot['flags'][ship + '_driver'] = True

  @staticmethod
  def get_ship_flag(ship):
    return LOOKUP.get(ship, 'unknown')

  def _set_weapon_flags(self):
    for pilot in self.attackers['wingspan']:
      weapon = self.get_weapon_flag(pilot['weapon_type_id'])
      pilot['flags'][weapon + '_user'] = True

  @staticmethod
  def get_weapon_flag(weapon):
    return LOOKUP.get(weapon, 'unknown')

  def _process_advanced_flags(self):
    self._is_solo_bomber()
    self._is_industrial()

  def _is_solo_bomber(self):
    if not self.data['zkb']['solo']:
      return

    if self.attackers['count']['wingspan'] < 1:
      return

    if 'bomber_driver' in self.attackers['wingspan'][0]['flags']:
      self.flags.append('solo_bomber')

  def _is_industrial(self):
    victim = self.get_ship_flag(self.data['victim']['ship_type_id'])

    for pilot in self.attackers['wingspan']:
      ship = self.get_ship_flag(self.data['victim']['ship_type_id'])
      if ship in ['transport', 'miner']:
        pilot['flags']['industrial_driver'] = True
      if victim in ['transport', 'miner']:
        pilot['flags']['industrial_killer'] = True

  def _prepare_flags_for_db(self):
    self.data['flags'] = {flag: True for flag in self.flags}

  def _process_attackers(self):
    if len(self.attackers['wingspan']):
      self.attackers['wingspan'][0]['flag_damage'] = True

    for pilot in self.attackers['wingspan']:
      pilot['ship_group_id'] = self.parser.items.get(pilot['ship_type_id'], 0)

    self.data['attackers_processed'] = self.attackers

  def _process_victim(self):
    self.data['victim']['ship_group_id'] = self.parser.items.get(self.data['victim']['ship_type_id'], 0)

  def _process_time(self):
    date = datetime.strptime(self.data['killmail_time'], '%Y-%m-%dT%H:%M:%SZ')
    self.data['date'] = {'year': date.year, 'month': date.month}

  def _check_legitimacy(self):
    if self.attackers['count']['capsuleer'] < 1:
      self.isLegit = False
      return

    if float(self.attackers['count']['wingspan']) / self.attackers['count']['capsuleer'] < StatsConfig.FLEET_COMP:
      self.isLegit = False
      return

    victim = self.data['victim']
    victim_ship_group_id = self.parser.get_ship_group_id(victim['ship_type_id'])
    if 'character_id' not in victim and victim_ship_group_id not in PILOTLESS:
      self.isLegit = False
      return

    if victim_ship_group_id == 237 and self.data['zkb']['totalValue'] < 100000: # Corvette kills less than 100k
      self.isLegit = False
      return

    if victim_ship_group_id == 25 and self.data['zkb']['totalValue'] < 1000000: # Frigate kills less than 1M
      self.isLegit = False
      return

    if victim_ship_group_id == 420 and self.data['zkb']['totalValue'] < 1500000: # Destroyer kills less than 1.5M
      self.isLegit = False
      return

    if victim_ship_group_id == 26 and self.data['zkb']['totalValue'] < 10000000: # Cruiser kills less than 10M
      self.isLegit = False
      return

    if victim_ship_group_id == 28 and self.data['zkb']['totalValue'] < 2000000: # Industrial kills less than 2M
      self.isLegit = False
      return

  def _save(self):
    if self.isLegit:
      table = self.parser.DB.killmails
    else:
      table = self.parser.DB.fail_killmails

    # FIXME should have some intelligent logic to avoid processing same killmails twice
    table.replace_one({'_id': self.data['_id']}, self.data, upsert=True)


# def kills(self):
#   $ret['kills'] = DB::getDB() -> kills -> aggregate([
#     ['$match' => ['killmail_time' => ['$gte' => $month[0], '$lt' => $month[1]]]],
#     ['$unwind' => '$wingspan'],
#     ['$group' => [
#       '_id' => '$wingspan.characterID',
#       'charID' => ['$first' => '$wingspan.characterID'],
#       'charName' => ['$first' => '$wingspan.characterName'],
#       'kills' => ['$sum' => 1]
#     ]],
#     ['$sort' => ['kills' => -1]],
#     ['$limit' => 3]
#   ]) -> toArray();
# def value(self):
#   $ret['value'] = DB::getDB() -> kills -> aggregate([
#     ['$match' => ['killmail_time' => ['$gte' => $month[0], '$lt' => $month[1]]]],
#     ['$unwind' => '$wingspan'],
#     ['$group' => [
#       '_id' => '$wingspan.characterID',
#       'charID' => ['$first' => '$wingspan.characterID'],
#       'charName' => ['$first' => '$wingspan.characterName'],
#       'value' => ['$sum' => '$zkb.totalValue']
#     ]],
#     ['$sort' => ['value' => -1]],
#     ['$limit' => 3]
#   ]) -> toArray();
# def damageDone(self):
#   $ret['damageDone'] = DB::getDB() -> kills -> aggregate([
#     ['$match' => ['killmail_time' => ['$gte' => $month[0], '$lt' => $month[1]]]],
#     ['$unwind' => '$wingspan'],
#     ['$group' => [
#       '_id' => '$wingspan.characterID',
#       'charID' => ['$first' => '$wingspan.characterID'],
#       'charName' => ['$first' => '$wingspan.characterName'],
#       'damageDone' => ['$sum' => '$wingspan.damageDone']
#     ]],
#     ['$sort' => ['damageDone' => -1]],
#     ['$limit' => 3]
#   ]) -> toArray();
# def solo(self):
#   $ret['solo'] = DB::getDB() -> kills -> aggregate([
#     ['$match' => ['wingspan' => ['$size' => 1], 'killmail_time' => ['$gte' => $month[0], '$lt' => $month[1]]]],
#     ['$group' => [
#       '_id' => '$wingspan.characterID',
#       'charID' => ['$first' => '$wingspan.characterID'],
#       'charName' => ['$first' => '$wingspan.characterName'],
#       'kills' => ['$sum' => 1]
#     ]],
#     ['$sort' => ['kills' => -1]],
#     ['$limit' => 3]
#   ]) -> toArray();
# def dedication(self):
#   $ret['dedication'] = DB::getDB() -> kills -> aggregate([
#     ['$match' => ['killmail_time' => ['$gte' => $month[0], '$lt' => $month[1]]]],
#     ['$unwind' => '$wingspan'],
#     ['$group' => [
#       '_id' => ['charID' => '$wingspan.characterID', 'shipTypeID' => '$wingspan.shipTypeID', 'weaponTypeID' => '$wingspan.weaponTypeID'],
#       'charID' => ['$first' => '$wingspan.characterID'],
#       'charName' => ['$first' => '$wingspan.characterName'],
#       'shipTypeID' => ['$first' => '$wingspan.shipTypeID'],
#       'weaponTypeID' => ['$first' => '$wingspan.weaponTypeID'],
#       'damageDone' => ['$sum' => '$wingspan.damageDone'],
#       'kills' => ['$sum' => 1]
#     ]],
#     ['$sort' => ['kills' => -1]],
#     ['$limit' => 1]
#   ]) -> toArray();
