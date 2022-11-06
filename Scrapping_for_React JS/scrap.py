import bs4
import requests
import json
import time
import dominate
from dominate.tags import *
import re

# Function to Extract values given a key


def json_extract(obj, key):
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    values = extract(obj, arr, key)
    return values


# Open hte saved json file
personInfo = {}
personInfo['person'] = []
with open('personInfo.json', 'r+', encoding='utf-8') as f:
    try:
        personInfo = json.load(f)
    except Exception as e:
        personInfo['person'] = []


# For Checking existing names
existingNames = json_extract(personInfo, 'name')


# Open the json file that contains the person ids (this file is obtained from mediapedia api: list rappeurs français) and search the information on wikipedia
with open('artists_id_from_wikipedia.json') as json_file:
    data = json.load(json_file)
    counter = 0
    for pers in data['categorymembers']:
        # time.sleep(2)
        counter = counter + 1
        # Check if the person is already in the lis or not, process only if he is not in the list
        if pers['title'] in existingNames:
            print("---> " + str(counter) + " - " +
                  str(pers['title']) + " already exists")
        else:
            url = "https://fr.wikipedia.org/?curid="+str(pers['pageid'])
            response = requests.get(url)

            if response is not None:
                html = bs4.BeautifulSoup(response.text, 'html.parser')
                name = html.select("#firstHeading")[0].text
                paragraphs = html.select("p")
                # print from 1 to 3 paragraphs. 0 adds "modifier" in french wikipedia version
                description = '\n'.join(
                    [para.text for para in paragraphs[1:5]])
                # replace some words to avoid plagiarism
                # remove everything in bracket like [2]
                description = re.sub("\[.\]", "", description)
                # remove everything in bracket like [2]
                description = re.sub("\[..\]", "", description)
                # remove everything in bracket like [2]
                description = re.sub("\[...\]", "", description)
                description = description.replace("modifier", "")
                description = description.replace(
                    "est un rappeur", "est connu comme étant un chanteur rappeur")
                description = description.replace(
                    "de son vrai nom", " dont le nom de naissance est")
                description = description.replace(
                    "son premier album", "son tout premier disque")
                description = description.replace(
                    "son deuxième album", "son second gros projet")
                description = description.replace(
                    "un rappeur français", "un musicien rappeur francophone")
                description = description.replace(
                    "publie son premier", "fait la publication de son tout premier")
                description = description.replace(
                    "dans le val-de-marne", "en région parisienne")
                description = description.replace(
                    "dans le val-d'oise", "en région parisienne")
                description = description.replace("français", "francophone", 1)
                description = description.replace(
                    "intitulé", "dont le nom est")
                description = description.replace(
                    "sa carrière", "son parcours")
                description = description.replace("artiste", "créateur")
                description = description.replace("groupe ", "crew ")
                description = description.replace("groupes ", "crews ")
                description = description.replace(
                    "participent à des", "font partie de")
                description = description.replace(
                    "participe à des", "fait partie de")
                description = description.replace(
                    "à l'âge de", "l'année de ses")
                description = description.replace(
                    "premier album solo", "tout premier album personnel")
                description = description.replace("par la suite", "Plus tard")
                description = description.replace(
                    "membre du groupe", "fait partie du comié")
                description = description.replace(
                    "il commence à", "Il débute par")
                description = description.replace(
                    "groupe de rap", "crew de rappeurs")
                description = description.replace(
                    "sous le nom", "avec comme blaz")
                description = description.replace(
                    "nom de scène", "blaz d'artiste")
                description = description.replace("d'un père", "d'un papa")
                description = description.replace("d'une mère", "d'une maman")

                images = html.select(
                    'div.infobox_v3 div.images a.image img[src]')
                if not images:
                    image = ""
                    print("Done:" + str(counter) + " - " +
                          name + " -------> No Image")
                else:
                    image = images[0]['src']
                    print("Done:" + str(counter) + " - " + name)

                # create HTML page
                pageTitle = 'Taille-' + name
                doc = dominate.document(title=pageTitle)

                with doc.head:
                    meta(charset="UTF-8")
                    meta(name="viewport",
                         content="width=device-width, initial-scale=1")
                    link(rel='stylesheet', href='style.css')
                    #script(type='text/javascript', src='script.js')

                with doc.body:
                    attr(cls='')

                if not images:
                    image = '//SITENAME.fr/wp-content/uploads/2020/06/QUELLE-Taille-1-1.png'
                with doc:
                    with div():
                        attr(cls='card')
                        with h3(name):
                            attr(cls='name')
                        with img():
                            attr(cls='image', src='http:'+image, alt=name)
                        with h3('...ans'):
                            attr(cls='age')
                        with span('🍂'):
                            attr(cls='emoji')
                        descriptions = description.split('\n')
                        for descrip in descriptions:
                            with p(descrip):
                                attr(cls="description")
                        with div():
                            with a():
                                attr(href="http://www.SITENAME.fr")
                                with button():
                                    attr(cls='button button3')
                                    span('Retour')
                # remove all / in the title, otherwise it will exept a folder
                pageTitle = pageTitle.replace('/', '-')
                pageTitle = pageTitle.replace(':', '-')
                pageTitle = pageTitle.replace(' ', '-')
                pageTitle = pageTitle.replace('ç', 'c')
                pageTitle = pageTitle.replace('é', 'e')
                pageTitle = pageTitle.replace('ë', 'e')
                pageTitle = pageTitle.replace('è', 'e')
                pageTitle = pageTitle.replace('ï', 'i')
                pageTitle = pageTitle.replace('Ä', 'a')
                pageTitle = pageTitle.replace('\'', '')
                pageTitle = pageTitle.replace('à', 'a')
                pageTitle = pageTitle.replace('ê', 'e')
                pageTitle = pageTitle.replace('_', '-')
                pageTitle = pageTitle.replace('(', '')
                pageTitle = pageTitle.replace(')', '')
                pageTitle = pageTitle.replace('î', 'i')

                path = 'articles/'+pageTitle + '.html'
                with open(path, 'w', encoding='utf-8') as htmlfile:
                    htmlfile.write(doc.render())

                #add in json
                url = 'http://SITENAME.fr/'+path
                personInfo['person'].append({
                    'name': name,
                    'image': image,
                    'description': description,
                    'url': url
                })
                with open('personInfo.json', 'w', encoding='utf-8') as f:
                    json.dump(personInfo, f, ensure_ascii=False, indent=4)
