
# coding: utf-8

# ### collect.py
# 
# This should collect data used in your analysis. This may mean submitting queries to Twitter or Facebook API, or scraping webpages. The data should be raw and come directly from the original source -- that is, you may not use data that others have already collected and processed for you (e.g., you may not use SNAP datasets). Running this script should create a file or files containing the data that you need for the subsequent phases of analysis.
# 

# In[1]:


import sys
import time
from TwitterAPI import TwitterAPI, TwitterOAuth
from collections import defaultdict


def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    o = TwitterOAuth.read_file('credentials.txt')
    # Using OAuth1...
    twitter = TwitterAPI(o.consumer_key,
                 o.consumer_secret,
                 o.access_token_key,
                 o.access_token_secret)
    return twitter


# In[3]:

def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


# In[5]:

def get_tweets( max_len = 5000):
    
    twitter = get_twitter()
    tweets = []
    m_id = 0 if len(tweets) is 0 else tweets[len(tweets)-1]['id']
    while len(tweets)<max_len:
        rid = m_id
        m_id = 0 if len(tweets) is 0 else tweets[len(tweets)-1]['id']
        for r in robust_request(twitter,'search/tweets',{'q':  'nationalpark OR "national park" -filter:retweets',
                                                   'country': 'United States', 'lang': 'en',
                                                   'count':100, 'max_id': m_id}):

            if r['id'] == rid:
                return (tweets,len(tweets)) 
            tweets.append(r)
        if len(tweets)%100 == 0:
            print('read %d tweets' % len(tweets) )
    return (tweets,len(tweets))    
            


# In[6]:




# In[7]:

def write_tweets2file(tweets, write_type = 'a', filename='save_tweets.txt',):
    rawData = open(filename, write_type)
    for t in tweets:
        rawData.write(t['text'].replace('\n', ' ').lower()+'\n')
    print('write %d tweets to %s' % (len(tweets),filename))
    rawData.close()


# In[8]:


def get_data_from_file(filename = 'rawtweets.txt'):
    d = open(filename)
    f = d.readlines()
    return f


# In[9]:

def get_national_park_list():
    f = open("national_park_list.txt")
    lines = f.readlines()
    park_list = [l.rstrip('\r\n').lower() for l in lines]
    return park_list


# In[10]:

def get_multi_names(park_names):
    return [(n, ''.join(n.split()), n.replace(' ', '_')) if ' ' in n else (n,) for n in park_names ]


# In[11]:


def get_park_trend(park_list, datatable):
    parks = defaultdict(lambda: [])
    for n in park_list:
        for i,t in enumerate(datatable):
            if n in t.lower():
                parks[n].append(t.lower())
                datatable.remove(t)
    park_nums = defaultdict(lambda: 0)
    for n in park_list:
        park_nums[n]=len(parks[n])
        
    p_nums =sorted(park_nums.items(), key=lambda x: x[1],reverse=True)
    return (p_nums, parks)


def write_trends2file(p_nums,fileName='save_trends.txt'):
    with open('save_trends.txt', 'w') as fp:
        fp.write('\n'.join(r[0] for r in p_nums))


# In[16]:

def save_nums(fn, nums):
    rawData = open(fn, 'w')
    rawData.write('%d\n'%nums)
    print('write %d number to %s' % (nums,fn))
    rawData.close()


# In[13]:

def data2commu(tweets):
    userdata = defaultdict(lambda:0)
    for t in tweets:
        if t['user']['screen_name'] not in userdata:
            userdata[t['user']['screen_name']] = t['user']['friends_count']
    userdata = sorted(userdata.items(), key=lambda x: x[1],reverse=True)[:14]
    with open('users.txt', 'w') as fp:
        fp.write('\n'.join(u[0] for u in userdata))


# In[15]:


def main():
    tweets,num_tweets = get_tweets() 
    fn = 'rawdata.txt'
    data2commu(tweets)
    write_tweets2file(tweets,write_type = 'w',filename = fn)
    save_nums('num_tweets.txt', len(tweets))
    print('read %d tweets' % len(tweets) )
    print('the last 10 tweets are:\n')
    for t in tweets[-10:]:
        print(t['text']+'\n')

    #read data from file in case of Twitter API rate limit
    datatable = get_data_from_file(filename = fn)
    print('%s number of data got from %s'%(len(datatable),fn))
    park_list = get_national_park_list()
    print('Number of national parks: ', len(park_list))
    p_nums, parks = get_park_trend(park_list, datatable)
    write_trends2file(p_nums)
    print('The number of US. national parks mentioned in the passed 1 week:')
    for i, r in enumerate(p_nums):
        print (i+1, r)


if __name__ == '__main__':
    main()

