# wingspanstats.py
# Author: Valtyr Farshield

import os
import json

from rules.statsconfig import StatsConfig
from rules.generalstats import GeneralStats
from rules.topagent import TopAgent
from rules.topship import TopShip
from rules.mostvalueable import MostValueable, MostValueableSolo
from rules.solohunter import SoloHunter
from rules.teamplayer import TeamPlayer
from rules.awox import Awox
from rules.blops import Blops
from rules.bombers import Bombers
from rules.astero import Astero
from rules.stratios import Stratios
from rules.nestor import Nestor
from rules.recons import Recons
from rules.t3cruiser import T3Cruiser
from rules.capitals import Capitals
from rules.explorerhunter import ExplorerHunter
from rules.minerbumper import MinerBumper
from rules.industrygiant import IndustryGiant
from rules.bombingrun import BombingRun
from rules.interdictorace import InterdictorAce
from rules.podexpress import PodExpress
from rules.theracrusader import TheraCrusader


def defined_rules():
    return [
        GeneralStats(),
        TopAgent(),
        TopShip(),
        MostValueable(),
        MostValueableSolo(),
        SoloHunter(),
        TeamPlayer(),
        Blops(),
        Bombers(),
        Astero(),
        Stratios(),
        Nestor(),
        Recons(),
        T3Cruiser(),
        Capitals(),
        ExplorerHunter(),
        MinerBumper(),
        IndustryGiant(),
        BombingRun(),
        InterdictorAce(),
        PodExpress(),
        TheraCrusader(),
    ]


def extract_killmails(file_name, rules_alltime, rules_monthly, awox_alltime, awox_monthly):
    with open(file_name) as data_file:
        data = json.load(data_file)

    for killmail in data:
        awox_alltime.process_km(killmail)
        awox_monthly.process_km(killmail)
        awox = False
        if killmail['victim']['corporationID'] in StatsConfig.CORP_IDS:
            awox = True

        [total_non_npc_attackers, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if total_non_npc_attackers > 0:
            if not awox or StatsConfig.INCLUDE_AWOX:
                if float(wingspan_attackers) / float(total_non_npc_attackers) >= StatsConfig.FLEET_COMP:
                    for rule in rules_alltime:
                        rule.process_km(killmail)
                    for rule in rules_monthly:
                        rule.process_km(killmail)


def analyze_data(db_list):
    rules_alltime = defined_rules()
    awox_alltime = Awox()

    for (year, month) in db_list:
        db_dir = os.path.join(StatsConfig.DATABASE_PATH, "{}-{:02d}".format(year, month))

        if os.path.exists(db_dir):
            rules_monthly = defined_rules()
            awox_monthly = Awox()
            print "Analyzing", db_dir

            page_nr = 1
            while True:
                file_name = os.path.join(db_dir, "{}-{:02d}_{:02d}.json".format(year, month, page_nr))

                if os.path.exists(file_name):
                    extract_killmails(file_name, rules_alltime, rules_monthly, awox_alltime, awox_monthly)
                    page_nr += 1
                else:
                    break

            for rule in rules_monthly:
                rule.output_results(os.path.join(StatsConfig.RESULTS_PATH, "{}-{:02d}".format(year, month)))
            awox_monthly.output_results(os.path.join(StatsConfig.RESULTS_PATH, "{}-{:02d}".format(year, month)))

    for rule in rules_alltime:
        rule.output_results(os.path.join(StatsConfig.RESULTS_PATH, '__alltime__'))
    awox_alltime.output_results(os.path.join(StatsConfig.RESULTS_PATH, '__alltime__'))


def main():
    analyze_data([
        (2014, 7),
        (2014, 8),
        (2014, 9),
        (2014, 10),
        (2014, 11),
        (2014, 12),
        (2015, 1),
        (2015, 2),
        (2015, 3),
        (2015, 4),
        (2015, 5),
        (2015, 6),
        (2015, 7),
        (2015, 8),
        (2015, 9),
        (2015, 10),
        (2015, 11),
        (2015, 12),
        (2016, 1),
        (2016, 2),
        (2016, 3),
        (2016, 4),
        (2016, 5),
        (2016, 6),
    ])

if __name__ == "__main__":
    main()
