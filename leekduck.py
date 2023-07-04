#!/usr/bin/env python3
from bs4 import BeautifulSoup
import datetime
import ics
import pytz
import requests

cal = ics.Calendar()
cal.creator = "codygarver"
cal.method = "PUBLISH"
cal.name = "Pokemon Go Events"
cal.timezone = "US/Eastern"

url = "https://leekduck.com"

page = requests.get(url + "/events/")

soup = BeautifulSoup(page.content, 'html.parser')

# Find all event spans
spans = soup.find_all('span', class_='event-header-item-wrapper')

for span in spans:
    # Create event
    cal_event = ics.Event()

    # Event name
    h2 = span.find('h2')
    cal_event.name = h2.text

    # Begin date
    try:
        begin_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-end-date"]
    except:
        continue
    begin_date_local = datetime.datetime.strptime(begin_date, "%Y-%m-%dT%H:%M:%S%z")
    #begin_date_local = begin_date_local.astimezone(pytz.timezone('US/Eastern'))
    # Subtract 12 hours from begin_date_local
    begin_date_local = begin_date_local - datetime.timedelta(hours=12)
    cal_event.begin = begin_date_local

    # End date
    try:
        end_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-end-date"]
    except:
        continue
    end_date_local = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z")
    #end_date_local = end_date_local.astimezone(pytz.timezone('US/Eastern'))
    # Subtract 12 hours from end_date_local
    end_date_local = end_date_local - datetime.timedelta(hours=12)
    cal_event.end = end_date_local

    # URL
    link = url + span.find('a', class_='event-item-link', href=True)['href']
    cal_event.url = link

    # DTSTAMP
    cal_event.created = begin_date_local

    # Add event to calendar
    cal.events.add(cal_event)

# Write calendar to file
with open('pokemon-go-events.ics', 'w') as cal_file:
    cal_file.writelines(cal)