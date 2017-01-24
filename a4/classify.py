import sys
import time
from TwitterAPI import TwitterAPI, TwitterOAuth
from collections import defaultdict
import collect as cl
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen


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


# In[8]:

# Download the AFINN lexicon, unzip, and read the latest word list in AFINN-111.txt

def get_afinn():
    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')

    afinn = dict()

    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])

    print('read %d AFINN terms.\nE.g.: %s' % (len(afinn), str(list(afinn.items())[:10])))
    return afinn


# In[52]:

# afinn = get_afinn()
def afinn_sentiment(terms, afinn):
    total = 0.
    for t in terms:
        if t in afinn:
            #             print('\t%s=%d' % (t, afinn[t]))
            total += afinn[t]
    return total


# doc = "i don't know if this is a scam or if mine was broken".split()
# print('AFINN: ', afinn_sentiment(doc, afinn))

def robust_request(twitter, resource, params, max_tries=5):
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


# In[98]:

# fn = 'save_trends.txt'
def get_park_list(filename, top=20):
    f = open(filename)
    da = f.readlines()
    data = [l.strip('\n') for l in da]
    return data[:top]


def get_data(park_list):
    datatable = cl.get_data_from_file(filename='rawdata.txt')
    p_nums, parks = cl.get_park_trend(park_list, datatable)
    return p_nums, parks


def get_list(p_nums):
    park_list = []
    for i, r in enumerate(p_nums):
        park_list.append(r[0])
    return park_list


# p_nums, parks = get_data()
# park_list = get_list(p_nums)


# In[132]:

def get_tweets_helper(name, max_len=200):
    twitter = get_twitter()
    tweets = []
    m_id = 0 if len(tweets) is 0 else tweets[len(tweets) - 1]['id']
    quary = name + ' national park OR "' + name + 'nationalpark"-filter:retweets'

    while len(tweets) < max_len:
        rid = m_id
        m_id = 0 if len(tweets) is 0 else tweets[len(tweets) - 1]['id']
        for r in robust_request(twitter, 'search/tweets', {'q': quary, 'country': 'United States', 'lang': 'en',
                                                           'count': 100, 'max_id': m_id}):
            #         for r in twitter.request('search/tweets', {'q':  quary, 'country': 'United States', 'lang': 'en',
            #                                                    'count':100, 'max_id': m_id}):

            if r['id'] == rid:
                print('Read %d tweets for %s' % (len(tweets), name))
                return tweets
            tweets.append(r)

    print('Read %d tweets for %s' % (len(tweets), name))
    return tweets


# In[133]:

def get_tweets(park_list):
    park_tweets = defaultdict()
    num_tweets = 0
    fw = open('class.txt', 'a')
    for name in park_list:
        t = get_tweets_helper(name)
        park_tweets[name] = t
        num_tweets += len(t)
        fw.write('\n%d\t%s\t' % (len(t), name))
        print(t[0], file=fw)

    return (park_tweets, num_tweets)


# In[121]:

def get_score_from_new_tweets(afinn, park_list, park_tweets):
    park_afinn = defaultdict(lambda: 0)
    for n in park_list:
        tweets = park_tweets[n]
        if len(tweets) is not 0:
            score = 0
            for t in tweets:
                score += afinn_sentiment(t['text'].split(), afinn)
            park_afinn[n] = score / len(tweets)
    return sorted(park_afinn.items(), key=lambda x: x[1], reverse=True)


# In[104]:

def get_score(afinn, park_list, parks):
    park_afinn = defaultdict(lambda: 0)
    for n in park_list[:20]:
        tweets = parks[n]
        if len(tweets) is not 0:
            score = 0
            for t in tweets:
                score += afinn_sentiment(t.split(), afinn)
            park_afinn[n] = score / len(tweets)
    return sorted(park_afinn.items(), key=lambda x: x[1], reverse=True)


def save_nums(fn, nums):
    rawData = open(fn, 'a')
    rawData.write('%d\n' % nums)
    print('write %d to %s' % (nums, fn))
    rawData.close()


# In[122]:

def main():
    print('Read AFINN file:')
    afinn = get_afinn()
    park_list = get_park_list('save_trends.txt', 20)

    print('Top 2 most popular national parks are: ')
    print(park_list)

    # model 1 using tweets collected from collect.py
    print('\nModel 1: Using data collected before:')
    p_nums, parks = get_data(park_list)
    result = get_score(afinn, park_list, parks)
    print('The top 10 recommended national parks are:\n')
    for r in result[:10]:
        print(' score:%f, %s national park' % (r[1], r[0]))

    # model 2 using new tweets collected according to top 20 parks' names
    print('\nModel 2: Using new tweets collected from Twitter:')
    park_tweets, num_tweets = get_tweets(park_list)
    print('Get %d tweets using park name as key word:' % num_tweets)
    save_nums('num_tweets.txt', num_tweets)
    result2 = get_score_from_new_tweets(afinn, park_list, park_tweets)
    print('The top 10 recommended national parks are:\n')
    for r in result2:
        print(' score:%f, %s national park' % (r[1], r[0]))


if __name__ == '__main__':
    main()