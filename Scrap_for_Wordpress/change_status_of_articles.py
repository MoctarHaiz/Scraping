########################### Read Me First ###############################
# This Code updated the status of all posts that have 
# low pageviews. 
# The robot code to google analytics to select the posts
# that have many views & keep only those posts are published.
# The other ones are unpublished.
# To cope with serve side efficiency, the posts of the website 
# are retrieved by post_batch_size

# https://gist.github.com/345161974/63573abdf1dc9c303d6740fb29496657
import urllib.request  # python 2 urllib
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
import xmlrpc  # python 2 xmlrpclib
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import os
import time 
from GoogleAnalyticsReport import GoogleAnalyticsReport


def get_artice_and_pageviews_from_googgle_analytics(number_articles_to_keep):
    analytics = GoogleAnalyticsReport()
    VIEW_ID = '227412376'
    metrics = ['ga:pageviews']
    dimensions = ['ga:pagePath', 'ga:pageTitle']
    start_date, end_date = '2021-01-01', '2023-01-30'
    response = analytics.get_report(VIEW_ID, start_date, end_date, metrics, dimensions)
    df = analytics.to_dataframe(response)
    df['ga:pageviews'] = df['ga:pageviews'].astype(int)
    df = df.sort_values(by='ga:pageviews', ascending=False)
    df = df.head(number_articles_to_keep)
    return df

def unpublish_all_other_articles(data):
    wpUrl = 'https://quelletaille.fr/xmlrpc.php'
    wpLogin = 'quelletaille2020'
    wpPassword = 'Issaka427&'
    offset = 0
    post_batch_size = 100
    number_published_articles = 0
    client = Client(wpUrl, wpLogin, wpPassword)
    while True:
        print("--> Batch: [" + str(offset)+","+str(offset+post_batch_size)+"]")
        posts_ = client.call(posts.GetPosts( {'offset': offset, 'number': post_batch_size}))
        print("-> Comparing with " + str(len(posts_)) + " articles obtained from the website")
        if len(posts_) == 0:
            break
        offset += post_batch_size 
        # Get the posts in the website    
        for post in posts_:
            if post.post_status == 'publish':
                #print(post.title + " - " + post.post_status + " - " + post.link)
                #post.post_status = 'draft'
                #client.call(posts.EditPost(post.id, post))
                #print(post.title + " - " + post.post_status)

                # Loop through the google analytics pageviews data
                sufficent_page_views = False
                for index, row in data.iterrows():
                    page_link = "https://quelletaille.fr"+row.tolist()[0]
                    page_title = row.tolist()[1]
                    page_views = row.tolist()[2]
                    post_link_temp = post.link
                    
                    if page_link[-1] == "/":
                        page_link = page_link[:-1]
                    if post_link_temp[-1] == "/":
                        post_link_temp =post_link_temp[:-1]
                    
                    if page_link == post_link_temp:
                        sufficent_page_views = True
                        number_published_articles = number_published_articles+1
                        print(page_link + " " + post.title + "\t\t\t\t" + page_title)# + "\t\t\t\t"+str(row.tolist()[2]))

                if not sufficent_page_views:
                    print("Not sufficent_page_views --------------------------------------------------------------------------------------------------------------------> " + post_link_temp + " ---------------- " + post.title + "\t\t\t\t")
                    #post.post_status = 'draft'
                    time.sleep(5)
                    #try:
                       #client.call(posts.EditPost(post.id, post))
                    #except:
                        #print("******")
                        #post.thumbnail = post.thumbnail['attachment_id']
                        #client.call(posts.EditPost(post.id, post))
                    client.call(posts.DeletePost(post.id))

    print("________________________________________________________________* number_published_articles " + str(number_published_articles) + "*________________________________________________________________")


if __name__ == "__main__":
    number_articles_to_keep=1400
    data = get_artice_and_pageviews_from_googgle_analytics(number_articles_to_keep)
    #print(data.to_string())
    unpublish_all_other_articles(data)
