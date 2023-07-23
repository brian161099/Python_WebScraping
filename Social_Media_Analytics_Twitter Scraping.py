# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 18:25:45 2022

@author: User
"""
import tweepy
import pandas as pd
import requests
import time
import os

# username -> ID
def FindID(username):
    # checkpoint
    # client, turn, iterations = CheckRateLimit(client, turn, iterations, "user", "N/A")
    user = client.get_user(username=username)
    user_dict = user.json()
    return user_dict["data"]["id"]

# 避免超出request限制，因此達特定次數會交換client
# df_retweet (search): 450次/15分鐘
# df_retweet (retweet): 75次/15分鐘
# df_likes: 75次/15分鐘
# df_follower: 15次/15分鐘

df_client = pd.read_excel("Twitter API Client keys.xlsx")

def CheckRateLimit(client, turn, iterations, action, progress):
    iterations[action] += 1
    if iterations["search"] > 449 or iterations["retweet"] > 74 or iterations["like"] > 74 or iterations["follower"] > 14 or iterations["user"] > 899:
        print("Client changed to: " + df_client.loc[turn, "User"])
        turn += 1
        iterations = {"search": 0,"retweet": 0, "like": 0, "follower": 0, "user":0}
        if turn == len(df_client.index):
            turn = 0
        consumer_key = df_client.loc[turn, "API Key"]
        consumer_secret = df_client.loc[turn, "API Key secret"]
        bearer_token = df_client.loc[turn, "Bearer token"]
        access_token = df_client.loc[turn, "Access token"]
        access_token_secret = df_client.loc[turn, "Access token secret"]
        print("Sleep for 3 seconds... " + action + " progress: "+ progress)
        time.sleep(3)
        client = tweepy.Client( bearer_token=bearer_token, 
                        consumer_key=consumer_key, 
                        consumer_secret=consumer_secret, 
                        access_token=access_token, 
                        access_token_secret=access_token_secret, 
                        return_type = requests.Response,
                        wait_on_rate_limit=True)
            
    return client, turn, iterations              
        
# 為CheckRateLimit設置基本參數 (Initial Client: 宗霖)

consumer_key = "Ap7vCI7SI6LbyKCulE2llc0W1"
consumer_secret = "2KFxYIHnptKH6joGnZOv3l9kuiRchLZUk7EqCn6V5gbL9PEPDO"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEXGbAEAAAAAB7Ec9uM5SR8R13FHJwLfdFCxOlE%3D931GBmUHhPZFhEygnh8WkmK7wltleAn8VB8AQnSDXF1pI7UQsr"
access_token = "4463037914-2Rxmc3ZDseYIUyR3E67LG4JMnNSZle9chlEimUI"
access_token_secret = "8jQkYBrB05L10DrKfgyOAjf3Q4FFi5cwAV7nrl44f7jNd"

turn = 0
iterations = {"search": 0,"retweet": 0, "like": 0, "follower": 0, "user":0}
client = tweepy.Client( bearer_token=bearer_token, 
                        consumer_key=consumer_key, 
                        consumer_secret=consumer_secret, 
                        access_token=access_token, 
                        access_token_secret=access_token_secret, 
                        return_type = requests.Response,
                        wait_on_rate_limit=True)



    
# In[] 
df_tweet = pd.read_excel(".\\tweets_drug_legalization.xlsx")
topics_list = list(set(df_tweet["topic"]))
tweets_dict = {}
for topic in topics_list:
    tweets_dict[topic] = pd.DataFrame(df_tweet[df_tweet["topic"] == topic])

# q="death penalty"

for q in topics_list:
    # Step 0: 創立新資料夾給每個主題
    newpath = ".//%s"%(q)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    # Step 1: 抓所選Tweet的Retweeters
    df_retweeters = pd.DataFrame()
    tweet_count = 0
    for tweet_id in tweets_dict[q]["tweet id"]:
        # checkpoint
        client, turn, iterations = CheckRateLimit(client, turn, iterations, "retweet", "%d/%d"%(tweet_count, len(tweets_dict[q].index)))
        retweet = client.get_retweeters(tweet_id)
        retweet_dict = retweet.json()
        if list(retweet_dict.keys())[0] != "errors":
            retweet_data = retweet_dict['data']  
            df5 = pd.json_normalize(retweet_data)
            while retweet_dict['meta']['result_count'] > 0:
                retweet_next_token = retweet_dict['meta']['next_token']
                # checkpoint
                client, turn, iterations = CheckRateLimit(client, turn, iterations, "retweet", "%d/%d"%(tweet_count, len(tweets_dict[q].index)))
                next_retweet = client.get_retweeters(tweet_id, pagination_token = retweet_next_token)
                retweet_dict = next_retweet.json()
                if retweet_dict['meta']['result_count'] > 0:
                    next_retweet_data = retweet_dict['data']  
                    next_df5 = pd.json_normalize(next_retweet_data)
                    df5 = pd.concat([df5, next_df5], axis=0, sort=False, ignore_index=True)
        df5["followee"] = tweets_dict[q].at[tweet_count,"username"]
        df5["bias"] = tweets_dict[q].at[tweet_count,"bias"]
        df5["topic"] = q
        df_retweeters = pd.concat([df_retweeters, df5], axis=0, sort=False, ignore_index=True)
        tweet_count += 1
    
    df_retweeters.to_excel(".//%s//df_retweeters_%s.xlsx"%(q, q))
    
    # Step 2: Check metrics of retweeters
    # df_retweeters = pd.read_excel(".\\%s\\df_retweeters_%s.xlsx"%(q,q))
    df_retweeters_metrics = pd.DataFrame()
    df1 = pd.DataFrame()
    retweeters_list = list(set(df_retweeters["username"]))
    string_list = []
    
    
    for count in range(round(len(retweeters_list)/100)):
        starting_point = 0 + count*100
        lower_bound = 1 + count*100
        upper_bound = min(99 + count*100, len(retweeters_list)-1)
        list_100 = retweeters_list[lower_bound:upper_bound]
        string = retweeters_list[starting_point]
        for next_string in list_100:
            string = string + "," + next_string
        string_list.append(string)
    
    
    for string in string_list:
        # checkpoint
        client, turn, iterations= CheckRateLimit(client, turn, iterations, "user", "N/A")
        user = client.get_users(usernames = string, user_fields=["public_metrics", "description"])
        user_dict = user.json()
        if list(user_dict.keys())[0] != "errors":
            df1_username = []
            df1_id = []
            df1_followers_count = []
            df1_following_count = []
            df1_listed_count = []
            df1_tweet_count = []
            df1_bio = []
            for j in range(len(user_dict["data"])):
                df1_username.append(user_dict["data"][j]["name"])
                df1_id.append(user_dict["data"][j]["id"])
                df1_followers_count.append(user_dict["data"][j]["public_metrics"]["followers_count"])
                df1_following_count.append(user_dict["data"][j]["public_metrics"]["following_count"])
                df1_listed_count.append(user_dict["data"][j]["public_metrics"]["listed_count"])
                df1_tweet_count.append(user_dict["data"][j]["public_metrics"]["tweet_count"])
                df1_bio.append(user_dict["data"][j]["description"])
            df_list = [df1_username,df1_id,df1_followers_count,df1_following_count,df1_listed_count,df1_tweet_count, df1_bio]
            df_list = list(map(list, zip(*df_list)))
            df1 = pd.DataFrame(df_list, columns=["Username", "ID", "Followers count", "Following count", "Listed count", "Tweet count", "Bio"]) 
        df_retweeters_metrics = pd.concat([df_retweeters_metrics, df1], axis=0, sort=False, ignore_index=True)
                
    # 篩掉F+F低於2000的Retweeters
    count1 = len(df_retweeters_metrics)
    print("Number of retweeters: " + str(count1))
    df_retweeters_metrics = df_retweeters_metrics[df_retweeters_metrics["Followers count"] + df_retweeters_metrics["Following count"] >= 2000]
    
    count2 = len(df_retweeters_metrics)
    
    print("Number of retweeters that have F+F greater than 2000: " + str(count2))
    print("(%d retweeters are removed.)"%(count1 - count2))

    df_not_endorsement = df_retweeters_metrics[df_retweeters_metrics["Bio"].str.contains("endorsement|Endorsement")]
    df_retweeters_metrics = df_retweeters_metrics[~df_retweeters_metrics["Bio"].str.contains("endorsement|Endorsement")]
    
    count3 = len(df_retweeters_metrics)
    
    print("Number of retweeters that did not state RT ≠ endorsement in their bio : " + str(count3))
    print("(%d retweeters are removed.)"%(count2 - count3))
    
    df_retweeters_metrics.to_excel(".//%s//df_retweeters_%s_metrics.xlsx"%(q, q))
    
    
    # Step 3: 抓Followers(雙向)
    # df_retweeters_metrics = pd.read_excel(".//%s//df_retweeters_%s_metrics.xlsx"%(q, q))
    senators_username_list = list(set(tweets_dict[q]["username"].astype(str)))
    senators_list = [FindID(x) for x in senators_username_list]
    df_senators = pd.DataFrame([senators_username_list, senators_list]).T
    df_senators.to_excel(".//%s//df_%s_senators.xlsx"%(q, q), index=False, header=False)
    
    retweeters_list = list(set(df_retweeters_metrics["ID"].astype(str)))
    full_list = senators_list + retweeters_list
    full_df = pd.DataFrame(full_list, columns=["id"])
    df_followers = pd.DataFrame()
    
    for i in range(len(full_list)):
        try:
            # checkpoint
            client, turn, iterations = CheckRateLimit(client, turn, iterations, "follower", "%d/%d"%(i, len(full_list)))
            following = client.get_users_following(full_list[i], max_results=1000)
            following_dict = following.json()
            if list(following_dict.keys())[0] != "errors":
                if following_dict["meta"]["result_count"] > 0:
                    following_data = following_dict['data']  
                    df6 = pd.json_normalize(following_data)
                    while following_dict['meta']['result_count'] == 1000:
                        try:
                            following_next_token = following_dict['meta']['next_token']
                            # checkpoint
                            client, turn, iterations = CheckRateLimit(client, turn, iterations, "follower", "%d/%d"%(i, len(full_list)))
                            next_following = client.get_users_following(full_list[i], pagination_token = following_next_token, max_results=1000)
                            following_dict = next_following.json()
                            if following_dict['meta']['result_count'] > 0:
                                next_following_data = following_dict['data']  
                                next_df6 = pd.json_normalize(next_following_data)
                                df6 = pd.concat([df6, next_df6], axis=0, sort=False, ignore_index=True)
                        except:
                            break
            df6 = df6[df6["id"].isin(full_df["id"])]
            df6["follower id"] = full_list[i]
            df6 = df6[["follower id", "id"]]
            df6.rename(columns = {'id':'followee id'}, inplace = True)
            df_followers = pd.concat([df_followers, df6], axis=0, sort=False, ignore_index=True)
        except:
            continue
    
    df_followers.to_excel(".//%s//df_%s_followee_followers.xlsx"%(q, q), index=False)

# In[]
q = "vaccine" # change topic here
df_retweeters = pd.read_excel(".\\%s\\df_retweeters_%s.xlsx"%(q, q))
df_retweeters_metrics = pd.DataFrame()
df1 = pd.DataFrame()
retweeters_list = list(set(df_retweeters["username"]))
string_list = []


for count in range(round(len(retweeters_list)/100)):
    starting_point = 0 + count*100
    lower_bound = 1 + count*100
    upper_bound = min(99 + count*100, len(retweeters_list)-1)
    list_100 = retweeters_list[lower_bound:upper_bound]
    string = retweeters_list[starting_point]
    for next_string in list_100:
        string = string + "," + next_string
    string_list.append(string)


for string in string_list:
    # checkpoint
    client, turn, iterations= CheckRateLimit(client, turn, iterations, "user", "N/A")
    user = client.get_users(usernames = string, user_fields=["public_metrics", "description"])
    user_dict = user.json()
    if list(user_dict.keys())[0] != "errors":
        df1_username = []
        df1_id = []
        df1_followers_count = []
        df1_following_count = []
        df1_listed_count = []
        df1_tweet_count = []
        df1_bio = []
        for j in range(len(user_dict["data"])):
            df1_username.append(user_dict["data"][j]["name"])
            df1_id.append(user_dict["data"][j]["id"])
            df1_followers_count.append(user_dict["data"][j]["public_metrics"]["followers_count"])
            df1_following_count.append(user_dict["data"][j]["public_metrics"]["following_count"])
            df1_listed_count.append(user_dict["data"][j]["public_metrics"]["listed_count"])
            df1_tweet_count.append(user_dict["data"][j]["public_metrics"]["tweet_count"])
            df1_bio.append(user_dict["data"][j]["description"])
        df_list = [df1_username,df1_id,df1_followers_count,df1_following_count,df1_listed_count,df1_tweet_count, df1_bio]
        df_list = list(map(list, zip(*df_list)))
        df1 = pd.DataFrame(df_list, columns=["Username", "ID", "Followers count", "Following count", "Listed count", "Tweet count", "Bio"]) 
    df_retweeters_metrics = pd.concat([df_retweeters_metrics, df1], axis=0, sort=False, ignore_index=True)
            

# 篩掉F+F低於2000的Retweeters
count1 = len(df_retweeters_metrics)
print("Number of retweeters: " + str(count1))
df_retweeters_metrics = df_retweeters_metrics[df_retweeters_metrics["Followers count"] + df_retweeters_metrics["Following count"] >= 2000]
count2 = len(df_retweeters_metrics)
print("Number of retweeters that have F+F greater than 2000: " + str(count2))
print("(%d retweeters are removed.)"%(count1 - count2))
df_not_endorsement = df_retweeters_metrics[df_retweeters_metrics["Bio"].str.contains("endorsement|Endorsement")]
df_retweeters_metrics = df_retweeters_metrics[~df_retweeters_metrics["Bio"].str.contains("endorsement|Endorsement")]
count3 = len(df_retweeters_metrics)
print("Number of retweeters that did not state RT ≠ endorsement in their bio : " + str(count3))
print("(%d retweeters are removed.)"%(count2 - count3))

df_retweeters_metrics.to_excel(".//%s//df_retweeters_%s_metrics.xlsx"%(q, q))

df_followers = pd.read_excel(".\\%s\\df_%s_followee_followers.xlsx"%(q, q))

df_followers = df_followers[~df_followers["follower id"].astype(str).isin(df_not_endorsement["ID"])]
df_followers = df_followers[~df_followers["followee id"].astype(str).isin(df_not_endorsement["ID"])]
df_followers = df_followers[["follower id", "followee id"]]


df_followers.to_excel(".//%s//df_%s_followee_followers.xlsx"%(q, q))

# In[] 2nd
q = "drug legalization" # change topic here
df_retweeters = pd.read_excel(".\\%s\\df_retweeters_%s.xlsx"%(q, q))
df_follower_followee= pd.read_excel(".//%s//df_%s_followee_followers.xlsx"%(q, q))
df_retweeters_metrics = pd.read_excel(".//%s//df_retweeters_%s_metrics.xlsx"%(q, q))
tweets_data = pd.read_excel("tweets_drug_legalization.xlsx")

# In[] 1st
df_not_excessive_retweeters = pd.read_excel(".//%s//df_not_excessive_retweeters_drug legalization.xlsx"%(q))

# In[]
df_excessive_retweeters = df_retweeters[df_retweeters["followee"] == "BernieSanders"]
df_excessive_retweeters = df_excessive_retweeters[~df_excessive_retweeters["id"].isin(df_not_excessive_retweeters["id"])]

# In[]
df_retweeters = df_retweeters[~df_retweeters["id"].isin(df_excessive_retweeters["id"])]
df_follower_followee = df_follower_followee[~df_follower_followee["follower id"].isin(df_excessive_retweeters["id"])]
df_follower_followee = df_follower_followee[~df_follower_followee["followee id"].isin(df_excessive_retweeters["id"])]
df_retweeters_metrics = df_retweeters_metrics[~df_retweeters_metrics["ID"].isin(df_excessive_retweeters["id"])] 

# In[]
df_follower_followee.to_excel(".//%s_revised//df_%s_followee_followers.xlsx"%(q, q))
df_retweeters_metrics.to_excel(".//%s_revised//df_%s_retweeters_metrics.xlsx"%(q, q))
df_retweeters.to_excel(".//%s_revised//df_%s_retweeters.xlsx"%(q, q))


