from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import logging


# br = mechanize.Browser()
# br.open("https://www.goodreads.com/book/show/61231")

def scrape(id_goodreads):
    url = f"https://www.goodreads.com/book/show/{id_goodreads}"

    page = urlopen(url)

    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    # print("soup: ", soup.find_all("ul", class_="CollapsableList"), "soup:")
    # print("soup: ", soup.get_text(), "soup:")
    
    uls = soup.find("ul", class_="CollapsableList")
    uls =str(uls)
    index = 0
    genres = []
    first_published = None

    check = uls.find('<span tabindex="-1"><span class="BookPageMetadataSection__genrePlainText"><span class="Text Text__body3 Text__subdued">Genres</span>')
    logging.debug(f"genre uls: {uls}")
    if check == -1:
        logging.debug(f"Check failed, check {check}")
        return (None, None)
    
    while True:

        start = uls.find('<span class="Button__labelItem">')

        if start == -1:
            break
        end = uls[start:].find("</span>")

        gen_start = start+32
        gen_end = start + end

        genres.append(uls[gen_start: gen_end])
        uls = (uls[start + end +7:])

        

    logging.debug(f"genres: {genres}")
    if not genres:
        return

    if genres[-1] == "...more":
        genres.remove("...more")

    if "Audiobook" in genres:
        genres.remove("Audiobook")
    if "Fiction" in genres and len(genres) > 1:
        genres.remove("Fiction")
    if "Literature" in genres and len(genres) > 1:
        genres.remove("Literature")

    uls = soup.find("div", class_="BookDetails")
    uls = str(uls)
    start = uls.find('<p data-testid="publicationInfo">')

    if start != -1 and start:
        end = uls[start:].find("</p>")
        end = start +end
        first_published = uls[end-4:end]


    uls = soup.find("span", class_="ContributorLink__name")
    uls = str(uls)
    end = uls.find("</span>")
    start = uls.find('"name"')
    author =  uls[start+7:end]



    logging.debug(f"returning {genres} and {first_published}")
    return (genres, first_published, author)


