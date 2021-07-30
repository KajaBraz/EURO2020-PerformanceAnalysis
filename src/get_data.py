import json
import re
import requests
from bs4 import BeautifulSoup

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
p_national_team = re.compile(r'.?National team.?')
p_date_range = re.compile(r'\d{4}.*')


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html5lib')


def get_goals_num(soup: BeautifulSoup, achievement_type: str) -> {}:
    """
    :param soup: wiki page soup with a given competition statistics
    :param achievement_type: 'goals' or 'assists'
    :return: dictionary with the goals/assists numbers as keys and lists of html players elements
    """
    if achievement_type == 'goals':
        pattern = p_goals
    else:
        pattern = p_assist

    goals = {}
    body = soup.find('div', attrs={'class': 'mw-parser-output'})
    headlines = body.findAll('b', text=pattern)
    if sum([headline is not None and achievement_type[:-1] in headline.text for headline in headlines]) == 0:
        headlines = body.findAll('dt', text=p_goals)

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
    for s in name.find_all('style'):
        s.decompose()
    for s in name.find_all('span'):
        s.decompose()
    return ''.join([ch for ch in name.text if ch.isalpha() or ch == ' '])


def get_age(soup: BeautifulSoup, tournament_year: int) -> int:
    age_row = soup.find('th', text=p_birth_date_headline)
    birth_date = age_row.find_next_sibling('td').text
    return tournament_year - int(p_digit.search(birth_date).group())


def get_height(soup: BeautifulSoup) -> float:
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


def get_league_country(league_url: str) -> str:
    try:
        r = requests.get(league_url)
        soup = BeautifulSoup(r.content, 'html5lib')
        country_row = soup.find('th', text='Country')
        country = country_row.find_next_sibling('td').text
        country = p_parenthesis.sub('', country)
        return country.strip()
    except:
        return ''


def check_dates(dates_range_str: str, year: int) -> bool:
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


def cut_initial_chars(name: str) -> str:
    if name.strip() == "":
        return ""
    i = -1
    valid_start = False
    while not valid_start:
        i += 1
        valid_start = name[i].isalnum()
    return name[i:]


def get_team(soup: BeautifulSoup, tournament_year: int) -> (str, str):
    team, team_url = '', ''
    elem_after_teams = soup.find_all('th')
    elem_after_teams = [elem for elem in elem_after_teams if elem and p_national_team.search(elem.text)]
    th_elems = elem_after_teams[0].find_all_previous('th')
    for th in th_elems:
        date_range = th.text.strip()
        if p_date_range.search(date_range) and check_dates(date_range, tournament_year):
            team_elem = th.find_next_sibling('td')
            team = cut_initial_chars(p_parenthesis.sub('', team_elem.text.strip()))
            team_url = get_pure_url(team_elem.find('a', href=True)['href'])
            return team, team_url
    return team, team_url


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
    age = get_age(soup_player_table, tournament_year)
    height = get_height(soup_player_table)
    team, league = get_team_league(soup_player_table, tournament_year)
    nation = get_nation(soup_nation)
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


def get_assistants(assists_dictionary, tournament_year: int) -> ({str: {str}}):
    assistants_data = []
    for assists_num, assistants in assists_dictionary:
        for assistant in assistants:
            nation_url = assistant[0]
            assistant_url = assistant[1]
            assistant_dict = get_player_data(nation_url, assistant_url, tournament_year)
            assistant_dict['assists'] = assists_num
            print(assistant_dict)
            assistants_data.append(assistant_dict)
    return assistants_data


def save_json(filename: str, players_dictionary: {}):
    with open(filename, 'w') as players_file:
        data = json.dumps(players_dictionary)
        players_file.write('playerData = ')
        players_file.write(data)


if __name__ == '__main__':
    stats_url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2020_statistics'
    # stats_url = 'https://en.wikipedia.org/wiki/2006_FIFA_World_Cup_statistics'
    # stats_url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2012_statistics'

    soup_2021 = get_soup(stats_url)
    d = get_goals_num(soup_2021, 'goals')
    goals_dict = extract_dict_data(d)
    goal_scorers = get_goal_scorers(goals_dict, 2021)
    save_json('../js/data_2021.js', goal_scorers)

    d_a = get_goals_num(soup_2021, 'assists')
    goals_dict = extract_dict_data(d_a)
    goal_scorers = get_goal_scorers(goals_dict, 2021)
    save_json('../js/data_assists_2021.js', goal_scorers)

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
