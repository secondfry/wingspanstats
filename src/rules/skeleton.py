# skeleton.py
# Author: Valtyr Farshield

import os


class Skeleton():

    def __init__(self):
        self.file_name = "skeleton.txt"

    def __str__(self):
        output = ""
        return output

    def process_km(self, killmail):
        pass

    def additional_processing(self, directory):
        pass

    def output_results(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_full_path = os.path.join(directory, self.file_name)
        with open(file_full_path, 'w') as f_out:
            f_out.write(str(self))
        self.additional_processing(directory)
