from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json


# br = mechanize.Browser()
# br.open("https://www.goodreads.com/book/show/61231")

def scrape(id_goodreads):
    print("goodreads: ",id_goodreads)
    url = f"https://www.goodreads.com/book/show/{id_goodreads}"

    page = urlopen(url)

    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    # print("soup: ", soup.find_all("ul", class_="CollapsableList"), "soup:")
    # print("soup: ", soup.get_text(), "soup:")
    
    uls = soup.find("ul", class_="CollapsableList")
    print("uls: ",uls)
    uls =str(uls)
    index = 0
    genres = []
    while True:
        start = str(uls).find('<span class="Button__labelItem">')

        if start == -1:
            break
        end = uls[start:].find("</span>")

        gen_start = start+32
        gen_end = start + end

        genres.append(uls[gen_start: gen_end])
        uls = (uls[start + end +7:])

        # print("uls:", uls
        #       )
        index+=1

    if genres[-1] == "...more":
        genres.remove("...more")
        
    print("genres:", genres)
    return genres
        

    

    # start_index = title_index + len("<title>")
    # end_index = html.find("</title>")
    # title = html[start_index:end_index]

    # pattern = 'data-testid="genresList"'
    # match_results = re.search(pattern, html, re.IGNORECASE)



#     print("match: ", match_results)
#     print("title: ", title)
# # 
    # re.findall("Button__labelItem")
