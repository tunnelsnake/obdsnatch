import csv


class Config:

    configpath = r"/home/pi/obdsnatch/config.csv"

    def __init__(self):
        pass

    def writeconfig(self):
        pass

    def updateconfig(self):
        pass

    def readconfig(self):
        with open(self.configpath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Colour'] == 'blue':
                    print(row['ID'], row['Make'], row['Colour'])

    def writedefault(self):
        pass