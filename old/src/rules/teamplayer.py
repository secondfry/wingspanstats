# teamplayer.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class TeamPlayer(Skeleton):

    def __init__(self):
        self.file_name = "team_player"
        self.agent_ships_destroyed = {}
        self.agent_isk_destroyed = {}
        self.agent_name_id = {}

    def __str__(self):
        output = ""

        output += "Ships destroyed in a fleet\n"
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

        output += "ISK destroyed in a fleet\n"
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
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Ships destroyed in a fleet</h2></div></div>"

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
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>ISK destroyed in a fleet</h2></div></div>"

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

        [_, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if wingspan_attackers > 1:
            # fleet kill

            for attacker in killmail['attackers']:
                if attacker['corporationID'] in StatsConfig.CORP_IDS:
                    attacker_name = attacker['characterName']
                    attacker_id = attacker['characterID']

                    if attacker_name != "":
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
