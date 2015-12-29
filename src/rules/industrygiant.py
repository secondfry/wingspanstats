# industrygiant.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class IndustryGiant(Skeleton):

    def __init__(self):
        self.file_name = "industry_giant.txt"
        self.agent_ships_destroyed = {}
        self.agent_isk_destroyed = {}


    def __str__(self):
        output = ""

        output += "Top industrial hunters - ships destroyed\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.agent_ships_destroyed,
                key=self.agent_ships_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {} ships\n".format(place, w, self.agent_ships_destroyed[w])

        output += "\n"

        output += "Top industrial hunters - ISK destroyed\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.agent_isk_destroyed,
                key=self.agent_isk_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {:.2f}b\n".format(place, w, self.agent_isk_destroyed[w] / 1000000000.0)

        return output

    def process_km(self, killmail):
        if killmail['victim']['shipTypeID'] in [
            648, 1944, 33695, 655, 651, 33689, 657, 654,  # industrials
            652, 33693, 656, 32811, 4363, 4388, 650, 2998,  # industrials
            2863, 19744, 649, 33691, 653,  # industrials
            12729, 12733, 12735, 12743,  # blockade runners
            12731, 12753, 12747, 12745,  # deep space transports
            34328, 20185, 20189, 20187, 20183,  # freighters
            28848, 28850, 28846, 28844,  # jump freighters
            28606, 33685, 28352, 33687,  # orca, rorqual
        ]:
            isk_destroyed = killmail['zkb']['totalValue']

            for attacker in killmail['attackers']:
                attacker_name = attacker['characterName']
                attacker_corp = attacker['corporationID']

                if attacker_name != "" and attacker_corp in StatsConfig.CORP_IDS:

                    if attacker_name in self.agent_ships_destroyed.keys():
                        self.agent_ships_destroyed[attacker_name] += 1
                    else:
                        self.agent_ships_destroyed[attacker_name] = 1

                    if attacker_name in self.agent_isk_destroyed.keys():
                        self.agent_isk_destroyed[attacker_name] += isk_destroyed
                    else:
                        self.agent_isk_destroyed[attacker_name] = isk_destroyed
