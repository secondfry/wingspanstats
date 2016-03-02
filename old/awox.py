# awox.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class Awox(Skeleton):
    def __init__(self):
        self.file_name = "top_awox"
        self.awox_kills = {}

    def __str__(self):
        output = ""
        output += "Top AWOX kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.awox_kills.keys(),
                key=lambda k: self.awox_kills[k][1],
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {} - {:.2f}m\n".format(
                    place,
                    w,
                    self.awox_kills[w][0],
                    self.awox_kills[w][1] / 1000000.0,
            )
        return output

    def html(self):
        # Preprocess
        self.awox_kills = sorted(self.awox_kills.items(), key=lambda k: k[1][1], reverse=True)

        # Output
        output = "<div class=\"container\">"

        ## Awox
        # Title
        output += "<div class=\"row\"><div class=\"col-xs-12\"><h2>Top AWOX kills</h2></div></div>"

        # First places as cards
        output += "<div class=\"row\">"
        for idx, w in enumerate(self.awox_kills[:3], start=1):
            output += "<div class=\"col-xs-12 col-md-4\"><a href=\"https://zkillboard.com/kill/" + str(w[
                                                                                                           0]) + "/\"><div class=\"card text-center\"><img class=\"card-img-top img-fluid p-a-1\" src=\"https://image.eveonline.com/Character/" + str(
                    w[1][2]) + "_512.jpg\" alt=\"" + w[1][
                          0] + "\"><div class=\"card-block\"><p class=\"card-text\">" + str(idx) + ". " + w[1][
                          0] + " - " + "{:.2f}m".format(w[1][1] / 1000000.0) + " ISK</p></div></div></a></div>"
        output += "</div>"

        # Next places as list
        output += "<div class=\"row\"><div class=\"col-xs-12\"><ol start=\"4\">"
        for idx, w in enumerate(self.awox_kills[3:StatsConfig.MAX_PLACES], start=4):
            output += "<li><a href=\"https://zkillboard.com/kill/" + str(w[0]) + "/\">" + w[1][
                0] + "</a> - " + "{:.2f}m".format(w[1][1] / 1000000.0) + " ISK</li>"
        output += "</ol>"

        return output

    def process_km(self, killmail):
        if killmail['victim']['corporationID'] in StatsConfig.CORP_IDS:
            kill_id = killmail['killID']
            isk_destroyed = killmail['zkb']['totalValue']
            victim_name = killmail['victim']['characterName']
            victim_id = killmail['victim']['characterID']

            self.awox_kills[kill_id] = [victim_name, isk_destroyed, victim_id]
