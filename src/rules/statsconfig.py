# statsconfig.py
# Author: Valtyr Farshield

import os
import requests
import re


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

    @staticmethod
    def decode_extended(chr):
        if ord('A') <= ord(chr) <= ord('Z'):
            return ord(chr) - ord('A')
        elif ord('a') <= ord(chr) <= ord('z'):
            return 26 + ord(chr) - ord('a')
        elif ord('0') <= ord(chr) <= ord('9'):
            return 52 + ord(chr) - ord('0')
        elif chr == '.':
            return 62
        elif chr == '-':
            return 63
        else:
            return -1

    @staticmethod
    def member_count(corp_name, start_date, stop_date):
        url = "http://evemaps.dotlan.net/corp/{}/stats/{}:{}".format(corp_name, start_date, stop_date)
        result = requests.get(url)

        data_points = 0
        avg_member_count = 0

        match_obj = re.findall("chds=([0-9]+),([0-9]+)", result.text, re.MULTILINE)
        graph_range = float(match_obj[-1][1])

        match_obj = re.findall("chd=e:([a-zA-Z0-9.-]+)", result.text, re.MULTILINE)
        if len(match_obj) >= 1:
            encoded_data = match_obj[-1]
            encoded_data = encoded_data.encode('ascii', 'ignore')

            for code in [encoded_data[i:i+2] for i in range(0, len(encoded_data), 2)]:
                decoded_nr = StatsConfig.decode_extended(code[0]) * 64 + StatsConfig.decode_extended(code[1])
                member_count = decoded_nr / 4095.0 * graph_range
                avg_member_count += int(round(member_count))
                data_points += 1
        else:
            match_obj = re.findall("chd=s:([a-zA-Z0-9.-]+)", result.text, re.MULTILINE)
            if match_obj:
                encoded_data = match_obj[-1]
                encoded_data = encoded_data.encode('ascii', 'ignore')
                for code in encoded_data:
                    decoded_nr = StatsConfig.decode_extended(code)
                    member_count = decoded_nr / 63.0 * graph_range
                    avg_member_count += int(round(member_count))
                    data_points += 1
            else:
                avg_member_count = 0
                data_points = 1

        avg_member_count = avg_member_count / float(data_points)
        avg_member_count = int(round(avg_member_count))
        return avg_member_count


def main():
    print StatsConfig.member_count("WiNGSPAN Delivery Services".replace(" ", "_"), "2015-06-01", "2015-06-31")

if __name__ == "__main__":
    main()
