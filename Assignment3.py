"""
Date: 03/01/2024
Description: Script pulls the statistical data on the top 20 most popular YouYube videos on the US chart
via YouTube API and imports it into a redis JSON. 

References:
https://developers.google.com/youtube/v3/docs/videos/list
https://redis.io/docs/connect/clients/python/

"""

from googleapiclient.discovery import build
from dotenv import load_dotenv
from db_config import get_redis_connection
import matplotlib.pyplot as plt 
import pandas as pd
import json
import redis
import os

load_dotenv()
'''loads environmental values from .env'''

class Data:
      def import_JSON():
            '''Imports YouTube API data into a redis JSON
            
            Returns
            youTubeJSON: Redis JSON object'''

            api_key = os.getenv('api_key') 
            youtube = build('youtube', 'v3', developerKey = api_key)

            #creats data request for statistics on top 20 Youtube Videos
            requests = youtube.videos().list(
                  part='statistics',
                  chart='mostPopular',
                  regionCode='US',
                  maxResults=20
                  )
                 
            response = requests.execute()
       
            #Imports Data into redisJSON
            r = get_redis_connection()
            r.json().set('YouTubeData', '.',response)
            
            #Gets redisJSON and places into JSON object 'youtubeJSON'
            global youtubeJSON
            youtubeJSON = r.json().get('YouTubeData')

      import_JSON()




class Procsess:
      ''' loads JSON object into a pandas Data Frame
      Does some processing and plotting
      '''

      #loads 'youtubeJSON' into Data frame 'df' and replaces header titles
      df = pd.json_normalize(youtubeJSON, record_path=['items']), 
      df[0].rename(columns={'id': 'videoID','statistics.viewCount': 'ViewCount', 'statistics.likeCount':
                       'LikeCount', 'statistics.commentCount': 'CommentCount' }, inplace=True) 

      print(df)

      #drops unnecessary columns from 'df' and saves as new Data Frame 'df2'
      #defines values as integers and orders by 'CommentCount'
      df1 = df[0].drop(['kind', 'etag','statistics.favoriteCount'], axis=1)
      df1["ViewCount"]=df1["ViewCount"].astype(int)
      df1['LikeCount']=df1['LikeCount'].astype(int)
      df1['CommentCount']=df1['CommentCount'].astype(int)
      df1=df1.sort_values(by='CommentCount')

      print(df1)


      #Plots Youtube Like Counts vs Comment Counts in bar chart
      df1.plot(x="videoID", y=["LikeCount", "CommentCount"], kind="bar") 
      plt.title('YouTube Like Counts vs Comment Counts')
      plt.show()

      #Plots Youtube Like Counts vs View Counts in scatter plot
      df1.plot.scatter('LikeCount', 'ViewCount')
      plt.title("Youtube View Counts vs Like Counts")
      plt.show() 


