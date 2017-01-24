
# coding: utf-8

# 
# ### summarize.py

#This should read the output of the previous methods to write a textfile called summary.txt containing the following entries:
#   - Number of users collected: // read 'users.txt', length
#   - Number of messages collected: // read 'num_tweets.txt', sum
#   - Number of communities discovered: // read 'clusters.txt' len
#   - Average number of users per community: // read 'clusters.txt' calc avg
#   - Number of instances per class found: // read 'class.txt' split by '\'
#   - One example from each class: // per class: <classname>\t<number>\t<example>\n
# 
# 
# 

# In[46]:

def read_file(filename):
    o = open(filename)
    f = o.read()
    files = f.split('\n')
    return list(filter(None, files))


# In[47]:

def get_users():
    users = read_file('users.txt')
    return (len(users))

def get_tweets():
    nums = read_file('num_tweets.txt')
    return sum(int(n) for n in nums)       

def get_class():
    result = []
    cls = read_file('class.txt')
#     print(cls[0].split('\t'))
    for c in cls:
#         print (c)
        result.append(c.split('\t'))
    return result


# In[48]:

def get_clusters():
    clus = read_file('clusters.txt')
    l = [int(c) for c in clus]
    num_clu = len(l)
    avg = sum(l) / len(l)
    return (num_clu, avg)


# In[54]:

def main():
    fw = open('summary.txt', 'w')
    users = get_users()  
    print('\nNumber of users collected: %d' % users, file = fw)
    tsum = get_tweets()
    print('\nNumber of messages collected: %d' % tsum, file = fw)
    num_clu, avg = get_clusters()
    print('\nNumber of communities discovered: %d' %num_clu, file = fw)
    print('\nAverage number of users per community: %d' % avg, file = fw)
    print ('\nNumber of instances per class found:', file = fw)
    cl = get_class()
    for c in cl:
        print('%s, %s'%(c[0],c[1]), file = fw)
        
    print('\nOne example from each class: \n',file = fw)
    for c in cl:
        print('%s:\n%s\n'%(c[1],c[2]), file = fw)   
    
    
if __name__ == '__main__':
    main()




