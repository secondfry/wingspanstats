# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from scripts.log import log
from config.statsconfig import StatsConfig
from datetime import date, datetime
import os
import json
import csv
import shutil


class DbParse(object):
    STATUS_DONE = 0
    STATUS_START = 1
    STATUS_ONGOING = 2
    LOG_LEVEL = 1

    def __init__(self):
        log(self.LOG_LEVEL, 'Starting DB parser')

        with open(os.path.join(StatsConfig.SCRIPTS_PATH, 'security.csv'), mode='r') as infile:
            reader = csv.reader(infile)
            self.security = {int(rows[0]): rows[1] for rows in reader}

        self.data = {}
        self.persons = {}
        self.result = {}
        self.isForced = False

        self.parse_db()

    def parse_db(self):
        self.LOG_LEVEL += 1
        db_dir = None

        log(self.LOG_LEVEL, 'Checking results directory')
        if not os.path.isdir(StatsConfig.RESULTS_PATH):
            os.mkdir(StatsConfig.RESULTS_PATH)
        else:
            db_dir = os.listdir(StatsConfig.RESULTS_PATH)

        log(self.LOG_LEVEL, 'Finding timestamp to check')
        timestamp_today = date.today()
        if timestamp_today.month == 1:
            timestamp_check = timestamp_today.replace(year=timestamp_today.year - 1, month=12, day=1)
        else:
            timestamp_check = timestamp_today.replace(month=timestamp_today.month - 1, day=1)
        log(self.LOG_LEVEL, 'Will check: ' + timestamp_check.strftime('%Y-%m-%d'))

        log(self.LOG_LEVEL, 'Finding last checked timestamp')
        if db_dir:
            year_last, month_last = sorted(db_dir)[-1].split("-")
            timestamp_last = datetime.strptime(year_last + month_last, '%Y%m').date()
        else:
            timestamp_last = datetime.strptime('2000', '%Y').date()
        log(self.LOG_LEVEL, 'Last checked: ' + timestamp_last.strftime('%Y-%m-%d'))

        log(self.LOG_LEVEL, 'Is there old months to parse?')
        if timestamp_last < timestamp_check:
            log(self.LOG_LEVEL + 1, 'Yes')
            status = self.STATUS_START
        else:
            log(self.LOG_LEVEL + 1, 'No, parcing this month partial stats')
            res_dir_date = os.path.join(StatsConfig.RESULTS_PATH, timestamp_today.strftime('%Y-%m'))
            if os.path.exists(res_dir_date):
                shutil.rmtree(res_dir_date)
            timestamp_check = timestamp_today.replace(day = 1)
            timestamp_last = timestamp_today.replace(day = 1)
            status = self.STATUS_START
            self.isForced = True

        while status != self.STATUS_DONE:
            log(self.LOG_LEVEL, 'Starting parsing ' + timestamp_check.strftime('%Y-%m'))
            status, timestamp_check = self.parse(timestamp_check)
            if status != self.STATUS_DONE and timestamp_last >= timestamp_check:
                status = self.STATUS_DONE

        log(self.LOG_LEVEL, 'Creating leaderboards')
        self.make_leaderboards(timestamp_last)

        log(self.LOG_LEVEL, 'Done! [database parser]')
        self.LOG_LEVEL -= 1

    def parse(self, timestamp_check):
        self.LOG_LEVEL += 1

        db_dir_date = os.path.join(StatsConfig.DATABASE_PATH, timestamp_check.strftime('%Y-%m'))
        res_dir_date = os.path.join(StatsConfig.RESULTS_PATH, timestamp_check.strftime('%Y-%m'))
        self.data[timestamp_check.strftime('%Y-%m')] = []
        self.persons[timestamp_check.strftime('%Y-%m')] = {}

        if os.path.exists(res_dir_date):
            log(self.LOG_LEVEL, '[Error] Directory already exists, something went wrong')
            raise EnvironmentError('Directory already exists, something went wrong')
        else:
            os.mkdir(res_dir_date)

        page = 1
        while True:
            filepath = os.path.join(db_dir_date, timestamp_check.strftime('%Y-%m') + "_{:02d}.json".format(page))
            if os.path.exists(filepath):
                with open(filepath) as data_file:
                    data = json.load(data_file)

                for killmail_raw in data:
                    ret = self.analyze(killmail_raw)
                    if ret['status']:
                        if not ret['awox'] or StatsConfig.INCLUDE_AWOX:
                            self.data[timestamp_check.strftime('%Y-%m')].append(ret['killmail'])

                page += 1
            else:
                break
        log(self.LOG_LEVEL, 'Fetched ' + str(page) + ' pages')

        file_name = os.path.join(res_dir_date, timestamp_check.strftime('%Y-%m') + '_data.json')
        with open(file_name, 'w') as f_out:
            f_out.write('[')
            for killmail in self.data[timestamp_check.strftime('%Y-%m')]:
                f_out.write(killmail.toJSON())
                f_out.write(',')
            f_out.write(']')
        log(self.LOG_LEVEL, 'Saved data to json')

        for killmail in self.data[timestamp_check.strftime('%Y-%m')]:
            for attacker in killmail.attackers:
                if attacker['characterID'] in self.persons[timestamp_check.strftime('%Y-%m')].keys():
                    persona = self.persons[timestamp_check.strftime('%Y-%m')][attacker['characterID']]
                    persona['kills'] += 1
                    persona['damage'] += attacker['damageDone']
                    persona['lasthits'] += 1 if attacker['finalBlow'] else 0
                    if attacker['weaponTypeID'] in persona['weapons'].keys():
                        persona['weapons'][attacker['weaponTypeID']][0] += 1
                        persona['weapons'][attacker['weaponTypeID']][1] += killmail.value
                    else:
                        persona['weapons'][attacker['weaponTypeID']] = [1, killmail.value]
                    if attacker['shipTypeID'] in persona['ships'].keys():
                        persona['ships'][attacker['shipTypeID']][0] += 1
                        persona['ships'][attacker['shipTypeID']][1] += killmail.value
                    else:
                        persona['ships'][attacker['shipTypeID']] = [1, killmail.value]
                    if killmail.is_explorer:
                        persona['kills_explorer'][0] += 1
                        persona['kills_explorer'][1] += killmail.value
                    if killmail.is_fleet:
                        persona['kills_fleet'][0] += 1
                        persona['kills_fleet'][1] += killmail.value
                    if killmail.is_fw:
                        persona['kills_fw'][0] += 1
                        persona['kills_fw'][1] += killmail.value
                    if killmail.is_solo:
                        persona['kills_solo'][0] += 1
                        persona['kills_solo'][1] += killmail.value
                    if killmail.security_value in persona['space'].keys():
                        persona['space'][killmail.security_value][0] += 1
                        persona['space'][killmail.security_value][1] += killmail.value
                    else:
                        persona['space'][killmail.security_value] = [1, killmail.value]
                    persona['value'] += killmail.value
                    if killmail.victim_ship in persona['victims'].keys():
                        persona['victims'][killmail.victim_ship][0] += 1
                        persona['victims'][killmail.victim_ship][1] += killmail.value
                    else:
                        persona['victims'][killmail.victim_ship] = [1, killmail.value]
                else:
                    self.persons[timestamp_check.strftime('%Y-%m')][attacker['characterID']] = {
                        'name': attacker['characterName'],
                        'kills': 1,
                        'damage': attacker['damageDone'],
                        'lasthits': 1 if attacker['finalBlow'] else 0,
                        'weapons': {
                            attacker['weaponTypeID']: [1, killmail.value]
                        },
                        'ships': {
                            attacker['shipTypeID']: [1, killmail.value]
                        },
                        'kills_explorer': [1, killmail.value] if killmail.is_explorer else [0, 0],
                        'kills_fleet': [1, killmail.value] if killmail.is_fleet else [0, 0],
                        'kills_fw': [1, killmail.value] if killmail.is_fw else [0, 0],
                        'kills_solo': [1, killmail.value] if killmail.is_solo else [0, 0],
                        'space': {
                            '1': [0, 0],
                            '2': [0, 0],
                            '3': [0, 0],
                            '4': [0, 0],
                            '5': [0, 0],
                            '6': [0, 0],
                            '7': [0, 0],
                            '8': [0, 0],
                            '9': [0, 0],
                            '10': [0, 0],
                            '11': [0, 0],
                            '12': [0, 0],
                            killmail.security_value: [1, killmail.value]
                        },
                        'value': killmail.value,
                        'victims': {
                            killmail.victim_ship: [1, killmail.value]
                        },

                    }
        log(self.LOG_LEVEL, 'Killmail analysis done')

        for persona in self.persons[timestamp_check.strftime('%Y-%m')]:
            persona_obj = self.persons[timestamp_check.strftime('%Y-%m')][persona]
            persona_obj['ships_categories'] = self.parse_ships(persona_obj['ships'])
            persona_obj['victims_categories'] = self.parse_ships(persona_obj['victims'])
            persona_obj['weapons_categories'] = self.parse_weapons(persona_obj['weapons'])
        log(self.LOG_LEVEL, 'Categorizing done')

        file_name = os.path.join(res_dir_date, timestamp_check.strftime('%Y-%m') + '_persons.json')
        with open(file_name, 'w') as f_out:
            f_out.write(json.dumps(self.persons[timestamp_check.strftime('%Y-%m')]))
        log(self.LOG_LEVEL, 'Saved persons to json')

        self.LOG_LEVEL -= 1
        if not self.data[timestamp_check.strftime('%Y-%m')]:
            shutil.rmtree(res_dir_date)
            return self.STATUS_DONE, timestamp_check
        if timestamp_check.month == 1:
            timestamp_check = timestamp_check.replace(year=timestamp_check.year - 1, month=12)
        else:
            timestamp_check = timestamp_check.replace(month=timestamp_check.month - 1)
        return self.STATUS_ONGOING, timestamp_check

    def analyze(self, killmail):
        ret = {'status': False}

        is_awox = False
        if killmail['victim']['corporationID'] in StatsConfig.CORPORATION_IDS:
            is_awox = True
        ret['awox'] = is_awox

        attackers_capsuleer, attackers_wingspan, attackers = self.process_attackers(killmail['attackers'])

        if attackers_capsuleer < 1:
            return ret
        if float(attackers_wingspan) / float(attackers_capsuleer) < StatsConfig.FLEET_COMP:
            return ret

        ids = killmail['killID']
        sv = security_value(self.security[killmail['solarSystemID']])
        victim = killmail['victim']['shipTypeID']
        isk = killmail['zkb']['totalValue']
        fw = is_fw(killmail['victim']['factionID'])
        ex = False
        for item in killmail['items']:
            if is_explorer(item['flag'], item['typeID']):
                ex = True
                break
        solo = True if attackers_capsuleer == attackers_wingspan == 1 else False
        fleet = True if attackers_wingspan > 1 else False

        ret['status'] = True
        ret['killmail'] = Killmail(ids, sv, attackers, victim, isk, fw, ex, solo, fleet)
        return ret

    @staticmethod
    def parse_ships(ships):
        rules = [
            'is_astero',
            'is_stratios',
            'is_nestor',
            'is_blops',
            'is_bomber',
            'is_dictor',
            'is_recon',
            'is_t3c',
            'is_t3d',
            'is_capital',
            'is_industrial',
            'is_miner',
            'is_pod'
        ]
        ret = {}
        for rule in rules:
            rule_name = rule.split('_')[1]
            ret[rule_name] = [0, 0]
            for ship in ships.keys():
                if globals()[rule](ship):
                    ret[rule_name][0] += ships[ship][0]
                    ret[rule_name][1] += ships[ship][1]
        return ret

    @staticmethod
    def parse_weapons(weapons):
        rules = [
            'is_bomb',
        ]
        ret = {}
        for weapon in weapons.keys():
            for rule in rules:
                if globals()[rule](weapon):
                    if rule.split('_')[1] in ret.keys():
                        ret[rule.split('_')[1]][0] += weapons[weapon][0]
                        ret[rule.split('_')[1]][1] += weapons[weapon][1]
                    else:
                        ret[rule.split('_')[1]] = weapons[weapon]
        return ret

    @staticmethod
    def process_attackers(attackers):
        attackers_capsuleer = 0
        attackers_wingspan = 0
        attackers_new = []

        for attacker in attackers:
            # Non-NPC attackers
            if attacker['characterName'] != '':
                attackers_capsuleer += 1

                # Wingspan attackers
                if attacker['corporationID'] in StatsConfig.CORPORATION_IDS:
                    attackers_wingspan += 1
                    attackers_new.append({
                        'characterID': attacker['characterID'],
                        'characterName': attacker['characterName'],
                        'damageDone': attacker['damageDone'],
                        'finalBlow': attacker['finalBlow'],
                        'weaponTypeID': attacker['weaponTypeID'],
                        'shipTypeID': attacker['shipTypeID']
                    })

        return attackers_capsuleer, attackers_wingspan, attackers_new

    def mred(self, x, y):
        if isinstance(x, list):
            return x[int(y)]
        else:
            return x.get(y)

    def fare_enumerate(self, sequence, key_list):
        n = 1
        fare = 1
        attr_compare_last = 0
        for elem in sequence:
            yield n, fare, elem
            attr_compare = reduce(lambda x, y: self.mred(x, y), key_list, elem)
            if attr_compare_last != attr_compare:
                fare += 1
            attr_compare_last = attr_compare
            n += 1

    def leaderboard(self, name, key_list, datex, date_last):
        self.result[datex][name] = {}
        data_dictionary = self.persons[datex]

        if len(key_list) > 1:
            key_list_kills = key_list[:-1]
            key_list_kills.append(0)
            key_list_value = key_list[:-1]
            key_list_value.append(1)

        data_list = []
        for key, value in data_dictionary.iteritems():
            value['id'] = key
            data_list.append(value)
        if len(key_list) > 1:
            key_list_secondary = key_list[:-1]
            key_list_secondary.append(1) # Sort by ISK value first
            positions = sorted(data_list,
                               key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list_secondary, item),
                               reverse=True)
            positions = sorted(positions,
                               key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list, item),
                               reverse=True)
        else:
            positions = sorted(data_list,
                               key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list, item),
                               reverse=True)

        if date_last:
            data_dictionary_last = self.persons[date_last]
            data_list_last = []
            for key, value in data_dictionary_last.iteritems():
                value['id'] = key
                data_list_last.append(value)
            if len(key_list) > 1:
                positions_last = sorted(data_list_last,
                                        key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list_secondary, item),
                                        reverse=True)
                positions_last = sorted(positions_last,
                                        key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list, item),
                                        reverse=True)
            else:
                positions_last = sorted(data_list_last,
                                        key=lambda item: reduce(lambda x, y: self.mred(x, y), key_list, item),
                                        reverse=True)
            fare_enum_last = list(self.fare_enumerate(positions_last, key_list))

        fare_enum = list(self.fare_enumerate(positions, key_list))[0:StatsConfig.MAX_PLACES]
        for idx, fare_idx, persona in fare_enum:
            kills_change = 0
            kills_last = 0
            value_change = 0
            value_last = 0
            change = 0
            new = True
            if date_last:
                fare_enum_last_filtered = filter(lambda item: int(item[2]['id']) == persona['id'], fare_enum_last)
                if len(fare_enum_last_filtered):
                    idx_last, fare_idx_last, persona_last = fare_enum_last_filtered[0]
                    if reduce(lambda x, y: self.mred(x, y), key_list, persona_last) != 0:
                        change = idx_last - idx
                        new = False
                        if len(key_list) > 1:
                            kills_last = reduce(lambda x, y: self.mred(x, y), key_list_kills, persona_last)
                            value_last = reduce(lambda x, y: self.mred(x, y), key_list_value, persona_last)
                        else:
                            kills_last = persona_last['kills']
                            value_last = persona_last['value']
            if len(key_list) > 1:
                kills = reduce(lambda x, y: self.mred(x, y), key_list_kills, persona)
                value = reduce(lambda x, y: self.mred(x, y), key_list_value, persona)
            else:
                kills = persona['kills']
                value = persona['value']
            if kills == 0 and value == 0:
                continue
            if not new:
                kills_change = kills - kills_last
                value_change = value - value_last
            self.result[datex][name][idx] = {
                'charID': persona['id'],
                'charName': persona['name'],
                'kills': kills,
                'kills_change': kills_change,
                'value': value,
                'change_value': value_change,
                'change': change,
                'is_new': new,
                'fare': fare_idx
            }

    def make_leaderboards(self, timestamp_last):
        self.LOG_LEVEL += 1
        date_last = ''
        res_dir = sorted(os.listdir(StatsConfig.RESULTS_PATH))
        for datex in res_dir:
            if datex not in self.persons.keys():
                filepath = os.path.join(StatsConfig.RESULTS_PATH, datex, datex + "_persons.json")
                if not os.path.exists(filepath):
                    log(self.LOG_LEVEL, 'Directory which should contain persons.json doesn\'t exist. How? Date: ' + datex)
                    raise SystemExit(0)
                else:
                    with open(filepath) as data_file:
                        self.persons[datex] = json.load(data_file)

            if datex < timestamp_last.strftime('%Y-%m'):
                date_last = datex
                continue

            self.result[datex] = {}
            self.leaderboard('kills', ['kills'], datex, date_last)
            self.leaderboard('lasthits', ['lasthits'], datex, date_last)
            self.leaderboard('value', ['value'], datex, date_last)
            self.leaderboard('kills_explorer', ['kills_explorer', '0'], datex, date_last)
            self.leaderboard('value_explorer', ['kills_explorer', '1'], datex, date_last)
            self.leaderboard('kills_fw', ['kills_fw', '0'], datex, date_last)
            self.leaderboard('value_fw', ['kills_fw', '1'], datex, date_last)
            self.leaderboard('kills_solo', ['kills_solo', '0'], datex, date_last)
            self.leaderboard('value_solo', ['kills_solo', '1'], datex, date_last)
            self.leaderboard('kills_fleet', ['kills_fleet', '0'], datex, date_last)
            self.leaderboard('value_fleet', ['kills_fleet', '1'], datex, date_last)
            self.leaderboard('kills_space_hs', ['space', '1', '0'], datex, date_last)
            self.leaderboard('value_space_hs', ['space', '1', '1'], datex, date_last)
            self.leaderboard('kills_space_ls', ['space', '2', '0'], datex, date_last)
            self.leaderboard('value_space_ls', ['space', '2', '1'], datex, date_last)
            self.leaderboard('kills_space_ns', ['space', '3', '0'], datex, date_last)
            self.leaderboard('value_space_ns', ['space', '3', '1'], datex, date_last)
            self.leaderboard('kills_space_c123', ['space', '4', '0'], datex, date_last)
            self.leaderboard('value_space_c123', ['space', '4', '1'], datex, date_last)
            self.leaderboard('kills_space_c456', ['space', '7', '0'], datex, date_last)
            self.leaderboard('value_space_c456', ['space', '7', '1'], datex, date_last)
            self.leaderboard('kills_space_c12', ['space', '10', '0'], datex, date_last)
            self.leaderboard('value_space_c12', ['space', '10', '1'], datex, date_last)
            self.leaderboard('kills_space_c13', ['space', '11', '0'], datex, date_last)
            self.leaderboard('value_space_c13', ['space', '11', '1'], datex, date_last)
            self.leaderboard('kills_space_unknown', ['space', '12', '0'], datex, date_last)
            self.leaderboard('value_space_unknown', ['space', '12', '1'], datex, date_last)
            self.leaderboard('astero_driver_kills', ['ships_categories', 'astero', '0'], datex, date_last)
            self.leaderboard('astero_driver_value', ['ships_categories', 'astero', '1'], datex, date_last)
            self.leaderboard('astero_killer_kills', ['victims_categories', 'astero', '0'], datex, date_last)
            self.leaderboard('astero_killer_value', ['victims_categories', 'astero', '1'], datex, date_last)
            self.leaderboard('stratios_driver_kills', ['ships_categories', 'stratios', '0'], datex, date_last)
            self.leaderboard('stratios_driver_value', ['ships_categories', 'stratios', '1'], datex, date_last)
            self.leaderboard('stratios_killer_kills', ['victims_categories', 'stratios', '0'], datex, date_last)
            self.leaderboard('stratios_killer_value', ['victims_categories', 'stratios', '1'], datex, date_last)
            self.leaderboard('nestor_driver_kills', ['ships_categories', 'nestor', '0'], datex, date_last)
            self.leaderboard('nestor_driver_value', ['ships_categories', 'nestor', '1'], datex, date_last)
            self.leaderboard('nestor_killer_kills', ['victims_categories', 'nestor', '0'], datex, date_last)
            self.leaderboard('nestor_killer_value', ['victims_categories', 'nestor', '1'], datex, date_last)
            self.leaderboard('blops_driver_kills', ['ships_categories', 'blops', '0'], datex, date_last)
            self.leaderboard('blops_driver_value', ['ships_categories', 'blops', '1'], datex, date_last)
            self.leaderboard('blops_killer_kills', ['victims_categories', 'blops', '0'], datex, date_last)
            self.leaderboard('blops_killer_value', ['victims_categories', 'blops', '1'], datex, date_last)
            self.leaderboard('bomber_driver_kills', ['ships_categories', 'bomber', '0'], datex, date_last)
            self.leaderboard('bomber_driver_value', ['ships_categories', 'bomber', '1'], datex, date_last)
            self.leaderboard('bomber_killer_kills', ['victims_categories', 'bomber', '0'], datex, date_last)
            self.leaderboard('bomber_killer_value', ['victims_categories', 'bomber', '1'], datex, date_last)
            self.leaderboard('dictor_driver_kills', ['ships_categories', 'dictor', '0'], datex, date_last)
            self.leaderboard('dictor_driver_value', ['ships_categories', 'dictor', '1'], datex, date_last)
            self.leaderboard('dictor_killer_kills', ['victims_categories', 'dictor', '0'], datex, date_last)
            self.leaderboard('dictor_killer_value', ['victims_categories', 'dictor', '1'], datex, date_last)
            self.leaderboard('recon_driver_kills', ['ships_categories', 'recon', '0'], datex, date_last)
            self.leaderboard('recon_driver_value', ['ships_categories', 'recon', '1'], datex, date_last)
            self.leaderboard('recon_killer_kills', ['victims_categories', 'recon', '0'], datex, date_last)
            self.leaderboard('recon_killer_value', ['victims_categories', 'recon', '1'], datex, date_last)
            self.leaderboard('t3c_driver_kills', ['ships_categories', 't3c', '0'], datex, date_last)
            self.leaderboard('t3c_driver_value', ['ships_categories', 't3c', '1'], datex, date_last)
            self.leaderboard('t3c_killer_kills', ['victims_categories', 't3c', '0'], datex, date_last)
            self.leaderboard('t3c_killer_value', ['victims_categories', 't3c', '1'], datex, date_last)
            self.leaderboard('t3d_driver_kills', ['ships_categories', 't3d', '0'], datex, date_last)
            self.leaderboard('t3d_driver_value', ['ships_categories', 't3d', '1'], datex, date_last)
            self.leaderboard('t3d_killer_kills', ['victims_categories', 't3d', '0'], datex, date_last)
            self.leaderboard('t3d_killer_value', ['victims_categories', 't3d', '1'], datex, date_last)
            self.leaderboard('capital_driver_kills', ['ships_categories', 'capital', '0'], datex, date_last)
            self.leaderboard('capital_driver_value', ['ships_categories', 'capital', '1'], datex, date_last)
            self.leaderboard('capital_killer_kills', ['victims_categories', 'capital', '0'], datex, date_last)
            self.leaderboard('capital_killer_value', ['victims_categories', 'capital', '1'], datex, date_last)
            self.leaderboard('industrial_driver_kills', ['ships_categories', 'industrial', '0'], datex, date_last)
            self.leaderboard('industrial_driver_value', ['ships_categories', 'industrial', '1'], datex, date_last)
            self.leaderboard('industrial_killer_kills', ['victims_categories', 'industrial', '0'], datex, date_last)
            self.leaderboard('industrial_killer_value', ['victims_categories', 'industrial', '1'], datex, date_last)
            self.leaderboard('miner_driver_kills', ['ships_categories', 'miner', '0'], datex, date_last)
            self.leaderboard('miner_driver_value', ['ships_categories', 'miner', '1'], datex, date_last)
            self.leaderboard('miner_killer_kills', ['victims_categories', 'miner', '0'], datex, date_last)
            self.leaderboard('miner_killer_value', ['victims_categories', 'miner', '1'], datex, date_last)
            self.leaderboard('pod_driver_kills', ['ships_categories', 'pod', '0'], datex, date_last)
            self.leaderboard('pod_driver_value', ['ships_categories', 'pod', '1'], datex, date_last)
            self.leaderboard('pod_killer_kills', ['victims_categories', 'pod', '0'], datex, date_last)
            self.leaderboard('pod_killer_value', ['victims_categories', 'pod', '1'], datex, date_last)

            date_last = datex

            file_name = os.path.join(StatsConfig.RESULTS_PATH, datex, datex + '_result.json')
            with open(file_name, 'w') as f_out:
                f_out.write(json.dumps(self.result[datex], indent=2, sort_keys=True))
            log(self.LOG_LEVEL, 'Saved leaderboard to json')
        self.LOG_LEVEL -= 1


def security_value(security):
    return {
        'hs': '1',
        'ls': '2',
        'ns': '3',
        'c1': '4',
        'c2': '5',
        'c3': '6',
        'c4': '7',
        'c5': '8',
        'c6': '9',
        'c12': '10',
        'c13': '11',
        'c14': '12',
        'c15': '12',
        'c16': '12',
        'c17': '12',
        'c18': '12'
    }.get(security, '12')


def is_fw(factionID):
    return {
        500001: True,
        500002: True,
        500003: True,
        500004: True
    }.get(factionID, False)


def is_explorer(item_flag, item_typeID):
    return {
        3581: True,
        22175: True,
        22177: True,
        30832: True,
        30834: True,
    }.get(item_typeID, False) if 19 <= item_flag <= 26 else False


def is_astero(ship):
    return True if ship == 33468 else False


def is_stratios(ship):
    return True if ship == 33470 else False


def is_nestor(ship):
    return True if ship == 33472 else False


def is_blops(ship):
    return True if ship in [22430, 22440, 22428, 22436] else False


def is_bomber(ship):
    return True if ship in [11377, 12034, 12032, 12038] else False


def is_dictor(ship):
    return True if ship in [
        22460, 22464, 22452, 22456,  # interdictors
        12013, 12017, 11995, 12021,  # heavy interdictors
    ] else False


def is_recon(ship):
    return True if ship in [11969, 11957, 11965, 11963, 20125, 11961, 11971, 11959] else False


def is_t3c(ship):
    return True if ship in [29986, 29990, 29988, 29984] else False


def is_t3d(ship):
    return True if ship in [34317, 34562, 34828, 35683] else False


def is_capital(ship):
    return True if ship in [
        19724, 34339, 19722, 34341, 19726, 34343, 19720, 34345,  # Dreads
        23757, 23915, 24483, 23911,  # Carriers
        23919, 22852, 3628, 23913, 3514, 23917,  # Supers
        11567, 671, 3764, 23773,  # Titans
    ] else False


def is_industrial(ship):
    return True if ship in [
        648, 1944, 33695, 655, 651, 33689, 657, 654,  # industrials
        652, 33693, 656, 32811, 4363, 4388, 650, 2998,  # industrials
        2863, 19744, 649, 33691, 653,  # industrials
        12729, 12733, 12735, 12743,  # blockade runners
        12731, 12753, 12747, 12745,  # deep space transports
        34328, 20185, 20189, 20187, 20183,  # freighters
        28848, 28850, 28846, 28844,  # jump freighters
        28606, 33685, 28352, 33687,  # orca, rorqual
    ] else False


def is_miner(ship):
    return True if ship in [
        32880, 33697, 37135,  # mining frigates
        17476, 17480, 17478,  # mining barges
        22544, 22548, 33683, 22546  # exhumers
    ] else False


def is_pod(ship):
    return True if ship in [670, 33328] else False


def is_bomb(weapon):
    return True if weapon in [27916, 27920, 27918, 27912] else False


class Killmail:
    def __init__(self, ids, sv, attackers, victim, isk, fw, ex, solo, fleet):
        self.killID = ids
        self.security_value = sv
        self.attackers = attackers
        self.victim_ship = victim
        self.value = isk
        self.is_fw = fw
        self.is_explorer = ex
        self.is_solo = solo
        self.is_fleet = fleet

    def __str__(self):
        return str(vars(self))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
