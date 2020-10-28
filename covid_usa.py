from firebase_admin import credentials
from firebase_admin import firestore
from bs4 import BeautifulSoup
from utilities import sms
import firebase_admin
import requests
import sys
import re
import os

# Initializing Firebase Database called covid19
cred = credentials.Certificate(os.path.join(sys.path[0], 'fbapp.json'))
firebase_admin.initialize_app(cred, {'projectId': os.getenv('PROJECT_ID')})
db = firestore.client().collection(os.getenv('COLLECTION_NAME'))


class Location:
    """
    Holds the data for each location
    """

    def __init__(self, name, deaths, total, **kwargs):
        self.name = name
        self.deaths = deaths
        self.total = total
        self.recovered = kwargs.get('recovered')    # not using this data
        self.new_cases = kwargs.get('new_cases')
        self.new_deaths = kwargs.get('new_deaths')

    def to_dict(self):
        """
        Converts the Location data into a dictionary
        :return: dictionary of data
        """

        return {
            'deaths': self.deaths,
            'total': self.total,
            'new_cases': self.new_cases,
            'new_deaths': self.new_deaths}

    def __str__(self):
        """
        Converts the Location data into a formatted string
        :return: formatted string of data
        """

        return f'''
*{self.name}*:
😷 {self.total} *({self.new_cases if self.new_cases else 0})*
☠ {self.deaths} *({self.new_deaths if self.new_deaths else 0})*
'''


def load_db():
    """
    Loads the database from Firebase
    :return: Dictionary of database data
    """

    data = {}

    # Data is retrieved from the database as a stream
    data_raw = db.stream()

    # Creating a dictionary from the stream data
    for d in data_raw:
        data[d.id] = d.to_dict()
    return data


def update_db(new_data):
    """
    Updates the Firebase database
    :param new_data: the new data retrieved from Worldometer
    """

    try:
        # Update the database, if the "document" i.e. location name doesnt exist
        db.document(new_data.name).update(new_data.to_dict())
    except:
        # Create a new "document" i.e. location name ex: Texas, if error above
        db.add(new_data.to_dict(), new_data.name)


def get_main_data(name, parsed_url):
    """
    Get data for USA from the parsed data

    :param name: Name of location
    :param parsed_url: Passed url
    :return: Data for location as a Location class object
    """

    # Building the url for location
    url = "https://www.worldometers.info/coronavirus/" + parsed_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

    s = requests.Session()
    r = s.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')

    # Getting the totals from the big counter on the location page
    totals_raw = soup.find_all('div', class_="maincounter-number")
    main_raw = list(map(lambda x: x.text.strip(), totals_raw))
    cases, deaths, recovered = main_raw

    # Getting New Cases and New Deaths from the main table
    # Selecting the table with the data
    table = soup.find('table', id="usa_table_countries_today")

    # Finding the cell in the table that contains the state total data (first row of table)
    cells = table.find('tr', class_="total_row_usa")

    # Selecting the next 6 cells after the cell with the State name
    main_data = cells.find_all_next('td', limit=6)

    # Getting the text from each of the cells and running strip() and making a list
    main_data_raw = list(map(lambda x: x.text.strip(), main_data[1:]))

    # Extracting data into variables
    total_cases, new_cases, total_deaths, new_deaths, active_cases = main_data_raw

    return Location(name, deaths, cases, recovered=recovered, new_cases=new_cases, new_deaths=new_deaths)


def get_county(county_name):
    """
    Get data for county from the state url/page

    :param county_name: Name of the county for which to pull data
    :return: Data for the State as a Location class object
    """

    url = "https://www.worldometers.info/coronavirus/usa/texas"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

    s = requests.Session()
    r = s.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')

    # Getting County Data
    # Selecting the table with the county data
    table = soup.find('table', id="usa_table_countries_today")

    # Finding the cell in the table that contains the county name
    cells = table.find('td', text=re.compile(county_name))

    # Selecting the next 5 cells after the cell with the State name
    county_data = cells.find_all_next('td', limit=5)

    # Getting the text from each of the cells and running strip() and making a list
    county_raw = list(map(lambda x: x.text.strip(), county_data))

    # Extracting data into variables
    total_cases, new_cases, total_deaths, new_deaths, active_cases = county_raw

    return Location(county_name, total_deaths, total_cases, new_cases=new_cases, new_deaths=new_deaths)


def get_results():
    """
    Gets the data from Worldometer
    Extracts Data for USA and each State
    Updates the Firebase database
    Returns a string containing all the results

    :return: Results for USA and States in a String format
    """

    urls = {'USA': "country/us/", 'Texas': "usa/texas"}
    counties = ['Harris', 'Fort Bend']

    final_results = []
    final_string = ""
    need_update = False
    old_results = load_db()

    for k, v in urls.items():
        final_results.append(get_main_data(name=k, parsed_url=v))

    # Getting the County data for each county
    for county in counties:
        final_results.append(get_county(county))

    # Comparing data retrieved to the database data to see if a new message needs to be sent
    for result in final_results:
        if result.total != old_results[result.name]['total']:
            need_update = True
        if result.deaths != old_results[result.name]['deaths']:
            need_update = True

        # Appending the USA/State/County results to a string
        final_string += result.__str__()

        # Updating the Firebase database
        update_db(result)

    return final_string, need_update


if __name__ == '__main__':
    results, need_to_update = get_results()

    if need_to_update:
        print('Got new data from covid_usa.py')
        # Sending the string results as a WhatsApp message
        sms.send_whatsapp(results)
