import os
from pathlib import Path
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import matplotlib.pyplot as plt
import random


date_now=datetime.now().strftime('%Y-%m-%d')
time_now=datetime.now().strftime('%H:%M:%S')


# cols = ['Date','Time','Inside Temp', 'Inside Pressure', 'Inside Humidity', 'Raw Inside Temp Sensor','Outside Temp', 'Outside Pressure', 'Outside Humidity']
# data = [('2020-12-31','23:59:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:00:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:01:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:02:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:03:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:04:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:05:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:06:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0),
#         ('2021-01-01','00:07:00', 72.0, 29.9, 50.0, 72.0, 72.0, 29.9, 50.0)
#         ]
# df = DataFrame(data,columns=cols)
# print(df)
#
# df.to_csv('test.csv',index=False)



new_data = {'Date':f'{date_now}','Time':f'{time_now}','Inside Temp':72.0 + random.random()*10,'Inside Humidity':29.9 + random.random()*10,'Raw Inside Temp Sensor':50 + random.random()*10,'Outside Temp': 42 + random.random()*10, 'Outside Pressure':29 + random.random()*10, 'Outside Humidity':55 + random.random()*10}
new_df= DataFrame([new_data])

# df = pd.concat([df,new_df],ignore_index=True)
df=new_df

path = Path('./test.csv')
if path.is_file():
        print("file exists append data to it")
        df.to_csv('test.csv',index=False, mode='a', header=False)
else:
        print("file does not exist create it")
        df.to_csv('test.csv',index=False, mode='w', header=True)

df_to_graph = pd.read_csv('test.csv')
# graph = df_to_graph.plot(x='Time', y=['Inside Temp', 'Outside Temp','Inside Humidity'], title='Greenhouse Temperature and Humidity', xlabel='Time', ylabel='Temperature (F)', xticks=df_to_graph.index, rot=90, figsize=(20,10), grid=True)
graph = df_to_graph.plot(x='Time', y=['Inside Temp', 'Outside Temp','Inside Humidity'], title='Greenhouse Temperature and Humidity', xlabel='Time', ylabel='Temperature (F)', xticks=[], figsize=(20,10), grid=True)
fig = graph.get_figure()
fig.savefig('GreenHouseChart.png')

import boto3
s3 = boto3.resource('s3')
s3.Bucket('johnfunk.com').upload_file(Filename='GreenHouseChart.png', Key='greenhouse/GreenHouseChart.png')
