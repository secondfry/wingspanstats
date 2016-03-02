# statsconfig.py
# Author: Valtyr Farshield

import os


class StatsConfig:
    DATABASE_PATH = os.path.join('..', 'database')
    RESULTS_PATH = os.path.join('..', 'results')

    CORP_IDS = [
        98330748,  # WiNGSPAN Delivery Services
        98415327,  # WiNGSPAN Academy for Enterprising Pilots
    ]

    FLEET_COMP = 0.25
    INCLUDE_AWOX = False

    MAX_PLACES = 25

    @staticmethod
    def attacker_types(killmail):
        total_non_npc_attackers = 0
        wingspan_attackers = 0
        for attacker in killmail['attackers']:

            # Non-NPC attackers
            if attacker['characterName'] != "":
                total_non_npc_attackers += 1

                # Wingspan attackers
                if attacker['corporationID'] in StatsConfig.CORP_IDS:
                    wingspan_attackers += 1

        return [total_non_npc_attackers, wingspan_attackers]
