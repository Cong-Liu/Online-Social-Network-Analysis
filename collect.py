
# coding: utf-8

# ### collect.py
# 
# This should collect data used in your analysis. This may mean submitting queries to Twitter or Facebook API, or scraping webpages. The data should be raw and come directly from the original source -- that is, you may not use data that others have already collected and processed for you (e.g., you may not use SNAP datasets). Running this script should create a file or files containing the data that you need for the subsequent phases of analysis.

# In[415]:

from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRestPager
import pandas as pd
import numpy as np
from collections import defaultdict


# In[417]:

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


# In[468]:

def get_tweets( max_len = 5000):
    
    twitter = get_twitter()
    tweets = []
    m_id = 0 if len(tweets) is 0 else tweets[len(tweets)-1]['id']
    while len(tweets)<max_len:
        rid = m_id
        m_id = 0 if len(tweets) is 0 else tweets[len(tweets)-1]['id']
        for r in twitter.request('search/tweets', {'q':  'nationalpark OR "national park" -filter:retweets', 
                                                   'country': 'United States', 'lang': 'en',
                                                   'count':100, 'max_id': m_id}):

            if r['id'] == rid:
                return (tweets,len(tweets)) 
            tweets.append(r)
        if len(tweets)%100 == 0:
            print('read %d tweets' % len(tweets) )
    return (tweets,len(tweets))    
            


# In[480]:

def write_tweets2file(tweets, write_type = 'a', filename='save_tweets.txt',):
    rawData = open(filename, write_type)
    for t in tweets:
        rawData.write(t['text'].replace('\n', ' ').lower()+'\n')
    print('write %d tweets to %s' % (len(tweets),filename))
    rawData.close()
# write_tweets2file(tweets,write_type = 'w',filename = 'save_tweets.txt')


# In[439]:

# get data from file
def get_data_from_file(filename = 'rawtweets.txt'):
#     rawdata = pd.read_csv(filename, sep,names=['tweets'])
#     print('len of raw data is' ,len(rawdata))
#     return rawdata
    d = open(filename)
    f = d.readlines()
    return f

# datatable = get_data_from_file(filename = 'rawdata.txt')
# for t in datatable[-3:]:
#     print (t)
# len(datatable)


# In[427]:

def get_national_park_list():
    f = open("national_park_list.txt")
    lines = f.readlines()
    park_list = [l.rstrip('\r\n').lower() for l in lines]
    return park_list

# park_list = get_national_park_list()
# print('Number of national parks: ', len(park_list))
# park_list


# In[428]:

def get_multi_names(park_names):
    return [(n, ''.join(n.split()), n.replace(' ', '_')) if ' ' in n else (n,) for n in park_names ]

# park_multi_names = get_multi_names(park_list)
# for n in zip(park_list, park_multi_names):
#     print (n[0], '\n\t', ' | '.join(n[1][i] for i in range(len(n[1]))), '\n')


# In[486]:

# datatable = get_data_from_file(filename = 'rawtweets.txt')
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

# p_nums, parks = get_park_trend(park_list, datatable)
# for i, r in enumerate(p_nums):
#     print (i+1, r)

def write_trends2file(fileName='save_trends.txt'):
    with open('save_trends.txt', 'w') as fp:
#         fp.write('\n'.join('%s %s' % r for r in result))
        fp.write('\n'.join(r[0] for r in result))
# write_trends2file()

# datatable = get_data_from_file(filename = 'rawtweets.txt')
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

def save_nums(fn, nums, des):
    rawData = open(fn, 'a')
    rawData.write(nums + ' ' + des + '\n')
    print('write %d to %s' % (nums,fn))
    rawData.close()

# In[487]:

def main():
    twitter = get_twitter()
    fn = 'rawdata.txt'
    tweets,num_tweets = get_tweets() 
    write_tweets2file(tweets,write_type = 'w',filename = fn)
    save_nums('save_nums.txt', len(tweets),'tweets for collect')
    print('read %d tweets' % num_tweets )
    print('the last 10 tweets are:\n')
    for t in tweets[-10:]:
        print(t['text']+'\n')


if __name__ == '__main__':
    main()


# In[ ]:



