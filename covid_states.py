from bs4 import BeautifulSoup
from datetime import datetime
from utilities import sms
import requests
import json
import sys
import os

today = datetime.today()

filename = os.path.join(sys.path[0], 'covid-data.txt')


def get_saved_data(state_name):
    with open(filename, 'r+') as file:
        states = json.load(file)
        try:
            return states[1][state_name]
        except KeyError:
            states[1][state_name] = {"old": {"pos": 0, "neg": 0, "tot": 0, "ded": 0, "upd": "0"},
                                     "new": {"pos": 0, "neg": 0, "tot": 0, "ded": 0, "upd": "0"}}
            file.seek(0)
            json.dump(states, file)
            return states[1][state_name]


def save_file(state_name, pos, neg, total, death, date):
    with open(filename, 'r+') as file:
        states = json.load(file)
        states[1][state_name]['old'] = states[1][state_name]['new']
        states[1][state_name]['new'] = {"pos": pos, "neg": neg, "tot": total, "ded": death, "upd": date}
        file.seek(0)
        json.dump(states, file)


def get_data(*args):
    results = ""

    url = 'https://covidtracking.com/api/states'

    for state in args:
        r = requests.Session()
        params = {'state': state}
        raw_data = r.get(url, params=params)
        raw_data.raise_for_status()
        new_data = json.loads(raw_data.text)

        if new_data:
            state_name = new_data['state']
            saved_data = get_saved_data(state_name)

            positive = new_data['positive']
            negative = new_data['negative']
            total = new_data['total']
            death = new_data['death']
            updated = new_data['lastUpdateEt']

            # Using * to bold and _ to italicize in WhatsApp
            results += f'''
*{new_data['state']}* - _Updated: {updated}_
Positive: {positive:,} *(+{positive - saved_data['old']['pos']:,})*
Negative: {negative:,} *(+{negative - saved_data['old']['neg']:,})*
Total: {total:,} *(+{total - saved_data['old']['tot']:,})*
Death: {death:,} *(+{death - saved_data['old']['ded']:,})*
'''

            if state == "TX":
                url_county = 'https://dshs.texas.gov/news/updates.shtm'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
                try:
                    r2 = requests.Session()
                    s2 = r2.get(url_county, headers=headers, verify=False)
                    soup2 = BeautifulSoup(s2.text, 'lxml')

                    table = soup2.find('table', summary="COVID-19 Cases in Texas Counties")
                    counties = ['Harris', 'Fort Bend']
                    for county in counties:
                        label = table.find('td', text=county)
                        cases = label.find_next_sibling('td').text

                        results += f'*{county} County:* {cases} cases\n'
                except:
                    results += '_Cannot retrieve county data_'

            # If the last updated date is the same as today then dont update numbers
            last_updated = updated.split()[0]
            if saved_data['new']['upd'] == last_updated:
                pass
            else:
                save_file(state_name, positive, negative, total, death, last_updated)

        else:
            results += f'''
            Unable to retrieve data for {state}
            '''

    return results


if __name__ == '__main__':
    final = ""
    final += get_data('TX', 'NJ')
    sms.send_whatsapp(final)
