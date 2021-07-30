import json
import re
from pprint import pprint
from functools import reduce
from typing import Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

p_url = re.compile(r'href=\S+')
p_wiki = re.compile(r'/wiki/\S+')
p_national = re.compile(r' national')
p_digit = re.compile(r'\d+')
p_goals = re.compile(r'\d+\sgoals?')
p_assist = re.compile(r'\d+\sassists?')
p_parenthesis = re.compile(r'\(.+\)')
p_height_m = re.compile(r'\d\.\d*.*m')
p_height_cm = re.compile(r'\d*\s?cm')
p_height = re.compile(r'\d\.\d*')
p_birth_date_headline = re.compile(r'Date of birth|Born')
p_national_team = re.compile(r'National team\.?')


def get_lists(url: str) -> ([], []):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    names = soup.findAll('div', attrs={'class': 'div-col'})
    paragraphs = soup.findAll('p')
    headlines = [paragraph.find('b') for paragraph in paragraphs]
    if sum([headline != None and 'goal' in headline.text for headline in headlines]) == 0:
        headlines = soup.findAll('dt')
        # headlines=[1]
    return names, headlines


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html5lib')


def get_scorers(soup: BeautifulSoup) -> [[str]]:
    li_elems = soup.findAll('li')
    names = map(lambda li: p_wiki.findall(str(li)), li_elems)
    filtered = list(filter(lambda x: x, names))
    return list(filtered)


def get_goals_num(soup: BeautifulSoup) -> {}:
    goals = {}
    body = soup.find('div', attrs={'class': 'mw-parser-output'})
    headlines = body.findAll('b', text=p_goals)
    if sum([headline is not None and 'goal' in headline.text for headline in headlines]) == 0:
        headlines = body.findAll('dt', text=p_goals)

    # filtered = filter(lambda x: p_goals.match(x.text),headlines)
    # headlines = list((map(lambda x: p_goals.match(x.text).group(),filtered)))
    for h in set(headlines):
        next_elem = h.findNext('ul').findAll('li')
        goals[int(p_digit.search(h.text).group())] = next_elem
    return goals


def extract_dict_data(goals_dictionary: {}) -> {}:
    url_dictiionary = {}
    for num, soup_elem in goals_dictionary.items():
        players = [player.find_all('a', href=True) for player in soup_elem]
        players_hrefs = [[href['href'] for href in player] for player in players]
        url_dictiionary[num] = [list(map(get_pure_url, player_urls)) for player_urls in players_hrefs]
    return url_dictiionary


def get_name(soup_table: BeautifulSoup) -> str:
    name = soup_table.find('caption', attrs={'class': 'fn'})
    print(name)
    print(name.text)
    for s in name.find_all('style'):
        s.decompose()
    for s in name.find_all('span'):
        s.decompose()
    return ''.join([ch for ch in name.text if ch.isalpha() or ch == ' '])
    # return name


def get_age(soup: BeautifulSoup, tournament_year: int) -> int:
    age_row = soup.find('th', text=p_birth_date_headline)
    birth_date = age_row.find_next_sibling('td').text
    return tournament_year - int(p_digit.search(birth_date).group())


def get_height(soup: BeautifulSoup):
    height_row = soup.find('th', text='Height')
    height = height_row.find_next_sibling('td').text
    h_meters = p_height_m.search(height)
    if h_meters:
        height_str = h_meters.group()
        height_meters = p_height.search(height_str).group()
        return float(height_meters)
    else:
        h_cm = p_height_cm.search(height)
        height_str = h_cm.group()
        height_cm = p_digit.search(height_str).group()
        return float(height_cm) / 100


def get_team_league(soup: BeautifulSoup, year: int) -> (str, str):
    team, team_url = get_team(soup, year)
    league, country = '', ''
    if team_url != '':
        r = requests.get(team_url)
        soup_league = BeautifulSoup(r.content, 'html5lib')
        league, league_url = get_league(soup_league)
        country = get_league_country(league_url)
    return team, f'{league} ({country})'


def get_league_country(league_url: str):
    try:
        r = requests.get(league_url)
        soup = BeautifulSoup(r.content, 'html5lib')
        country_row = soup.find('th', text='Country')
        country = country_row.find_next_sibling('td').text
        country = p_parenthesis.sub('', country)
        return country.strip()
    except:
        return ''


def check_dates(dates_range_str: str, year: int):
    last_date = dates_range_str.replace('0000', '').strip()
    if (not last_date[-1].isdigit()) and int(p_digit.search(last_date).group()) < year:
        return True
    dates = [int(date) for date in p_digit.findall(dates_range_str)]
    if len(dates) == 1:
        if dates[0] == year:
            return True
        return False
    if dates[0] < year <= dates[1]:
        return True
    return False

def check_dates_kuba(year_range: str, year: int) -> bool:
    int_range = [int(x) if x else 9999 for x in re.split(r'\D', year_range)]
    int_range = [x if x!=0 else 9999 for x in int_range]
    int_range = int_range * 2 if len(int_range)==1 else int_range
    return int_range[0] <= year <= int_range[1]


def cut_initial_chars(name: str) -> str:
    if name.strip() == "":
        return ""
    i = -1
    valid_start = False
    while not valid_start:
        i += 1
        valid_start = name[i].isalnum()
    return name[i:]


def get_team(soup: BeautifulSoup, tournament_year: int):
    # elem_after_teams = soup.find('th', p_national_team)
    # print(elem_after_teams.text)
    # teams = elem_after_teams.find_all_previous('th')

    table_components = soup.findAll('tr')[::-1]
    teams_found, correct_team = False, False
    i = 0
    team, team_url = '', ''
    while not teams_found and i < len(table_components):
        row = table_components[i].find('th')
        if row and 'National team' in row.text:
            # print(row.text)
            teams_found = True
            if table_components[i + 1].find('th').text == 'Total':
                i += 1
            while not correct_team:
                most_recent_team = table_components[i + 1]
                # pprint(most_recent_team)
                # print('--------------')
                most_recent_team_dates = most_recent_team.find('span')
                # print("most recent  SPAN")
                # pprint(most_recent_team_dates)
                if not most_recent_team_dates or not most_recent_team_dates.text:
                    return team, team_url
                if most_recent_team_dates and check_dates(most_recent_team_dates.text, tournament_year):
                    team_elem = most_recent_team.find('td')
                    team = team_elem.text
                    # print(most_recent_team_dates.text)
                    # print('PRZED CUT', team)
                    # print("PO CUT")
                    team = cut_initial_chars(p_parenthesis.sub('', team))
                    team_url = p_wiki.search(str(team_elem))
                    # print('|||||||||||||||||||||||||', team)
                    team_url = get_pure_url(team_url.group())
                    # print('|||||||||||||||||||||||||', team_url)
                    correct_team = True
                else:
                    # print('?else')
                    i += 1
        i += 1
        # print(team_url)
    return team.strip(), team_url


def get_league(soup: BeautifulSoup) -> (str, str):
    league, league_url = 'No club', '-'
    try:
        league_headline = soup.find('table', attrs={'class': 'infobox vcard'}).find('th', text='League')
        league = league_headline.find_next_sibling('td')
        league_url = get_pure_url(league.find('a', href=True)['href'])
        return league.text, league_url
    except Exception as e:
        print('EXCEPT', e)
        return league, league_url


def get_nation(soup: BeautifulSoup) -> str:
    nation = soup.find('h1', attrs={'id': 'firstHeading'}).text
    span = p_national.search(nation)
    if span:
        span = span.span()
        return nation[:span[0]]
    return nation


def get_player_data(url_nation: str, url_player: str, tournament_year: int) -> {}:
    r_nation = requests.get(url_nation)
    soup_nation = BeautifulSoup(r_nation.content, 'html5lib')
    r_player = requests.get(url_player)
    soup_player = BeautifulSoup(r_player.content, 'html5lib')
    soup_player_table = soup_player.find('table', attrs={'class': 'infobox vcard'})
    name = get_name(soup_player_table)
    # print(name)
    age = get_age(soup_player_table, tournament_year)
    # print(age)
    height = get_height(soup_player_table)
    # print('H', height)
    team, league = get_team_league(soup_player_table, tournament_year)
    # print(team, league)
    nation = get_nation(soup_nation)
    # print(nation)
    player_data = {'name': name, 'age': age, 'height': height, 'club': team, 'league': league, 'country': nation}
    return player_data


def get_pure_url(url: str) -> str:
    html_base = 'https://en.wikipedia.org'
    main = p_wiki.search(url).group()
    if main[-1] == '"':
        main = main[:-1]
    return html_base + main


def get_goal_scorers(goals_dictionary, tournament_year: int) -> ({str: {str}}):
    players_data = []
    for goals_num, players in goals_dictionary.items():
        for player in players:
            nation_url = player[0]
            player_url = player[1]
            player_dict = get_player_data(nation_url, player_url, tournament_year)
            player_dict['goals'] = goals_num
            print(player_dict)
            players_data.append(player_dict)
    return players_data


def get_assistants(names: [], assists_num_headlines: [], start_ind: int, tournament_year: int):
    assistant_names = names[start_ind:]
    assistants_urls = [p_url.findall(str(assistant_names[i])) for i in range(len(assists_num_headlines))]
    assistants_data = []
    assists_num_ind = 0
    for assistants in assistants_urls:
        assists_num = assists_num_headlines[assists_num_ind]
        assistants_num = len(assistants) // 2
        i = 0
        for assistant_ind in range(assistants_num):
            nation_url = get_pure_url(assistants[i])
            assistant_url = get_pure_url(assistants[i + 1])
            i += 2
            assistant_dict = get_player_data(nation_url, assistant_url, tournament_year)
            assistant_dict['assists'] = assists_num
            assistants_data.append(assistant_dict)
            print(assistant_dict)
        assists_num_ind += 1
    return assistants_data


def get_scored_goals_headlines(headlines: []) -> [int]:
    sorted_headlines = [p_goals.search(headline.text) for headline in headlines if headline]
    sorted_headlines = [headline.group() for headline in sorted_headlines if headline]
    return [int(p_digit.search(goals).group()) for goals in sorted_headlines]


def get_assist_headlines(headlines: []) -> [int]:
    assists_list = [p_assist.search(headline.text) for headline in headlines if headline]
    assists_list = [headline.group() for headline in assists_list if headline]
    return [int(p_digit.search(assists).group()) for assists in assists_list]


def save_json(filename: str, players_dictionary: {}):
    with open(filename, 'w') as players_file:
        data = json.dumps(players_dictionary)
        players_file.write('playerData = ')
        players_file.write(data)


def get_senior_career_trs(soup: BeautifulSoup) -> ResultSet:
    trs = soup.findAll('tr')
    take_after = lambda acc, elem: (acc[0]+[elem], True) if acc[1] else (acc[0], "Years" in elem.text and "Team" in elem.text)
    (head_removed, temp) = reduce(take_after, trs, ([], False))
    take_while = lambda acc, elem: (acc[0]+[elem], True) if "National team" not in elem.text and acc[1] else (acc[0], False)
    (tail_removed, temp) = reduce(take_while, head_removed, ([], True))
    return tail_removed


def get_team_kuba(soup: BeautifulSoup, tournament_year: int) -> Tuple[str, str]:
    for tr in get_senior_career_trs(soup):
        years = tr.find('th').getText(strip=True)
        url = tr.find('a')['href']
        team_name = tr.find('a')['title']
    result = [(x[0], x[1], x[3]) for x in map(parse_player_tr, get_senior_career_trs(soup)) if check_dates_kuba(x[2], tournament_year)]
    if len(result) > 1:
        result = [x for x in result if x[2]]
    if len(result) == 0: return '', ''
    team, url, on_loan = result[0]
    return team, get_pure_url(url)


def parse_player_tr(tr: BeautifulSoup) -> Tuple[str, str, str]:
    return (tr.find('a')['title'], tr.find('a')['href'], tr.find('th').text, '(loan)' in tr.text)


if __name__ == '__main__':
    stats_url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2020_statistics'
    # stats_url = 'https://en.wikipedia.org/wiki/2006_FIFA_World_Cup_statistics'
    # stats_url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2012_statistics'
    # players_names, goals_headlines = get_lists(stats_url)
    # pprint(players_names)
    # pprint(len(players_names))
    # print(goals_headlines)
    # goals_scored_headlined = get_scored_goals_headlines(goals_headlines)
    # scorers_dict = get_goal_scorers(players_names, goals_scored_headlined, 2006)
    # save_json('../js/data_2006.js', scorers_dict)

    # goals_headlines_num = len(goals_scored_headlined) + 1
    # assists_headlines = get_assist_headlines(goals_headlines)
    # assistants_dict = get_assistants(players_names, assists_headlines, goals_headlines_num)
    # save_json('../js/assists_data.js', assistants_dict)

    # r = get_player_data("https://en.wikipedia.org/wiki/Ecuador","https://en.wikipedia.org/wiki/Agust%C3%ADn_Delgado",2006)
    # r = get_player_data("https://en.wikipedia.org/wiki/Italy","https://en.wikipedia.org/wiki/Clint_Dempsey",2006)
    # print("AAAA")
    # print(r)
    # print("BBBB")

    soup = get_soup(stats_url)
    d = get_goals_num(soup)
    print('----------------------------------------')
    goals_dict = extract_dict_data(d)
    # pprint(goals_dict)
    goal_scorers = get_goal_scorers(goals_dict, 2021)

# TODO
# - posortowac dane w kolkach
# - dopasowac do copa america, serie a i innych lig
# - asysyty i samoboje
# - dodac pozycje
# - dodac wysokosc i grubosc
# - make 'Euro 2020 statistics' page header looking nicer
# - add unicode flag
# - fix colors in 'on-goal-scorers'
# - add menu at the top of the page
