import requests
from bs4 import BeautifulSoup
import time
import logging
from countries import *

AIRTABLE_TOKEN = "patuutHG4fw7LszmL.bdbace627b447277dd6eb51915ed5dbfcfa7f303b14deda7d7db7ef229cf95d5"
AIRTABLE_TABLE_URL = "https://api.airtable.com/v0/appYcSafnpm1UhWrT/tblmrPGNxkfkfySES"
AEROTHEME_URL = "https://www.astrotheme.fr/celestar/filtres.php"
START = 1
MAX = 20000000
POLITENESS = 100
SLEEP = 61
SAVE_HTML = False

logging.basicConfig(filename="logging.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
for country in countries[61:]:
    logging.info("-----------> Country: " + country[1])
    form_data = {
        "sexe": "M|F",
        "tri": "0",
        "categorie[0]": "0|1|2|3|4|5|6|7|8|9|10|11|12",  # All categories selected
        "connue": "0|1",  # Indifferent
        "pays": country[0],  #  You can change this to select another country
        # "fourchette": "0",  # Filter by birth year activated
        # "annee[0]": "1980",
        # "annee[1]": "1990",
    }
    response = requests.post(AEROTHEME_URL, data=form_data)
    cookies = response.cookies.get_dict()

    # Get Last Page Number
    soup = BeautifulSoup(response.content, "html.parser")
    last_page_link = soup.find("a", string="Fin")
    MAX = int(last_page_link["href"].split("=")[-1] if last_page_link else 1)
    logging.info("-----------> Last Page Number: " + str(MAX))

    for page_number in range(START, MAX + 1):
        logging.info("-----------> Starting Page Number: " + str(page_number))
        if page_number % POLITENESS == 0:
            # Refresh Connexion and Cookies every POLITENESS pages (approx. 100*POLITENESS records) to avoid being flagged
            response = requests.post(AEROTHEME_URL, data=form_data)
            cookies = response.cookies.get_dict()
            print("-----------> Sleeping")
            time.sleep(SLEEP)

        # Use the extracted cookie in subsequent requests
        response = requests.get(AEROTHEME_URL + "?page=" + str(page_number), cookies=cookies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            if SAVE_HTML:
                with open("parsed_content.html", "w", encoding="utf-8") as file:
                    file.write(str(response.headers))
            divs_with_id = soup.find_all("div", id=True)
            print(f"Results from page {page_number}:")
            for div in divs_with_id:
                try:
                    name = div.find("div", class_="titreFiche").a
                    name.find("span").extract()
                    name = name.text
                    birthdate = [
                        td.find_next_sibling("td").text.strip()
                        for td in div.find_all("td", string=["Né le : ", "Née le : "])
                    ][0]
                    birthplace = div.find("td", string="à :").find_next_sibling("td").text.strip()
                    height = div.find("td", string="Taille :").find_next_sibling("td").a.text.strip()
                    status = "Ready"
                    # print("Nom:", name)
                    # print("Date de naissance:", birthdate)
                    # print("Taille:", height)
                    # print()

                    # POST To AIRTABLE
                    try:
                        airtable_headers = {
                            "Authorization": "Bearer " + AIRTABLE_TOKEN,
                            "Content-Type": "application/json",
                        }
                        airtable_data = {
                            "fields": {
                                "Name": name,
                                "height": height,
                                "Birthdate": birthdate,
                                "Birthplace": birthplace,
                                "Status": status,
                                "Country": country[1],
                            },
                            "typecast": True,
                        }
                        response = requests.post(AIRTABLE_TABLE_URL, headers=airtable_headers, json=airtable_data)
                        print(response.status_code)
                        print(response.json())
                    except Exception as i:
                        print(i)
                        exit(0)
                except Exception as e:
                    print()
        else:
            print(f"Failed to retrieve page {page_number}. Status code:", response.status_code)
