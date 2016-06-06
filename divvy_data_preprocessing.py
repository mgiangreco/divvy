import pandas as pd
import datetime as dt
import numpy as np
import os
from pandas.tseries.holiday import USFederalHolidayCalendar 

os.chdir('/Users/mgiangreco/Dropbox/EECS_349')

#create a list of Divvy_Trips files and the format of each file's datetime column
filename_fmts=[['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2013.csv', '%Y-%m-%d %H:%M'],
           ['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2014_Q1Q2.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2014-Q3-07.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2014-Q3-0809.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2014-Q4.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015-Q1.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015-Q2.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015_07.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015_08.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015_09.csv', '%m/%d/%Y %H:%M'],
['/Users/mgiangreco/Dropbox/EECS_349/Divvy_Trips_2015_Q4.csv', '%m/%d/%Y %H:%M']]

#function that creates an hourly index based on the minimum and maximum datetimes 
def reindex_by_date(df):
    dates = pd.date_range(df.index.min(), df.index.max(), freq='H')
    return df.reindex(dates)

#function that reads in the Divvy_Trips files, converts starttime columns to datetime format,
#...counts the number of trips for each hour by station_id, and fills in empty hours for each station_id with zeros
def bikeBin(filename, dt_fmt):   
    data = pd.read_csv(filename)
    data['starttime'] = data['starttime'].apply(lambda x: dt.datetime.strptime(x, dt_fmt))
    data['starttime'] = data['starttime'].apply(lambda x: x.replace(minute = 0))
    keeper_cols = ['starttime', 'from_station_id', 'trip_id']
    groupby_cols = ['from_station_id', 'starttime']
    df = data.loc[:, keeper_cols].groupby(groupby_cols).count().reset_index()
    df = df.set_index(['starttime'])
    df = df.groupby('from_station_id').apply(reindex_by_date).reset_index(0, drop=True)
    df['from_station_id'] = df['from_station_id'].ffill()
    df = df.fillna(value=0)
    df['depart_times']=df.index
    return df
     
#create an empty master dataframe
df_master = pd.DataFrame()

#function that concatenates the results from bikeBin into a single master df
for filename_fmt in filename_fmts:
    print (filename_fmt)
    df_temp = bikeBin(filename_fmt[0], filename_fmt[1])
    df_master = pd.concat([df_temp, df_master], ignore_index=True)
    
#set depart_times to index
df_master.set_index(['depart_times'], drop=True, inplace=True)

#resample df_master to 3 hour intervals
df_master = df_master.groupby('from_station_id').resample('3H', how='sum').reset_index()
df_master.set_index(['depart_times'], drop=True, inplace=True)

#replace missing values with zeroes
df_master = df_master.fillna(value=0)

#read in the weather file
weather = pd.read_csv('/Users/mgiangreco/Dropbox/EECS_349/weather.csv')

#keep only relevant columns from weather file
weather = weather[['datetime', 'precipi', 'pressurei', 'hum', 'tempi', 'dewpti', 
'visi', 'wspdi']]

#convert weather datetime column to datetime format
weather['datetime'] = weather['datetime'].apply(lambda x: dt.datetime.strptime(x, 
'%Y-%m-%d-%H'))

#replace anomalous weather readings with zero
weather.replace(to_replace=-9999.0, value=0, inplace=True)

#set datetime to index
weather.set_index(['datetime'], drop=True, inplace=True)

#resample weather to 3 hour intervals
weather = weather.resample('3H', how='mean')

#merge the master df and the weather df
merged_submaster = df_master.merge(weather, how='inner', left_index=True, 
                                   right_index=True, sort=False)

##STATION DATA##
#import the station data
stations_2013 = pd.read_csv('/Users/mgiangreco/Dropbox/EECS_349/Divvy_Stations_2013.csv')
stations_2014_Q1Q2 = pd.read_csv('/Users/mgiangreco/Dropbox/EECS_349/Divvy_Stations_2014-Q1Q2.csv')
stations_2014_Q3Q4 = pd.read_csv('/Users/mgiangreco/Dropbox/EECS_349/Divvy_Stations_2014-Q3Q4.csv')
stations_2015 = pd.read_csv('/Users/mgiangreco/Dropbox/EECS_349/Divvy_Stations_2015.csv')

stations_2013 = stations_2013[['id', 'latitude', 'longitude']]
stations_2014_Q1Q2 = stations_2014_Q1Q2[['id', 'latitude', 'longitude']]
stations_2014_Q3Q4 = stations_2014_Q3Q4[['id', 'latitude', 'longitude']]
stations_2015 = stations_2015[['id', 'latitude', 'longitude']]

merged_stations = pd.concat([stations_2013, stations_2014_Q1Q2,stations_2014_Q3Q4, stations_2015])
merged_stations.sort_values(['id'], inplace=True)
merged_stations.drop_duplicates(subset='id', inplace=True)
merged_stations.rename(columns={'id': 'from_station_id'}, inplace=True)


#merge the master df and the station df
merged_master = merged_submaster.reset_index().merge(merged_stations, how='left', 
on='from_station_id').set_index('index')

#sort merged_master df based on station_id and then by depart_times
merged_master['depart_times']=merged_master.index
merged_master.sort_values(['from_station_id', 'depart_times'], inplace=True)

#drop depart_times column
merged_master.drop(['depart_times'], axis=1, inplace=True)

#rename trip_id column to trips_count
merged_master.rename(columns={'trip_id': 'trip_count'}, inplace=True)

#add a column for hour of day
merged_master['hour_of_day'] = merged_master.index.hour

#drop non-daylight hours
merged_master = merged_master[(merged_master.hour_of_day > 5) & (merged_master.hour_of_day < 16)]

#create hour of day dummies
dummy_df = pd.get_dummies(merged_master['hour_of_day'], prefix='hour')
merged_master = pd.concat([merged_master,dummy_df], axis=1)

#drop hour of day field
merged_master.drop('hour_of_day', axis=1, inplace=True)

#add a column for day of the week and create day of week dummies
merged_master['day_of_week'] = merged_master.index.weekday
dummy_df = pd.get_dummies(merged_master['day_of_week'], prefix='day')
merged_master = pd.concat([merged_master,dummy_df], axis=1)

#add a dummy variable for weekend day
merged_master['weekend_day'] = np.where((merged_master['day_of_week']==5)|(merged_master['day_of_week']==6),1,0)

#drop day_of_week field
merged_master.drop('day_of_week', axis=1, inplace=True)

#add a column for month and create month dummies
merged_master['month'] = merged_master.index.month
dummy_df = pd.get_dummies(merged_master['month'], prefix='month')
merged_master = pd.concat([merged_master,dummy_df], axis=1)
merged_master.drop('month', axis=1, inplace=True)

#add a column for holiday
merged_master['date'] = merged_master.index.date
merged_master['date'] = pd.to_datetime(merged_master['date'])
cal = USFederalHolidayCalendar()
holidays = cal.holidays(start=merged_master.date.min(), end=merged_master.date.max())
merged_master['holiday'] = merged_master['date'].isin(holidays).astype(int)
merged_master.drop('date', axis=1, inplace=True)

#add a column for days since first date in dataset
merged_master['days_since_first_date'] = (merged_master.index.date - (merged_master.index.date.min())).astype('timedelta64[D]').astype(int)

#Drop any rows with null values
merged_master.dropna(axis=0, inplace=True)

#rearrange column order
merged_master['station_id'] = merged_master['from_station_id']
merged_master.drop(['from_station_id'], axis=1, inplace=True)
