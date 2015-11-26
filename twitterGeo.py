import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sys
import argparse

import json
import urllib2
from httplib import BadStatusLine
from lxml.html import parse


#arguments
dirName = str(sys.argv[2]) #data path
numTweets = int(sys.argv[1]) #num of tweets 

#twitter credentials
access_token = "2585435621-zr2ojDoppuuDFnzN8UhFtKVgcNlCfMWyzyzfa5y"
access_token_secret = "fh8B8I82kNo0bPg4flmD8uMAMNw6Ec4bK2ecQT4Aemlzv"
consumer_key = "8IuNWIYCRXVOgQubHjNv79Xrz"
consumer_secret = "TKr8paciYE1BhcVCiap0hPtwPo0z4tiQc8TUw850ylFjeRDWQv"

tweetcnt = 0
filecnt = 0
outputPath = dirName
outputPath += '/'
outputPath += 'twitter_data'
outputPath += str(filecnt)
outputPath += '.txt'
f = open(outputPath, 'a')
chkFlag = True


#twitter listener
class twitterListener(StreamListener):
    
    def on_data(self, data):
        global f
        global filecnt
        global tweetcnt
        global chkFlag

        #checks num of tweet parameter
        if tweetcnt >= numTweets and numTweets != 0:
            print "first"
            chkFlag = False
            return False

        #Ends when files reach 5GB in total size
        if (filecnt >= 500):
            print "filecnt"
            chkFlag = False
            return False

        #Create a new text file every 10MB
        if (f.tell() >= 10485760):
            print "last"
            f.close()
            chkFlag= True
            filecnt += 1
            outputPath = dirName
            outputPath += '/'
            outputPath += 'twitter_data'
            outputPath += str(filecnt)
            outputPath += '.txt'
            f = open(outputPath, 'a')

        
        decoded = json.loads(data)  

        #Checks geo enable and if there is coordinates
        if unicode(decoded['user']['geo_enabled']).encode("ascii","ignore") == "True" and unicode(decoded['coordinates']).encode("ascii","ignore") != "None":

            username = unicode(decoded['user']['screen_name']).encode("ascii","ignore")  #gets username
            userTweet = unicode(decoded['text']).encode("ascii","ignore") #gets tweet
            userTweetTime = unicode(decoded['created_at']) #gets timestamp
            userLocation = unicode(decoded['user']['location']).encode("ascii","ignore") #gets location as per profile, not of the specific tweet
            userCoords = unicode(decoded['coordinates']).encode("ascii","ignore") #gets coordinates, will be 'None' if they have disable location services
            userURLS = unicode(decoded['entities']['urls']).encode("ascii","ignore")#get URLS 
            userData = "Date:" + userTweetTime +  " Coords:" + userCoords[36:-1] + " User:" + username + " Text:" + userTweet  

            #Loops through the list of hashtags and adds them to userData
            userHashtags = decoded['entities']['hashtags']
            if (userHashtags != "[]"):
                userData += " Hashtags:"
                tmp = decoded['text']
                for Hashtags in userHashtags:
                    userHashtags = unicode(Hashtags['text']).encode("ascii","ignore")
                    userData += userHashtags + " "
            
            #url
            if userURLS != "[]":
                expanded_url = unicode(decoded['entities']['urls'][0]['expanded_url']).encode("ascii","ignore")
                userData += " URL:"
                userData += expanded_url
                pageTitle = None

                try:
                    page = urllib2.urlopen(expanded_url)
                    p = parse(page)
                    
                    #pageTitle = unicode(p.find(".//title").text).encode("utf-8")
                    pageT = p.find(".//title")
                    if (pageT != None):
                        pageTitle = unicode(p.find(".//title").text).encode("ascii","ignore")
                    if (pageTitle != None):
                        userData += " Title:"
                        userData += pageTitle
                except urllib2.HTTPError, err:
                    if err.code == 404:
                        print "Page not found!"
                    elif err.code == 403:
                        print "Access denied!"
                    else:
                        print "Error:", err.code
                except urllib2.URLError, err:
                    print "URL error:", err.reason
                except BadStatusLine:
                    print "Could not fetch URL"
        
            tweetcnt += 1
            print 'Tweet:', tweetcnt, ' F.size = ', f.tell(), ' on file:', filecnt 
            userData += "\n"
            print userData
            f.write(userData)

        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    while chkFlag != False:
        try:
            #Authentication and connection to twitter API
            l = twitterListener()
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            stream = Stream(auth, l)

            #stream.filter(locations=[-121.32,32.64,-113.76,36.09], languages=["en"]) #filter tweets to be in the Southern Califnornia area
            stream.filter(locations=[-123.40,35.59,-66.79,48.25], languages=["en"]) 
        except Exception:
            pass
    f.close()
