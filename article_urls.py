"""
Script for getting article urls from the New York Times API
"""

import requests



# Query for articles about affordable care act
base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json" \
           "?q=affordable+care+act&fq=news_desk%3A%28%22OpEd%22%29&fl=web_url%2Cnews_desk&" \
           "api-key=17a92e5aa402d751f17bff6ed5e9f0f1:19:49094860&page="
for i in xrange(1,20):
    r = requests.get("%s%d" % (base_url, i))
    data = r.json()
    for article in data["response"]["docs"]:
        print "%s\t%s" % (article["news_desk"],article["web_url"])


# Query for arcticles about Obamacare
base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?" \
           "q=obamacare&fq=news_desk%3A%28%22OpEd%22%29&fl=web_url%2Cnews_desk&" \
           "api-key=17a92e5aa402d751f17bff6ed5e9f0f1:19:49094860&page="
for i in xrange(1,20):
    r = requests.get("%s%d" % (base_url, i))
    data = r.json()
    for article in data["response"]["docs"]:
        print "%s\t%s" % (article["news_desk"],article["web_url"])

