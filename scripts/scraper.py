from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

def find_incumbents(url):
    r = requests.get(url)
    html = r.text
    year = int(re.search('(\d{4})', url).group())
    soup = BeautifulSoup(html, 'html.parser')  
    table = soup.find(class_='votebox')
    header = table.find(class_='votebox-header-election-type').text
    state, district = re.search(r'General election for U.S. House (.+) District (\d+)', header).groups()
    results = table.find_all(class_=re.compile(r'results_row(?:$|.*)'))
    for row in results:
        global df
        text = row.find(class_='votebox-results-cell--text').text
        if "Other/Write-in votes" in text: candidate, party = "", "Other"
        else: candidate, party = re.search(r'((?:\.|\w|\s)+) \(((?:\/|\w+|\s+)+)\)', text).groups()
        votes = row.find(class_='votebox-results-cell--number', string=re.compile(r'\d+'), recursive=False).text
        incumbent = not not row.find('u')
        df = pd.concat([df, pd.DataFrame([[year, state, district, candidate, party, votes, incumbent]], columns=df.columns)])
        
def find_district_links(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')  
    links = soup.find_all('a', href=re.compile(r'.*Congressional_District_election,_\d{4}$')) 
    for l in set(links):
        find_incumbents('https://ballotpedia.org'+l.get('href'))

def main():
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_New_York,_2022')
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Georgia,_2022')
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Illinois,_2022')
    
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_New_York,_2020')
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Georgia,_2020')
    find_district_links('https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Illinois,_2020')


if __name__ == '__main__':
    df = pd.DataFrame(columns=['year', 'state', 'district', 'name', 'party', 'votes', 'incumbent'])
    main()
    df.to_csv('scripts/data/house_candidates_by_district', index=False)