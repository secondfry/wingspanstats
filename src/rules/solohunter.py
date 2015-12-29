# solohunter.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class SoloHunter(Skeleton):

    def __init__(self):
        self.file_name = "solo_hunter.txt"
        self.agent_solo_ships_destroyed = {}
        self.agent_solo_isk_destroyed = {}

    def __str__(self):
        output = ""

        output += "Solo ships destroyed\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.agent_solo_ships_destroyed,
                key=self.agent_solo_ships_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {} ships\n".format(place, w, self.agent_solo_ships_destroyed[w])

        output += "\n"

        output += "Solo ISK destroyed\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.agent_solo_isk_destroyed,
                key=self.agent_solo_isk_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {:.2f}b\n".format(place, w, self.agent_solo_isk_destroyed[w] / 1000000000.0)

        return output

    def process_km(self, killmail):
        isk_destroyed = killmail['zkb']['totalValue']

        [total_non_npc_attackers, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if total_non_npc_attackers == wingspan_attackers and wingspan_attackers == 1:
            # solo kill
            attacker_name = ""
            for attacker in killmail['attackers']:
                if attacker['corporationID'] in StatsConfig.CORP_IDS:
                    attacker_name = attacker['characterName']
                    break

            if attacker_name != "":
                if attacker_name in self.agent_solo_ships_destroyed.keys():
                    self.agent_solo_ships_destroyed[attacker_name] += 1
                else:
                    self.agent_solo_ships_destroyed[attacker_name] = 1

                if attacker_name in self.agent_solo_isk_destroyed.keys():
                    self.agent_solo_isk_destroyed[attacker_name] += isk_destroyed
                else:
                    self.agent_solo_isk_destroyed[attacker_name] = isk_destroyed
