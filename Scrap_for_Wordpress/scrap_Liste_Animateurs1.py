import bs4
import requests
import json
import time
import dominate
from dominate.tags import *
import re
import uploader
import unidecode
create = 'post'  # 'html' to create html page


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


# Open the saved json file
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
with open('./WikipediaList/Liste_Animateurs1.json', encoding='utf-8') as json_file:
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
                description = ""
                for para in paragraphs[1:5]:
                    if len(para.text) > 10:  # if para has some text
                        # print(para.text)
                        description = str(description) + str(para.text) + '\n'

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
                description = description.replace(
                    "un ancien joueur", "un ex joueur")
                description = description.replace(
                    "déménagé", "changé de logement")
                description = description.replace("finir", "terminer")
                description = description.replace("joué", "travaillé")
                description = description.replace("detient", "a")
                description = description.replace("devenu", "qui devient")
                description = description.replace("joueur", "Player")
                description = description.replace(
                    "sélectionné", "est choisi par la sélection")
                description = description.replace("joueurs", "players")
                description = description.replace("remporte ", "gagne")
                description = description.replace("remportent", "gagnent")
                description = description.replace("évoluant", "jouant")
                description = description.replace("meilleur", "best")
                description = description.replace(
                    "est né le", "voit le jour le")
                description = description.replace("né le", "voyant le jour le")
                description = description.replace("l'équipe", "la team")
                description = description.replace("son équipe", "sa team")

                # Print Info
                pageTitle = 'Taille ' + name
                infobox_v2 = html.select('.infobox_v2')
                if len(infobox_v2) > 0:
                    infoBox = html.select('.infobox_v2')[0]
                    images = infoBox.select('a.image img[src]')
                    tailleTag = infoBox.select_one('th:contains("Taille")')
                    nationaliteTag = infoBox.select_one(
                        'th:contains("Nationalité")')
                    taille = "...m"
                    nationalite = "..."
                    nationaliteLink = "#"
                    image = ""
                    print("Done " + str(counter) + " - " + name)
                    if not tailleTag:
                        print(
                            "\t Taille: No <------------------------------------------")
                    else:
                        taille = tailleTag.parent.select('td')[0].text.strip()
                        print("\t Taille: " + taille)
                    if not nationaliteTag:
                        print(
                            "\t Nationalite: No <------------------------------------------")
                    else:
                        nationalite = nationaliteTag.parent.select('td')[
                            0].text.strip()
                        print("\t Nationalite: " + nationalite)
                        nationaliteLink = unidecode.unidecode(
                            "http://SITENAME.fr/category/"+nationalite.replace('ç', 'c'))
                    if not images:
                        print(
                            "\t Image: No <------------------------------------------")
                    else:
                        image = images[0]['src']
                        print("\t Image: Ok")

                    if create == 'post':  # post article directly on the site

                        #########################################
                        # Add the Wordpress login details
                        #########################################
                        wpLogin = '***'
                        wpPassword = '***'
                        #########################################
                        # The post (article) Details
                        #########################################
                        postTitle = pageTitle  # Post Title
                        postMetaDescription = 'Taille ' + name + ': ' + \
                            description[0:120]  # first 120 characters as description
                        imageExist = True
                        if not images:
                            #image = '//SITENAME.fr/wp-content/uploads/2020/06/QUELLE-Taille-1-1.png'
                            imageExist = False
                        descriptions = description.replace('\n\n', '\n')
                        descriptions = description.split('\n')
                        # print(description)
                        # for i in range(0,len(descriptions)):
                        #	print(str(i) +'--->'+descriptions[i])

                        if len(descriptions) <= 4:
                            postContent = ('<h2 style="text-align: center; color: #47AEF3">La Taille de ' + name + '</h2>'
                                           '<div style="text-align: center"><a href="#"><img alt= "taille ' +
                                           name + '" src="http:'+image+'" ></a></div>'
                                           '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>Taille: ' +
                                           taille + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                           '<p>La taille de ' + name + ' est de ' + taille + '.</p>'
                                           '<h2>1. D\'où vient '+name+' ?</h2>'
                                           '<br>' + descriptions[0] +
                                           '<h2>2. Que peut-on savoir sur '+name + ' ?</h2>'
                                                    '<br>' + descriptions[2] +
                                                    '<h3>Mots-clé:</h3>'
                                                    '<br>' + 'taille de '+name + ', la taille de ' + name + ', ' + name + ' taille'
                                                    '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                    '<h3>Style de chanson:</h3>'
                                                    '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎤'
                                                    '<br>'
                                                    '<br> Trouvez la taille des autres artistes sur <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                    '</div>'
                                           )
                        elif len(descriptions) <= 6:
                            postContent = ('<h2 style="text-align: center; color: #47AEF3">La Taille de ' + name + '</h2>'
                                           '<div style="text-align: center"><a href="#"><img alt= "taille ' +
                                           name + '" src="http:'+image+'" ></a></div>'
                                           '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>Taille: ' +
                                           taille + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                           '<p>La taille de ' + name + ' est de ' + taille + '.</p>'
                                           '<h2>1. D\'où vient '+name+' ?</h2>'
                                           '<br>' + descriptions[0] +
                                           '<h2>2. Que peut-on savoir sur '+name + ' ?</h2>'
                                                    '<br>' + descriptions[2] +
                                                    '<h2>3. Quels sont les projets de '+name+' ?</h2>'
                                                    '<br>' + descriptions[4] +
                                                    '<h3>Mots-clé:</h3>'
                                                    '<br>' + 'taille de '+name + ', la taille de ' + name + ', ' + name + ' taille'
                                                    '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                    '<h3>Style de chanson:</h3>'
                                                    '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎤'
                                                    '<br>'
                                                    '<br> Trouvez la taille des autres artistes sur <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                    '</div>'
                                           )
                        else:
                            postContent = ('<h2 style="text-align: center; color: #47AEF3">La Taille de ' + name + '</h2>'
                                           '<div style="text-align: center"><a href="#"><img alt= "taille ' +
                                           name + '" src="http:'+image+'" ></a></div>'
                                           '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>Taille: ' +
                                           taille + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                           '<p>La taille de ' + name + ' est de ' + taille + '.</p>'
                                           '<h2>1. D\'où vient '+name+' ?</h2>'
                                           '<br>' + descriptions[0] +
                                           '<h2>2. Que peut-on savoir sur '+name + ' ?</h2>'
                                                    '<br>' + descriptions[2] +
                                                    '<h2>3. Quels sont les projets de '+name+' ?</h2>'
                                                    '<br>' + descriptions[4] +
                                                    '<h2>4. Des rencontres et collaborations de '+name+' ?</h2>'
                                                    '<br>' + descriptions[6] +
                                                    '<h3>Mots-clé:</h3>'
                                                    '<br>' + 'taille de '+name + ', la taille de ' + name + ', ' + name + ' taille'
                                                    '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                    '<h3>Style :</h3>'
                                                    '<br>' + ' 🎤' + '  🎤'
                                                    '<br>'
                                                    '<br> Trouvez la taille des autres artistes sur <a href="http://SITENAME.fr"> Quelle Taille </a>'
                                                    '</div>'
                                           )

                        featuredImageUrl = 'http:'+image  # Url of the featured image
                        # the /xmlrpc.php path. Basically the same for most wordpres site. It is the posting adsresscause for the XML Server
                        wpUrl = 'http://www.SITENAME.fr/xmlrpc.php'
                        postTags = [nationalite, 'Animation', 'Animateur',
                                    name, 'TV', 'Télé', '2020']  # tags of the post
                        # Categories of the post
                        postCategories = [nationalite, 'Animation',
                                          'Animateur', name, 'TV', 'Télé', '2020']

                        #########################################
                        # Create an object of the xml rpc server and upload the post
                        #########################################
                        myObject = uploader.My_WP_XMLRPC()
                        myObject.postArticle(wpUrl, wpLogin, wpPassword, postTitle, postCategories,
                                             postMetaDescription, postContent, postTags, featuredImageUrl, imageExist)

                    else:
                        # create HTML page

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

                        pageTitle = pageTitle.replace(' ', '-')
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
                    path = 'articles/'+pageTitle + '.html'
                    url = 'http://SITENAME.fr/'+path
                    personInfo['person'].append({
                        'name': name,
                        'image': image,
                        'description': description,
                        'url': url
                    })
                    with open('personInfo.json', 'w', encoding='utf-8') as f:
                        json.dump(personInfo, f, ensure_ascii=False, indent=4)
