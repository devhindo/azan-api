from datetime import datetime
from datetime import date
import pytz

today = date.today()
now = datetime.now()
#print(now)
gmt = pytz.timezone('GMT')
current_time_gmt = datetime.now(gmt)
given = gmt.localize(now)

#print(current_time_gmt)

time_difference = given - current_time_gmt
#print(time_difference)

print(type(today))
print(today.year)