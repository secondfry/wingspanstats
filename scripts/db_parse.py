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
            self.security = {int(rows[0]):rows[1] for rows in reader}

        self.data = {}
        self.persons = {}
        self.result = {}

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

        log(self.LOG_LEVEL, 'Should we parse new data?')
        if timestamp_last < timestamp_check:
            log(self.LOG_LEVEL + 1, 'Yes')
            status = self.STATUS_START
        else:
            log(self.LOG_LEVEL + 1, 'No')
            status = self.STATUS_DONE

        while status != self.STATUS_DONE:
            log(self.LOG_LEVEL, 'Starting parsing ' + timestamp_check.strftime('%Y-%m'))
            status, timestamp_check = self.parse(timestamp_check)
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
                            1: [0, 0],
                            2: [0, 0],
                            3: [0, 0],
                            4: [0, 0],
                            5: [0, 0],
                            6: [0, 0],
                            7: [0, 0],
                            8: [0, 0],
                            9: [0, 0],
                            10: [0, 0],
                            11: [0, 0],
                            12: [0, 0],
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

        self.leaderboard('kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills'])
        self.leaderboard('lasthits', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['lasthits'])
        self.leaderboard('value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['value'])
        self.leaderboard('kills_explorer', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_explorer'][0])
        self.leaderboard('value_explorer', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_explorer'][1])
        self.leaderboard('kills_fw', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_fw'][0])
        self.leaderboard('value_fw', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_fw'][1])
        self.leaderboard('kills_solo', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_solo'][0])
        self.leaderboard('value_solo', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_solo'][1])
        self.leaderboard('kills_fleet', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_solo'][0])
        self.leaderboard('value_fleet', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['kills_solo'][1])
        self.leaderboard('kills_space_hs', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][1][0])
        self.leaderboard('value_space_hs', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][1][1])
        self.leaderboard('kills_space_ls', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][2][0])
        self.leaderboard('value_space_ls', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][2][1])
        self.leaderboard('kills_space_ns', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][3][0])
        self.leaderboard('value_space_ns', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][3][1])
        self.leaderboard('kills_space_c123', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona:
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][4][0] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][5][0] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][6][0])
        self.leaderboard('value_space_c123', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona:
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][4][1] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][5][1] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][6][1])
        self.leaderboard('kills_space_c456', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona:
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][7][0] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][8][0] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][9][0])
        self.leaderboard('value_space_c456', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona:
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][7][1] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][8][1] +
                            self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][9][1])
        self.leaderboard('kills_space_c12', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][10][0])
        self.leaderboard('value_space_c12', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][10][1])
        self.leaderboard('kills_space_c13', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][11][0])
        self.leaderboard('value_space_c13', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][11][1])
        self.leaderboard('kills_space_unknown', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][12][0])
        self.leaderboard('value_space_unknown', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['space'][12][1])
        self.leaderboard('astero_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['astero'][0])
        self.leaderboard('astero_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['astero'][1])
        self.leaderboard('astero_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['astero'][0])
        self.leaderboard('astero_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['astero'][1])
        self.leaderboard('stratios_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['stratios'][0])
        self.leaderboard('stratios_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['stratios'][1])
        self.leaderboard('stratios_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['stratios'][0])
        self.leaderboard('stratios_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['stratios'][1])
        self.leaderboard('nestor_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['nestor'][0])
        self.leaderboard('nestor_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['nestor'][1])
        self.leaderboard('nestor_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['nestor'][0])
        self.leaderboard('nestor_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['nestor'][1])
        self.leaderboard('blops_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['blops'][0])
        self.leaderboard('blops_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['blops'][1])
        self.leaderboard('blops_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['blops'][0])
        self.leaderboard('blops_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['blops'][1])
        self.leaderboard('bomber_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['bomber'][0])
        self.leaderboard('bomber_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['bomber'][1])
        self.leaderboard('bomber_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['bomber'][0])
        self.leaderboard('bomber_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['bomber'][1])
        self.leaderboard('dictor_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['dictor'][0])
        self.leaderboard('dictor_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['dictor'][1])
        self.leaderboard('dictor_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['dictor'][0])
        self.leaderboard('dictor_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['dictor'][1])
        self.leaderboard('recon_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['recon'][0])
        self.leaderboard('recon_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['recon'][1])
        self.leaderboard('recon_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['recon'][0])
        self.leaderboard('recon_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['recon'][1])
        self.leaderboard('t3c_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['t3c'][0])
        self.leaderboard('t3c_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['t3c'][1])
        self.leaderboard('t3c_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['t3c'][0])
        self.leaderboard('t3c_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['t3c'][1])
        self.leaderboard('t3d_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['t3d'][0])
        self.leaderboard('t3d_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['t3d'][1])
        self.leaderboard('t3d_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['t3d'][0])
        self.leaderboard('t3d_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['t3d'][1])
        self.leaderboard('capital_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['capital'][0])
        self.leaderboard('capital_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['capital'][1])
        self.leaderboard('capital_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['capital'][0])
        self.leaderboard('capital_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['capital'][1])
        self.leaderboard('industrial_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['industrial'][0])
        self.leaderboard('industrial_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['industrial'][1])
        self.leaderboard('industrial_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['industrial'][0])
        self.leaderboard('industrial_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['industrial'][1])
        self.leaderboard('miner_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['miner'][0])
        self.leaderboard('miner_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['miner'][1])
        self.leaderboard('miner_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['miner'][0])
        self.leaderboard('miner_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['miner'][1])
        self.leaderboard('pod_driver_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['pod'][0])
        self.leaderboard('pod_driver_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['ships_categories']['pod'][1])
        self.leaderboard('pod_killer_kills', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['pod'][0])
        self.leaderboard('pod_killer_value', self.persons[timestamp_check.strftime('%Y-%m')],
                         lambda persona: self.persons[timestamp_check.strftime('%Y-%m')][persona]['victims_categories']['pod'][1])

        file_name = os.path.join(res_dir_date, timestamp_check.strftime('%Y-%m') + '_result.json')
        with open(file_name, 'w') as f_out:
            f_out.write(json.dumps(self.result))
        log(self.LOG_LEVEL, 'Saved leaderboard to json')

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

    def leaderboard(self, name, array, key):
        self.result[name] = {}
        for idx, persona in enumerate(
                sorted(
                        array,
                        key=key, reverse=True
                )[0:StatsConfig.MAX_PLACES], start=1
        ):
            persona_id = persona
            persona = array[persona]
            self.result[name][idx] = {'charID': persona_id, 'charName': persona['name'], 'kills': persona['kills'], 'value': persona['value']}


def security_value(security):
    return {
        'hs': 1,
        'ls': 2,
        'ns': 3,
        'c1': 4,
        'c2': 5,
        'c3': 6,
        'c4': 7,
        'c5': 8,
        'c6': 9,
        'c12': 10,
        'c13': 11,
        'c14': 12,
        'c15': 12,
        'c16': 12,
        'c17': 12,
        'c18': 12
    }.get(security, 12)


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
