# nestor.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class Nestor(Skeleton):

    def __init__(self):
        self.file_name = "nestor"
        self.agent_ships_destroyed = {}
        self.agent_isk_destroyed = {}
        self.agent_name_id = {}


    def __str__(self):
        output = ""

        output += "Top Nestor pilots - ships destroyed\n"
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

        output += "Top Nestor pilots - ISK destroyed\n"
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

    def html(self):
        # Preprocess
        self.agent_ships_destroyed = sorted(self.agent_ships_destroyed.items(), key=lambda k: k[1], reverse=True)
        self.agent_isk_destroyed   = sorted(self.agent_isk_destroyed.items(),   key=lambda k: k[1], reverse=True)

        # Output
        output = "<div class=\"container\">"

        ## Ships
        # Title
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Top Nestor pilots <small>Ships destroyed</small></h2></div></div>"

        # First places as cards
        output += "<div class=\"row\">"
        for idx,w in enumerate(self.agent_ships_destroyed[:3], start=1):
            output += "<div class=\"col-xs-12 col-md-4\"><a href=\"https://zkillboard.com/character/" + str(self.agent_name_id[w[0]]) + "/\"><div class=\"card text-center\"><img class=\"card-img-top img-fluid p-a-1\" src=\"https://image.eveonline.com/Character/" + str(self.agent_name_id[w[0]]) + "_512.jpg\" alt=\"" + w[0] + "\"><div class=\"card-block\"><p class=\"card-text\">" + str(idx) + ". " + w[0] + " - " + str(w[1]) + " ships</p></div></div></a></div>"
        output += "</div>"

        # Next places as list
        output += "<div class=\"row\"><div class=\"col-xs-12\"><ol start=\"4\">"
        for idx,w in enumerate(self.agent_ships_destroyed[3:StatsConfig.MAX_PLACES], start=4):
            output += "<li><a href=\"https://zkillboard.com/character/" + str(self.agent_name_id[w[0]]) + "/\">" + w[0] + "</a> - " + str(w[1]) + " ships</li>"
        output += "</ol>"

        ## ISK
        # Title
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Top Nestor pilots <small>ISK destroyed</small></h2></div></div>"

        # First places as cards
        output += "<div class=\"row\">"
        for idx,w in enumerate(self.agent_isk_destroyed[:3], start=1):
            output += "<div class=\"col-xs-12 col-md-4\"><a href=\"https://zkillboard.com/character/" + str(self.agent_name_id[w[0]]) + "/\"><div class=\"card text-center\"><img class=\"card-img-top img-fluid p-a-1\" src=\"https://image.eveonline.com/Character/" + str(self.agent_name_id[w[0]]) + "_512.jpg\" alt=\"" + w[0] + "\"><div class=\"card-block\"><p class=\"card-text\">" + str(idx) + ". " + w[0] + " - " + "{:.2f}b".format(w[1] / 1000000000.0) + " ISK</p></div></div></a></div>"
        output += "</div>"

        # Next places as list
        output += "<div class=\"row\"><div class=\"col-xs-12\"><ol start=\"4\">"
        for idx,w in enumerate(self.agent_isk_destroyed[3:StatsConfig.MAX_PLACES], start=4):
            output += "<li><a href=\"https://zkillboard.com/character/" + str(self.agent_name_id[w[0]]) + "/\">" + w[0] + "</a> - " + "{:.2f}b".format(w[1] / 1000000000.0) + " ISK</li>"
        output += "</ol>"

        return output

    def process_km(self, killmail):
        isk_destroyed = killmail['zkb']['totalValue']

        for attacker in killmail['attackers']:
            attacker_name = attacker['characterName']
            attacker_id = attacker['characterID']
            attacker_corp = attacker['corporationID']
            attacker_ship = attacker['shipTypeID']

            if attacker_name != "" and attacker_corp in StatsConfig.CORP_IDS:
                if attacker_ship in [33472]:
                    if attacker_name in self.agent_ships_destroyed.keys():
                        self.agent_ships_destroyed[attacker_name] += 1
                    else:
                        self.agent_ships_destroyed[attacker_name] = 1
                        self.agent_name_id[attacker_name] = attacker_id

                    if attacker_name in self.agent_isk_destroyed.keys():
                        self.agent_isk_destroyed[attacker_name] += isk_destroyed
                    else:
                        self.agent_isk_destroyed[attacker_name] = isk_destroyed
                        self.agent_name_id[attacker_name] = attacker_id
