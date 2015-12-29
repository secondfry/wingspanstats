# bombingrun.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class BombingRun(Skeleton):

    def __init__(self):
        self.file_name = "bombing_run_specialist.txt"
        self.agent_ships_destroyed = {}
        self.agent_isk_destroyed = {}


    def __str__(self):
        output = ""

        output += "Top Bombing Run Specialists - ships destroyed\n"
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

        output += "Top Bombing Run Specialists - ISK destroyed\n"
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
        isk_destroyed = killmail['zkb']['totalValue']

        for attacker in killmail['attackers']:
            attacker_name = attacker['characterName']
            attacker_corp = attacker['corporationID']
            weapon_type = attacker['weaponTypeID']

            if attacker_name != "" and attacker_corp in StatsConfig.CORP_IDS:
                if weapon_type in [27916, 27920, 27918, 27912]:
                    if attacker_name in self.agent_ships_destroyed.keys():
                        self.agent_ships_destroyed[attacker_name] += 1
                    else:
                        self.agent_ships_destroyed[attacker_name] = 1

                    if attacker_name in self.agent_isk_destroyed.keys():
                        self.agent_isk_destroyed[attacker_name] += isk_destroyed
                    else:
                        self.agent_isk_destroyed[attacker_name] = isk_destroyed
