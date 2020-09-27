import time
from datetime import date

day = 31
month = 12
year = 2020

dateobj = date(year, month, day)
datestr = str(dateobj)

print(type(dateobj))
print(type(datestr))