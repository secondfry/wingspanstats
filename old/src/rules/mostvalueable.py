# mostvalueable.py
# Author: Valtyr Farshield

import csv
from skeleton import Skeleton
from statsconfig import StatsConfig


class MostValueable(Skeleton):

    def __init__(self):
        self.file_name = "most_valueable"
        self.most_valueable = {}

        with open('typeIDs.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.items = {int(rows[0]):rows[1] for rows in reader}

    def __str__(self):
        output = ""
        output += "Most valuable kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable.items(),
                key=lambda k: k[1][0],
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {} - {:.2f}b ISK\n".format(
                place,
                w[0],
                self.items[w[1][1]],
                w[1][0] / 1000000000.0,
            )

        return output

    def html(self):
        # Preprocess
        self.most_valueable = sorted(self.most_valueable.items(), key=lambda k: k[1][0], reverse=True)

        # Output
        output = "<div class=\"container\">"

        # Title
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Most valuable kills</h2></div></div>"

        # First places as cards
        output += "<div class=\"row\">"
        for idx,w in enumerate(self.most_valueable[:3], start=1):
            output += "<div class=\"col-xs-12 col-md-4\"><a href=\"https://zkillboard.com/kill/" + str(w[0]) + "/\"><div class=\"card text-center\"><img class=\"card-img-top img-fluid p-a-1\" src=\"https://image.eveonline.com/Render/" + str(w[1][1]) + "_512.png\" alt=\"" + self.items[w[1][1]] + "\"><div class=\"card-block\"><p class=\"card-text\">" + str(idx) + ". " + self.items[w[1][1]] + " - " + "{:.2f}b".format(w[1][0] / 1000000000.0) + " ISK</p></div></div></a></div>"
        output += "</div>"

        # Next places as list
        output += "<div class=\"row\"><div class=\"col-xs-12\"><ol start=\"4\">"
        for idx,w in enumerate(self.most_valueable[3:StatsConfig.MAX_PLACES], start=4):
            output += "<li><a href=\"https://zkillboard.com/kill/" + str(w[0]) + "/\">" + self.items[w[1][1]] + "</a> - " + "{:.2f}b".format(w[1][0] / 1000000000.0) + " ISK</li>"
        output += "</ol>"

        return output

    def process_km(self, killmail):
        kill_id = killmail['killID']
        isk_destroyed = killmail['zkb']['totalValue']
        shipType_destroyed = killmail['victim']['shipTypeID']
        self.most_valueable[kill_id] = (isk_destroyed, shipType_destroyed)


class MostValueableSolo(Skeleton):

    def __init__(self):
        self.file_name = "most_valueable_solo"
        self.most_valueable_solo = {}

        with open('typeIDs.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.items = {int(rows[0]):rows[1] for rows in reader}

    def __str__(self):
        output = ""
        output += "Most valuable solo kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable_solo.items(),
                key=lambda k: k[1][0],
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {} - {} - {:.2f}b ISK\n".format(
                    place,
                    w[0],
                    self.items[w[1][1]],
                    w[1][2],
                    w[1][0] / 1000000000.0,
                    )

        return output

    def html(self):
        # Preprocess
        self.most_valueable_solo = sorted(self.most_valueable_solo.items(), key=lambda k: k[1][0], reverse=True)

        # Output
        output = "<div class=\"container\">"

        # Title
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Most valuable solo kills</h2></div></div>"

        # First places as cards
        output += "<div class=\"row\">"
        for idx,w in enumerate(self.most_valueable_solo[:3], start=1):
            output += "<div class=\"col-xs-12 col-md-4\"><a href=\"https://zkillboard.com/kill/" + str(w[0]) + "/\"><div class=\"card text-center\"><img class=\"card-img-top img-fluid p-a-1\" src=\"https://image.eveonline.com/Render/" + str(w[1][1]) + "_512.png\" alt=\"" + self.items[w[1][1]] + "\"><div class=\"card-block\"><p class=\"card-text\">" + str(idx) + ". " + self.items[w[1][1]] + " - " + "{:.2f}b".format(w[1][0] / 1000000000.0) + " ISK</p></div></div></a></div>"
        output += "</div>"

        # Next places as list
        output += "<div class=\"row\"><div class=\"col-xs-12\"><ol start=\"4\">"
        for idx,w in enumerate(self.most_valueable_solo[3:StatsConfig.MAX_PLACES], start=4):
            output += "<li><a href=\"https://zkillboard.com/kill/" + str(w[0]) + "/\">" + self.items[w[1][1]] + "</a> - " + "{:.2f}b".format(w[1][0] / 1000000000.0) + " ISK</li>"
        output += "</ol>"

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

            shipType_destroyed = killmail['victim']['shipTypeID']
            self.most_valueable_solo[kill_id] = [isk_destroyed, shipType_destroyed, attacker_name]
