from astropy.coordinates import get_sun
from astropy.time import Time
from datetime import datetime, date
import pytz
from geopy import Point
import math

sun_time = Time('2017-12-6 17:00') #UTC time
sun_position = get_sun(sun_time)
# print(sun_position)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Helo World"}


def is_valid_coordinates(coordinates):
    try:
        Point(coordinates)
        return True
    except ValueError:
        return False



coordinates = "37.4220026, -122.0840409"
print(is_valid_coordinates(coordinates))

def difference_time_between_gmt_and_given(given: datetime):
    gmt = pytz.timezone('GMT')
    current_time_gmt = datetime.now(gmt)
    given_gmt = gmt.localize(given)
    time_difference = given_gmt - current_time_gmt
    return time_difference

def Julian_day(date: date): # D
    Julian_day =((367*date.year)-(int((7/4)*(date.year+int((date.month+9)/12))))+int(275*(date.month/9))+date.day-730531.5)
    return Julian_day

def Solar_longitude(date: date): # L
    return 280.461+0.9856474*Julian_day(date)

def average_sun_share(date: date): # M
    return 357.528+0.9856003*Julian_day(date)

def zodiacal_light(date: date): # Lambda
    lamb = Solar_longitude(date) +1.915*math.sin(average_sun_share(date))+0.02*math.sin(2*M)
    while lamb < 0:
        lamb = lamb + (360*int(lamb/360))
    while lamb > 360:
        lamb = lamb - (360*int(lamb/360))
    return lamb

def zodiac_slope(date: date): #Obliquity
    return 23.439-0.0000004*Julian_day(date)

def right_ascension(date: date): #alpha
    alpha = math.atan(math.cos(zodiac_slope(date))*math.tan(zodiacal_light(date)))
    while alpha < 0:
        alpha = alpha + (360*int(alpha/360))
    while alpha > 360:
        alpha = alpha - (360*int(alpha/360))
    return alpha

def sidereal_time(date: date): # ST
    ST = 100.46 + 0.985647352 * Julian_day(date)
    return ST

def solar_azimuth_angle(date: date): # Dec
    Dec = math.asin(math.sin(zodiac_slope(date))*math.sin(zodiacal_light(date)))

def middle_sun_setting(date: date): # noon
    noon = right_ascension(date) - sidereal_time(date)
    while noon < 0:
        noon = noon + (360*int(noon/360))
    while noon > 360:
        noon = noon - (360*int(noon/360))
    return noon

def UT_noon(date: date, location: Point): # UT Noon
    UT_noon = middle_sun_setting(date) - location.longitude

def local_noon(date: date, location: Point, given: datetime):
    local_noon = UT_noon(date, location)/15 + difference_time_between_gmt_and_given(given)


def asr(Location: Point, date: date, time: datetime):
    dec = solar_azimuth_angle(date)
    asr_alt = math.atan(1+math.tan(Location.latitude - dec)) # check
    asr_arc = math.acos(math.sin(90-asr_alt)-math.sin(dec))*math.sin(Location.latitude)/math.cos(dec)*math.cos(Location.latitude)
    asr_arc = asr_arc/15
    asr_time = local_noon(date, Location, time) + asr_arc
    return {"asr": {asr_time}}

def Durinal_arc(date: date, location: Point):
    dec = solar_azimuth_angle(date)
    Durinal_arc = math.acos(math.sin(-0.8333)-math.sin(dec)*math.sin(location.latitude)/math.cos(dec)*math.cos(location.latitude))
    return Durinal_arc


def sun_rise(Location: Point, data: datetime.date, time: datetime.time):
    sun_rise = local_noon(date, Location, time) - Durinal_arc(date, Location)/15
    return {"sun rise": {sun_rise}}

def msghrib(Location: Point, data: datetime.date, time: datetime.time):
    sun_set = local_noon(date, Location, time) + Durinal_arc(date, Location)/15
    return {"maghrib": {sun_set}}

def isha(Location: Point, data: datetime.date, time: datetime.time):
    dec = solar_azimuth_angle(date)
    isha_arc = math.acos((math.sin(-18)-math.sin(dec)*math.sin(Location.latitude))/(math.cos(dec)*math.cos(Location.latitude)))
    isha_time = local_noon(date, Location, time) + isha_arc/15
    return {"isha": {isha_time}}

def fajr(Location: Point, data: datetime.date, time: datetime.time):
    dec = solar_azimuth_angle(date)
    fajr_arc = math.acos((math.sin(-18)-math.sin(dec)*math.sin(Location.latitude))/(math.cos(dec)*math.cos(Location.latitude)))
    fajr_time = local_noon(date, Location, time) - fajr_arc/15
    return {"fajr": {fajr_time}}











    






#def dhuhr(Location: Point, data: datetime.date, time: datetime.time):


@app.get("/prayer_time/{date}/{longitude}/{latitude}")
async def prayer(date: date, longitude: float, latitude: float):
    locationCheck = f"{longitude}, {latitude}"
    if(not is_valid_coordinates(locationCheck)):
        return {"message": "Invalid coordinates"}
    location = Point(longitude, latitude)  
    prayer_time = {
        "fajr": fajr(location, date, time),
        "sun rise": sun_rise(location, date, time),
        "dhuhr": dhuhr(location, date, time),
        "asr": asr(location, date, time),
        "maghrib": msghrib(location, date, time),
        "isha": isha(location, date, time)

    }