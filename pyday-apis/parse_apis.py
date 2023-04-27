import urllib3

resp = urllib3.request('GET', 'https://api.zippopotam.us/us/94530')

print(resp.status)
print(resp.json())

# pretty print json
from rich import print
print(resp.json())

lat = resp.json()['places'][0]['latitude']
lon = resp.json()['places'][0]['longitude']

print(lat, lon)

resp2 = urllib3.request('GET', f'https://api.sunrisesunset.io/json?lat={lat}&lng={lon}&timezone=UTC&date=today')
print(resp2.json())

sunrise = resp2.json()['results']['sunrise']
print(sunrise)