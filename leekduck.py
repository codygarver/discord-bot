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
#cal.timezone = "US/Eastern"

url = "https://leekduck.com"

page = requests.get(url + "/events/")

soup = BeautifulSoup(page.content, 'html.parser')

# Find all event spans
spans = soup.find_all('span', class_='event-header-item-wrapper')

for span in spans:
    try:
        # Create event
        cal_event = ics.Event()

        # Event name
        h2 = span.find('h2')
        cal_event.name = h2.text

        # Determine local time
        if span.find_all("h5", class_="event-header-time-period")[0]["data-event-local-time"] == "true":
            display_local_time = True
        else:
            display_local_time = False

        # Begin date
        if display_local_time:
            begin_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-start-date-check"][:-5] + "-0400"
        else:
            begin_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-start-date-check"]
        begin_date_local = datetime.datetime.strptime(begin_date, "%Y-%m-%dT%H:%M:%S%z")
        begin_date_local = begin_date_local.astimezone(pytz.timezone('US/Eastern'))
        cal_event.begin = begin_date_local

        # End date
        if display_local_time:
            end_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-end-date"][:-5] + "-0400"
        else:
            end_date = span.find_all("h5", class_="event-header-time-period")[0]["data-event-end-date"]
        end_date_local = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z")
        end_date_local = end_date_local.astimezone(pytz.timezone('US/Eastern'))
        cal_event.end = end_date_local

        # URL
        link = url + span.find('a', class_='event-item-link', href=True)['href']
        cal_event.url = link

        # DTSTAMP
        cal_event.created = begin_date_local

        # Add event to calendar
        cal.events.add(cal_event)
    except:
        continue

# Write calendar to file
with open('pokemon-go-events.ics', 'w') as cal_file:
    cal_file.writelines(cal)