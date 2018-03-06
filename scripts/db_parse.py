#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
import csv
import gzip
import json
import os
import sys
import shutil

from config.statsconfig import StatsConfig
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
  'industrial',
  'miner',
  'pod'
]
SHIPS = {}
SHIPS['astero'] = [33468]
SHIPS['stratios'] = [33470]
SHIPS['nestor'] = [33472]
SHIPS['blops'] = [22430, 22440, 22428, 22436]
SHIPS['bomber'] = [11377, 12034, 12032, 12038]
SHIPS['dictor'] = [
  22460, 22464, 22452, 22456,  # interdictors
  12013, 12017, 11995, 12021,  # heavy interdictors
]
SHIPS['recon'] = [11969, 11957, 11965, 11963, 20125, 11961, 11971, 11959]
SHIPS['t3c'] = [29986, 29990, 29988, 29984]
SHIPS['t3d'] = [34317, 34562, 34828, 35683]
SHIPS['capital'] = [
  19724, 34339, 19722, 34341, 19726, 34343, 19720, 34345,  # Dreads
  23757, 23915, 24483, 23911,  # Carriers
  23919, 22852, 3628, 23913, 3514, 23917,  # Supers
  11567, 671, 3764, 23773,  # Titans
]
SHIPS['industrial'] = [
  648, 1944, 33695, 655, 651, 33689, 657, 654,  # industrials
  652, 33693, 656, 32811, 4363, 4388, 650, 2998,  # industrials
  2863, 19744, 649, 33691, 653,  # industrials
  12729, 12733, 12735, 12743,  # blockade runners
  12731, 12753, 12747, 12745,  # deep space transports
  34328, 20185, 20189, 20187, 20183,  # freighters
  28848, 28850, 28846, 28844,  # jump freighters
  28606, 33685, 28352, 33687,  # orca, rorqual
]
SHIPS['miner'] = [
  32880, # Venture
  33697, # Prospect
  37135, # Endurance
  17476, 17480, 17478,  # mining barges
  22544, 22548, 33683, 22546  # exhumers
]
SHIPS['pod'] = [670, 33328]
LOOKUP = {}
for ship_type, arr in SHIPS.iteritems():
  for ship_id in arr:
    LOOKUP[ship_id] = ship_type


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

  def run(self):
    self._read_pages()
    self._process_db()

  def _read_pages(self):
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

  def _process_db(self):
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
    self.DB.leaderboards.delete_many(query)

    query = {'_id.date.year': {'$gte': timestamp.year + 1}, '_id.date.month': {'$gte': 1}}
    self.DB.months.delete_many(query)
    self.DB.leaderboards.delete_many(query)

  def _process_db_month(self, timestamp):
    self._count_flags(timestamp)
    self._make_leaderboards(timestamp)

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
        # 'killmails': {'$push': '$$ROOT'} # don't need them?
      }
    }
    flags = [
      'solo',
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

    for flag in flags:
      group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$flags.' + flag, 1, 0]}}
      group['$group'][flag + '_value'] = {'$sum': {'$cond': ['$flags.' + flag, '$zkb.totalValue', 0]}}

    for ship in SHIP_RULES:
      flag = ship + '_killer'
      group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, 1, 0]}}
      group['$group'][flag + '_value'] = {
        '$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, '$zkb.totalValue', 0]}
      }

      flag = ship + '_driver'
      group['$group'][flag + '_count'] = {'$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, 1, 0]}}
      group['$group'][flag + '_value'] = {
        '$sum': {'$cond': ['$attackers_processed.wingspan.flags.' + flag, '$zkb.totalValue', 0]}
      }

    query.append(group)
    data = self.DB.killmails.aggregate(query)
    self.DB.months.insert_many(data)

  def _make_leaderboards(self, timestamp):
    query = [
      {'$match': {'_id.date.year': timestamp.year, '_id.date.month': timestamp.month}},
    ]
    flags = [
      'solo',
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
    for ship in SHIP_RULES:
      flags.append(ship + '_killer')
      flags.append(ship + '_driver')

    leaderboard = {
      '_id': {'date': {'year': timestamp.year, 'month': timestamp.month}},
    }

    categories = [flag + '_count' for flag in flags] + [flag + '_value' for flag in flags]
    for category in categories:
      leaderboard[category] = []

      project = {
        '$project': {
          '_id'  : {
            'date': '$_id.date',
            'flag': {'$literal': category}
          },
          'character_id': '$_id.character_id',
          'value': '$' + category
        }
      }
      sort = {'$sort': {
        'value': -1
      }}

      local = deepcopy(query)
      local.append(project)
      local.append(sort)

      data = self.DB.months.aggregate(local)

      place = 0
      rem = 0

      once = True
      for item in data:
        if item['value'] != 0:
          if (item['value'] < rem or rem == 0):
            place += 1
            rem = item['value']
        else:
          if once:
            place += 1
            once = False

        item['place'] = place
        item['change'] = 0

        if item['character_id'] in self.dori_memory and category in self.dori_memory[item['character_id']]:
          item['change'] = self.dori_memory[item['character_id']][category] - place

        if not item['character_id'] in self.dori_memory:
          self.dori_memory[item['character_id']] = {}

        self.dori_memory[item['character_id']][category] = place

        leaderboard[category].append(item)

    self.DB.leaderboards.insert_one(leaderboard)


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
    self._process_attackers()
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
    self._is_solo()
    self._is_fleet()
    self._is_explorer()
    self._is_fw()
    self._is_awox()
    self._is_pure()
    self._set_space_type_flag()
    self._is_thera()
    self._set_ship_flags()

    self.data['flags'] = {flag: True for flag in self.flags}

  def _is_solo(self):
    if self.data['zkb']['solo']:
      self.flags.append('solo')

  def _is_fleet(self):
    if not self.data['zkb']['solo']:
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
    if 'factionID' is self.data['victim'] and self.is_fw_faction(self.data['victim']['factionID']):
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

  def _set_ship_flags(self):
    for pilot in self.attackers['wingspan']:
      ship = self.get_ship_flag(pilot['ship_type_id'])
      pilot['flags'][ship + '_driver'] = True

      ship = self.get_ship_flag(self.data['victim']['ship_type_id'])
      pilot['flags'][ship + '_killer'] = True

  @staticmethod
  def get_ship_flag(ship):
    return LOOKUP.get(ship, 'unknown')

  def _check_legitimacy(self):
    if self.attackers['count']['capsuleer'] < 1:
      self.isLegit = False
      return

    if float(self.attackers['count']['wingspan']) / self.attackers['count']['capsuleer'] < StatsConfig.FLEET_COMP:
      self.isLegit = False
      return

  def _process_attackers(self):
    if len(self.attackers['wingspan']):
      self.attackers['wingspan'][0]['flag_damage'] = True

    self.data['attackers_processed'] = self.attackers

  def _process_time(self):
    date = datetime.strptime(self.data['killmail_time'], '%Y-%m-%dT%H:%M:%SZ')
    self.data['date'] = {'year': date.year, 'month': date.month}

  def _save(self):
    if self.isLegit:
      table = self.parser.DB.killmails
    else:
      table = self.parser.DB.fail_killmails

    try:
      table.insert_one(self.data)
    except:
      pass


def is_bomb(weapon):
  return True if weapon in [27916, 27920, 27918, 27912] else False

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
