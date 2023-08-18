import urllib3

resp = urllib3.request('GET',
    'https://api.zippopotam.us/us/94530')
result = resp.json()

print(result)
