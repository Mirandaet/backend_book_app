import requests
import json

index = 0

while True:

    url = "https://openlibrary.org/subjects/romance.json"
    params = {"limit": 1000, "offset": index}

    res = requests.get(url, params=params)
    print(index)
    
    response = res.json()
    
    if response["works"] is False:
        print("closing")
        break

    for book in response["works"]:
        dic = {"title": book["title"], "author": book["authors"]}
        with open ("books.txt", "a") as f:
            f.write(json.dumps(dic))
            f.write("\n")
    
    index += 1000
