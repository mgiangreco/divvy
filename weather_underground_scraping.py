from datetime import date, timedelta, datetime
import time
import requests
import csv


ENDPOINTpt1 = 'http://api.wunderground.com/api/9909d75a929b220c/history_'
ENDPOINTpt2 = '/q/IL/Chicago.json'



def getWeather(day):
	year  = str(day.year)
	month = str(day.month).zfill(2)
	day   = str(day.day).zfill(2)

	dateString = year + month + day

	r = requests.get(ENDPOINTpt1 + dateString + ENDPOINTpt2)
	return r.json()



def storeWeather(day, weather):
	year  = str(day.year)
	month = str(day.month).zfill(2)
	day   = str(day.day).zfill(2)
	dayString = year + "-" + month + "-" + day + "-"

	with open('weather.csv', 'a') as file:
	    writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

	    observations = weather['history']['observations']

	    # writer.writerow(createHeaderLine(observations[0]))
	    hours = []
	    for hourInfo in observations:
	    	hour = hourInfo['date']['hour']
	    	# take at most one reading per hour
	    	if hour not in hours:
	    		hours.append(hour)
	    		writer.writerow(createHourLine(dayString, hourInfo))

	    file.close()



def createHeaderLine(hourInfo):
	line = ['datetime']
	for field in hourInfo:
		if field not in ['date', 'utcdate']:
			line.append(field)
	return line



def createHourLine(dayString, hourInfo):
	line = [dayString + str(hourInfo['date']['hour'])]
	for field in hourInfo:
		if field not in ['date', 'utcdate']:
			line.append(hourInfo[field])
	return line



def getDaysBetween(start, end):
	delta = end - start
	for x in xrange(delta.days + 1):
		day = start + timedelta(days=x)
		storeWeather(day, getWeather(day))
		



def main():
	start = date(2014, 11, 4)
	end   = date(2015, 1, 1)
	# end   = date(2014, 12, 31)
	getDaysBetween(start, end)


	# you're getting month by month, backing up each time



if __name__ == "__main__":
	main()