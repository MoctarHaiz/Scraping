# https://gist.github.com/345161974/63573abdf1dc9c303d6740fb29496657
import urllib.request  # python 2 urllib
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
import xmlrpc  # python 2 xmlrpclib
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import os
########################### Read Me First ###############################
'''
------------------------------------------In DETAIL--------------------------------
Description
===========
Add new posts to WordPress remotely using Python using XMLRPC library provided by the WordPress.

Installation Requirement
************************
Verify you meet the following requirements
==========================================
Install Python 2.7 (Don't download 3+, as most libraries dont yet support version 3). 
Install from PyPI using easy_install python-wordpress-xmlrpc 
Easy_Install Link: https://pypi.python.org/pypi/setuptools
==========================================

Windows Installation Guide
==========================
-Download and Install Easy_Install from above Link -Extract Downloaded File and from CMD go to the extracted directory and run 'python setup.py install'. This will install easy_install. -Go to %/python27/script and run following command easy_install python-wordpress-xmlrpc

Ubuntu Installation Guide
=========================
sudo apt-get install python-setuptools 
sudo easy_install python-wordpress-xmlrpc

Note: Script has its dummy data to work initially which you can change or integrate with your code easily for making it more dynamic.

****************************************
For Bugs/Suggestions
contact@waqasjamal.com
****************************************
------------------------------------------In DETAIL--------------------------------		
'''


class My_WP_XMLRPC:
    def postArticle(self, wpUrl, wpLogin, wpPassword, postTitle, postCategories, postMetaDescription, postContent, postTags, featuredImageUrl, imageExist):
        # Copy the parameters values
        self.featuredImageUrl = featuredImageUrl
        self.wpUrl = wpUrl
        self.wpLogin = wpLogin
        self.wpPassword = wpPassword

        # Open connexion
        client = Client(self.wpUrl, self.wpPassword, self.wpPassword)

        if imageExist == True:
            try:
                # Save the image with this name
                self.path = os.getcwd()+"\\00000001.jpg"
                f = open(self.path, 'wb')
                # python 2 f.write(urllib.urlopen(self.articlePhotoUrl).read())
                f.write(urllib.request.urlopen(self.featuredImageUrl).read())
                f.close()

                filename = self.path
                # prepare the metadata and set the approprite name
                data = {'name': 'picture.jpg', 'type': 'image/jpg', }

                # read the binary file and let the XMLRPC library encode it into base64
                with open(filename, 'rb') as img:
                    data['bits'] = xmlrpc_client.Binary(img.read())
                response = client.call(media.UploadFile(data))
                attachment_id = response['id']
            except:
                attachment_id = 7
                print("Image decode Error")
        else:
            attachment_id = 7

        # Post (the article)
        post = WordPressPost()
        post.title = postTitle
        post.custom_fields = []  # Metadata if using Yoast SEO plugin
        post.custom_fields.append({
            'key': '_yoast_wpseo_focuskw',
            'value': postTitle
        })
        post.custom_fields.append({
            'key': '_yoast_wpseo_metadesc',
            'value': postMetaDescription
        })
        post.content = postContent
        post.terms_names = {'post_tag': postTags, 'category': postCategories}
        post.post_status = 'publish'  # publish draft
        post.thumbnail = attachment_id
        post.id = client.call(posts.NewPost(post))
        print('---->Post Uploaded: ' + postTitle + '\t Id: ' + post.id)


'''
#########################################
# Add the Wordpress login details
#########################################
#WordPress Username
wpLogin='***'
#WordPress Password
wpPassword='***'


#########################################
# The post (article) Details
#########################################


postTitle='Testing Python Script version 3' #Post Title
postContent='Final .... Testing Fully Automated' #post content
featuredImageUrl='http://SITENAME.fr/wp-content/uploads/elementor/thumbs/801x410_801x410_niska_du_lundi_au_lundi-or4hdnp1yzoheh5on9dylnea3tmx979tyekiry46vk.jpg' #Url of the featured image
wpUrl='http://www.SITENAME.fr/xmlrpc.php' # the /xmlrpc.php path. Basically the same for most wordpres site. It is the posting adsresscause for the XML Server
postTags=['code','python'] #tags of the post
postCategories=['language','art'] #Categories of the post
postMetaDescription =' '
#########################################
# Create an object of the xml rpc server and upload the post
#########################################
myObject	=	My_WP_XMLRPC()
myObject.postArticle(wpUrl,wpLogin,wpPassword,postTitle, postCategories, postMetaDescription, postContent, postTags,featuredImageUrl)
'''
