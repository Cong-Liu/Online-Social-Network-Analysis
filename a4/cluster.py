
# coding: utf-8

# In[1]:

from collections import Counter, defaultdict, deque
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI, TwitterOAuth

# In[2]:

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


# In[4]:

def read_screen_names(filename):

    file = open(filename)
    name_list = file.read()
    screen_names = name_list.split('\n')
    return list(filter(None, screen_names))
    pass


# In[5]:

def get_users(twitter, screen_names):

    request = robust_request(twitter,'users/lookup',{'screen_name': screen_names})
    return request
    pass


def get_friends(twitter, screen_name):

    request = robust_request(twitter, 'friends/ids', {'screen_name':screen_name,'count': 5000})
    fid = []
    for r in request:
        fid.extend([r])
    return sorted(fid)
    pass



def add_all_friends(twitter, users):

    for u in users:
        u['friends'] = get_friends(twitter, u['screen_name'])
    pass


def print_num_friends(users):

    sorted(users, key=lambda x: x['screen_name'])
    for u in users:
        print('%s %d'%(u['screen_name'],len(u['friends'])))
    pass


def count_friends(users):

    c = Counter()
    for u in users:
       c.update(u['friends'])
    return c
    pass


def friend_overlap(users):

    list = []
    user_list = len(users)
    for i in range(user_list):
        for j in range(i+1, user_list):
            # temp_list = []
            temp_list = users[i]['friends']+(users[j]['friends'])
            common = Counter(temp_list).most_common()
            num = sum([int(i[1])>1 for i in common])
            list.append((users[i]['screen_name'], users[j]['screen_name'],num))
    return sorted(list,key=lambda x: -x[2])

def create_graph(users, friend_counts):

    graph = nx.Graph()
    for u in users:
        u_name = u['screen_name']
        u_friends = u['friends']
        graph.add_node(u_name)
        for f_id in u_friends:
            if friend_counts[f_id]>1:
                graph.add_edge(u_name,f_id)
    return graph
    pass

def draw_network(graph, users, filename):

    screen_name =[u['screen_name'] for u in users]
    labels = {n:n if n in screen_name else '' for n in graph.nodes()}
    plt.figure(figsize=(16,16))
    nx.draw_networkx(graph, labels=labels, node_size=100,alfa =0.5, width = 0.1)
    plt.axis("off")
    plt.savefig(filename)
    plt.show()
    pass


def get_subgraph(graph, min_degree):

    nodes = [n for n in graph.nodes() if graph.degree(n) >= min_degree]

    subgraph = graph.subgraph(nodes)
    return subgraph


def girvan_newman(graph, minsize=30, maxsize=200):

    if graph.order() == 1:
        return [graph.nodes()]
    G = graph.copy()
    btn = nx.edge_betweenness_centrality(G)
    sbtn = sorted(btn.items(), key=lambda x: x[1], reverse=True)

    components = [c for c in nx.connected_component_subgraphs(G)]
    
    i = 0
    while len(components) == 1:
        G.remove_edge(*sbtn[0][0])
        i+=1
        del sbtn[0]
        components = [c for c in nx.connected_component_subgraphs(G)]

    gs = []
    for c in components:
        if len(c) >= minsize and len(c) <= maxsize:
            gs.append(c)
            print ('stoping for size of a component %s' % len(c))
        elif len(c) > maxsize:
            gs.extend(girvan_newman(c))

    return gs



# In[19]:

def get_cluster_size(result):
    clus = [len(x) for x in result]
    with open('clusters.txt', 'w') as fp:
        for x in result:
            print(len(x), file= fp)
    return clus


# In[10]:

def draw_subgraphs(graph,users, result):
    i=0
    for cluster in result:
        fn = '%d_subnetwork.png'%i
        draw_network(graph.subgraph(cluster),users,fn)
        i+=1


def main():
 
    twitter = get_twitter()
    screen_names = read_screen_names('users.txt')
    print('Read screen names: %s' % screen_names)
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')
    result = girvan_newman(graph, minsize=30, maxsize=100)
    print('final cluster sizes:')
    print(get_cluster_size(result))
    draw_subgraphs(graph, users, result)

if __name__ == '__main__':
    main()

