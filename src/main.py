from astropy.coordinates import get_sun
from astropy.time import Time

from geopy import Point

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


@app.get("/prayer/{prayer_name}/{data}/{longitude}/{latitude}")
async def prayer(prayer_name: str, longitude: float, latitude: float):
    locationCheck = f"{longitude}, {latitude}"
    if(not is_valid_coordinates(locationCheck)):
        return {"message": "Invalid coordinates"}
    location = Point(longitude, latitude)    
    return {"prayer_name": prayer_name, "location": locationCheck}
