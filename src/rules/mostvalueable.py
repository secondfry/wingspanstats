# mostvalueable.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class MostValueable(Skeleton):

    def __init__(self):
        self.file_name = "most_valueable.txt"
        self.most_valueable = {}

    def __str__(self):
        output = ""
        output += "Most valueable kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable,
                key=self.most_valueable.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {:.2f}b\n".format(
                place,
                w,
                self.most_valueable[w] / 1000000000.0,
            )

        return output

    def process_km(self, killmail):
        kill_id = killmail['killID']
        isk_destroyed = killmail['zkb']['totalValue']
        self.most_valueable[kill_id] = isk_destroyed


class MostValueableSolo(Skeleton):

    def __init__(self):
        self.file_name = "most_valueable_solo.txt"
        self.most_valueable_solo = {}

    def __str__(self):
        output = ""
        output += "Most valueable solo kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable_solo.keys(),
                key=lambda k: self.most_valueable_solo[k][1],
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {} - {:.2f}b\n".format(
                place,
                w,
                self.most_valueable_solo[w][0],
                self.most_valueable_solo[w][1] / 1000000000.0,
            )

        return output

    def process_km(self, killmail):
        kill_id = killmail['killID']
        isk_destroyed = killmail['zkb']['totalValue']

        [total_non_npc_attackers, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if total_non_npc_attackers == wingspan_attackers and wingspan_attackers == 1:
            # solo kill
            attacker_name = ""
            for attacker in killmail['attackers']:
                if attacker['corporationID'] in StatsConfig.CORP_IDS:
                    attacker_name = attacker['characterName']
                    break

            self.most_valueable_solo[kill_id] = [attacker_name, isk_destroyed]
