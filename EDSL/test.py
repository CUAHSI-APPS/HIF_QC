from Prototype import Flag, TimeSeries, Dataset

DS = Dataset("data/rockland.csv", numHeaderLines=9)
DS2 = Dataset("data/evergreen.csv")
DS3 = Dataset("data/bigelow_soilMTP_2017.csv", numHeaderLines=2)

print(DS)
print(DS2)
print(DS3)
