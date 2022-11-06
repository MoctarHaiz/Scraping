import bs4
import requests
import json
import time
import dominate
from dominate.tags import *
import re
import uploader
import unidecode
import sys
import urllib.request

fromfile = False  # Indicate whether the json is obtained from personInfo.json or directly from the webpage results of wikipedia
# File that containes the already treated people
personInfoFile = "personInfoEnglish.json"
create = 'post'  # 'html' to create html page
print("\n\n\n")


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


paramsSet = False
if(len(sys.argv) < 2):
    print("Please the category to scrap")
elif (len(sys.argv) == 2):
    print(
        'The information is obtained directly from wikipedia: ' + sys.argv[1])
    wikipediaLink = "https://en.wikipedia.org/w/api.php?cmtitle=Category:" + \
        sys.argv[1]+"&action=query&format=json&prop=langlinks&list=categorymembers&titles=Colugo&lllang=fr&lllimit=100&cmlimit=max"
    paramsSet = True
elif (len(sys.argv) == 4):
    print(
        'The information is obtained directly from wikipedia: ' + sys.argv[1])
    startWith = sys.argv[2]
    endWith = sys.argv[3]
    print('The listing will start from ' +
          startWith + ' and will end with ' + endWith)
    wikipediaLink = "https://en.wikipedia.org/w/api.php?cmtitle=Category:" + \
        sys.argv[1]+"&action=query&format=json&prop=langlinks&list=categorymembers&titles=Colugo&lllang=fr&lllimit=100&cmlimit=max&cmsort=sortkey&cmdir=asc&cmstartsortkeyprefix=" + \
        startWith+"&cmendsortkeyprefix=" + endWith
    paramsSet = True
else:
    print(" Please Specify only 3 params:  Category StartWith EndWith")

if(paramsSet):
    # Open the aved json file that contains all the people already treated
    personInfo = {}
    personInfo['person'] = []
    with open(personInfoFile, 'r+', encoding='utf-8') as f:
        try:
            personInfo = json.load(f)
        except Exception as e:
            personInfo['person'] = []

    # For Checking existing names
    existingNames = json_extract(personInfo, 'name')

    # Open the json file that contains the person ids (this file is obtained from mediapedia api: list rappeurs français) and search the information on wikipedia
    with urllib.request.urlopen(wikipediaLink) as json_file:
        print("\n List of " + sys.argv[1] + " obtained")
        json_file = json_file.read().decode()
        data = json.loads(json_file)
        counter = 0
        for pers in data['query']['categorymembers']:
            counter = counter + 1
            # Check if the person is already in the lis or not, process only if he is not in the list
            if pers['title'] in existingNames:
                print("---> " + str(counter) + " - " +
                      str(pers['title']) + " already exists")
            else:
                url = "https://en.wikipedia.org/?curid="+str(pers['pageid'])
                response = requests.get(url)

                if response is not None:
                    html = bs4.BeautifulSoup(response.text, 'html.parser')
                    name = html.select("#firstHeading")[0].text
                    paragraphs = html.select("p")
                    # print from 1 to 3 paragraphs. 0 adds "modifier" in french wikipedia version
                    description = ""
                    for para in paragraphs[1:20]:
                        if len(para.text) > 10:  # if para has some text
                            # print(para.text)
                            description = str(description) + \
                                str(para.text) + '\n'

                    # replace some words to avoid plagiarism
                    # remove everything in bracket like [2]
                    description = re.sub("\[.\]", "", description)
                    # remove everything in bracket like [2]
                    description = re.sub("\[..\]", "", description)
                    # remove everything in bracket like [2]
                    description = re.sub("\[...\]", "", description)
                    description = description.replace("modifier", "")
                    description = description.replace(
                        "(born", "(he is born in")
                    description = description.replace("(He", pers['title'])
                    description = description.replace("film", "movie")
                    description = description.replace(
                        "called", "which name is")
                    description = description.replace("role", "act")
                    description = description.replace("tlevision", "tv")
                    description = description.replace(
                        "He is best known", "The large public knows " + pers['title'] + " ")
                    description = description.replace(
                        "He attended", "He went to")
                    description = description.replace(
                        "American actor", "actor from the United-States ( 🇺🇸 )")
                    description = description.replace(
                        "American character actor", "actor from the United-States ( 🇺🇸 )")
                    description = description.replace("debut", "start")
                    description = description.replace("starred", "acted")

                    # Print Info
                    pageTitle = 'Height ' + name
                    infobox_v3 = html.select('.infobox')
                    if len(infobox_v3) > 0:
                        infoBox = html.select('.infobox')[0]
                        images = infoBox.select('a.image img[src]')
                        heightTag = infoBox.select_one('th:contains("Height")')
                        nationaliteTag = infoBox.select_one(
                            'th:contains("Nationality")')
                        citizenshipTag = infoBox.select_one(
                            'th:contains("Citizenship")')
                        height = "...m"
                        nationalite = "..."
                        nationaliteLink = "#"
                        image = ""
                        print("Done " + str(counter) + " - " + name)
                        if not heightTag:
                            print(
                                "\t Height: No <------------------------------------------")
                        else:
                            height = heightTag.parent.select(
                                'td')[0].text.strip()
                            print("\t Height: " + height)
                        if not nationaliteTag:
                            print(
                                "\t Nationality: No <------------------------------------------")
                            if not citizenshipTag:
                                print(
                                    "\t citizenship: No <------------------------------------------")
                            else:
                                nationalite = citizenshipTag.parent.select('td')[
                                    0].text.strip()
                                print("\t Nationality: " + nationalite)
                                nationaliteLink = unidecode.unidecode(
                                    "http://SITENAME.fr/category/"+nationalite.replace('ç', 'c'))
                        else:
                            nationalite = nationaliteTag.parent.select('td')[
                                0].text.strip()
                            print("\t Nationality: " + nationalite)
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
                            postMetaDescription = 'Height ' + name + ': ' + \
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

                            if len(descriptions) <= 1:
                                postContent = ('<h2 style="text-align: center; color: #47AEF3">Height of ' + name + '</h2>'
                                               '<div style="text-align: center"><a href="#"><img alt= "height ' +
                                               name + '" src="http:'+image+'" ></a></div>'
                                               '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>height: ' +
                                               height + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                               '<p> The height of ' + name + ' is ' + height + '.</p>'
                                               '<h2>1. Where did '+name+' come from ?</h2>'
                                               '<br>' + descriptions[0] +
                                               '<h3>Keywords:</h3>'
                                                        '<br>' + 'Height of '+name + ', the Height of ' + name + ', ' + name + ' Height'
                                                        '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                        '<h3>Style : </h3>'
                                                        '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎬'
                                                        '<br>'
                                                        '<br> find the height of other celebrities on <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                        'Source 1 : <a href="https://www.wikipedia.org"> wikipedia</a>'
                                                        ' Source 2 : <a href= "https://www.imdb.com"> imdb</a>'
                                                        '</div>'
                                               )
                            elif len(descriptions) <= 4:
                                postContent = ('<h2 style="text-align: center; color: #47AEF3">Height of ' + name + '</h2>'
                                               '<div style="text-align: center"><a href="#"><img alt= "height ' +
                                               name + '" src="http:'+image+'" ></a></div>'
                                               '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>height: ' +
                                               height + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                               '<p> The height of ' + name + ' is ' + height + '.</p>'
                                               '<h2>1. Where did '+name+' come from ?</h2>'
                                               '<br>' + descriptions[0] +
                                               '<h2>2. What could we know about '+name + ' besides his height ?</h2>'
                                                        '<br>' + descriptions[2] +
                                                        '<h3>Keywords:</h3>'
                                                        '<br>' + 'Height of '+name + ', the Height of ' + name + ', ' + name + ' Height'
                                                        '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                        '<h3>Style : </h3>'
                                                        '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎬'
                                                        '<br>'
                                                        '<br> find the height of other celebrities on <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                        'Source 1 : <a href="https://www.wikipedia.org"> wikipedia</a>'
                                                        ' Source 2 : <a href= "https://www.imdb.com"> imdb</a>'
                                                        '</div>'
                                               )
                            elif len(descriptions) <= 6:
                                postContent = ('<h2 style="text-align: center; color: #47AEF3">Height of ' + name + '</h2>'
                                               '<div style="text-align: center"><a href="#"><img alt= "height ' +
                                               name + '" src="http:'+image+'" ></a></div>'
                                               '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>height: ' +
                                               height + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                               '<p> The height of ' + name + ' is ' + height + '.</p>'
                                               '<h2>1. Where did '+name+' come from ?</h2>'
                                               '<br>' + descriptions[0] +
                                               '<h2>2. What could we know about '+name + ' besides his height ?</h2>'
                                                        '<br>' + descriptions[2] +
                                                        '<h2>3. What are the projects of '+name+' ?</h2>'
                                                        '<br>' + descriptions[4] +
                                                        '<h3>Keywords:</h3>'
                                                        '<br>' + 'Height of '+name + ', the Height of ' + name + ', ' + name + ' Height'
                                                        '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                        '<h3>Style : </h3>'
                                                        '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎬'
                                                        '<br>'
                                                        '<br> find the height of other celebrities on <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                        'Source 1 : <a href= "https://www.wikipedia.org"> wikipedia</a>'
                                                        ' Source 2 : <a href= "https://www.imdb.com"> imdb</a>'
                                                        '</div>'
                                               )
                            else:
                                remainingText = ""
                                for item in range(6, len(descriptions), 2):
                                    remainingText += '<br> <br> <br>' + \
                                        descriptions[item]

                                postContent = ('<h2 style="text-align: center; color: #47AEF3">Height of ' + name + '</h2>'
                                               '<div style="text-align: center"><a href="#"><img alt= "height ' +
                                               name + '" src="http:'+image+'" ></a></div>'
                                               '<div style="text-align: center"><h3 style="text-align: center; color: #47AEF3;   font-size: 0.875em;"><b>height: ' +
                                               height + '</b></h3><a href="'+nationaliteLink+'">' + nationalite + '</a></div>'
                                               '<p> The height of ' + name + ' is ' + height + '.</p>'
                                               '<h2>1. Where did '+name+' come from ?</h2>'
                                               '<br>' + descriptions[0] +
                                               '<h2>2. What could we know about '+name + ' besides his height ?</h2>'
                                                        '<br>' + descriptions[2] +
                                                        '<h2>3. What are the projects of '+name+' ?</h2>'
                                                        '<br>' + descriptions[4] +
                                                        '<h2>4. Somme collaborations with '+name+' ?</h2>'
                                                        '<br>' + remainingText +
                                                        '<h3>Keywords:</h3>'
                                                        '<br>' + 'Height of '+name + ', the Height of ' + name + ', ' + name + ' Height'
                                                        '<div style="text-align: center; color: #47AEF3, font-size:7%">'
                                                        '<h3>Style : </h3>'
                                                        '<br>' + ' 🎙️' + '  🌍' + '  🎤' + '  🎵' + '  🎹' + '  🔴' + '  🎬'
                                                        '<br>'
                                                        'Source 1 : <a href= "https://www.wikipedia.org"> wikipedia</a>'
                                                        ' Source 2 : <a href= "https://www.imdb.com"> imdb</a>'
                                                        '<br> find the height of other celebrities on <a href="www.SITENAME.fr"> Quelle Taille </a>'
                                                        '</div>'
                                               )

                            featuredImageUrl = 'http:'+image  # Url of the featured image
                            # the /xmlrpc.php path. Basically the same for most wordpres site. It is the posting adsresscause for the XML Server
                            wpUrl = 'https://www.SITENAME.fr/xmlrpc.php'
                            postTags = [nationalite, name, 'TV',
                                        'height']  # tags of the post
                            # Categories of the post
                            postCategories = [
                                nationalite, name, 'TV', 'height']

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
                                meta(
                                    name="viewport", content="width=device-width, initial-scale=1")
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
                                        attr(cls='image', src='http:' +
                                             image, alt=name)
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
                                            attr(
                                                href="http://www.SITENAME.fr")
                                            with button():
                                                attr(cls='button button3')
                                                span('Back')

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
                        try:
                            path = 'articles/'+pageTitle + '.html'
                            url = 'http://SITENAME.fr/'+path
                            personInfo['person'].append({
                                'name': name,
                                'image': image,
                                'description': description,
                                'url': url
                            })
                            with open(personInfoFile, 'w', encoding='utf-8') as f:
                                json.dump(personInfo, f,
                                          ensure_ascii=False, indent=4)
                        except:
                            print("\n\n\a Unable to write in " + personInfoFile)

print("\n\n\a")
