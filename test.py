import requests
import json

index = 0

while True:

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": "", "maxResults": 40, "startIndex": index}

    res = requests.get(url, params=params)
    
    response = res.json()
    print (response)
    print(index)

    index += 40
    if res.status_code == 400:
        print("closing")
        break
