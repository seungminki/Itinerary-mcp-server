from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="fastapi-app", timeout=10)


def get_coordinate(payload):

    for day in payload:
        for order in day["schedule"]:
            lat, lon = address_to_coordinate(order["address"])

            order["latitude"] = lat
            order["longitude"] = lon
    return payload


def address_to_coordinate(address: str):
    location = geolocator.geocode(address)

    if location:
        latitude = location.latitude
        longitude = location.longitude
    else:
        latitude = None
        longitude = None

    return latitude, longitude
