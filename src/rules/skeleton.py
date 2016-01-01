# skeleton.py
# Author: Valtyr Farshield

import os


class Skeleton():

    def __init__(self):
        self.file_name = "skeleton"

    def __str__(self):
        output = ""
        return output

    def html(self):
        return str(self)

    def process_km(self, killmail):
        pass

    def additional_processing(self, directory):
        pass

    def output_results(self, directory, output):
        if not os.path.exists(directory):
            os.makedirs(directory)

        if output == "text":
            self.file_name += '.txt'
            data = str(self)
        else:
            self.file_name += '.html'
            data = self.html()

        file_full_path = os.path.join(directory, self.file_name)
        with open(file_full_path, 'w') as f_out:
            f_out.write(data)
        self.additional_processing(directory)
