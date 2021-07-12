import json
import re
import requests
from bs4 import BeautifulSoup

p_url = re.compile(r'href=\S+')
p_wiki = re.compile(r'/wiki/\S+')
p_national = re.compile(r' national')
p_digit = re.compile(r'\d+')
p_goals = re.compile(r'\d+\sgoals?')


def get_lists(url: str) -> ([], []):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    names = soup.findAll('div', attrs={'class': 'div-col'})
    paragraphs = soup.findAll('p')
    headlines = [paragraph.find('b') for paragraph in paragraphs]
    return names, headlines


def get_name(soup_table: BeautifulSoup) -> str:
    name = soup_table.find('caption', attrs={'class': 'fn'})
    for s in name.find_all('style'):
        s.decompose()
    for s in name.find_all('span'):
        s.decompose()
    return ''.join([ch for ch in name.text if ch.isalpha() or ch == ' '])


def get_age(soup: BeautifulSoup) -> int:
    age = soup.find('span', attrs={'class': 'noprint ForceAgeToShow'}).text
    return int(p_digit.search(age).group())


def get_team_league(soup: BeautifulSoup) -> (str, str):
    try:
        team_element = soup.find('td', attrs={'class': 'org'}).find('a')
        team = team_element.text
        team_url = p_wiki.search(str(team_element))
        team_url = get_pure_url(team_url.group())
        r = requests.get(team_url)
        soup_league = BeautifulSoup(r.content, 'html5lib')
        league, league_url = get_league(soup_league)
        country = get_league_country(league_url)
        return team, f'{league} ({country})'
    except:
        return 'No club', 'No league'


def get_league_country(league_url: str):
    r = requests.get(league_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.find('table', attrs={'class': 'infobox'}).findAll('tr')
    country = '-'
    for row in table:
        row_content = row.find('th')
        if row_content:
            if row_content.text == 'Country':
                country = row.find('td').text
    country = re.sub(r'\(.+\)', '', country)
    return country.strip()


def get_league(soup: BeautifulSoup) -> (str, str):
    table = soup.find('table', attrs={'class': 'infobox vcard'}).findAll('tr')
    league, league_url = 'No club', '-'
    for row in table:
        row_content = row.find('th')
        if row_content:
            if row_content.text == 'League':
                league = row.find('td').text
                url_league_element = row.find('td').find('a')
                league_url = get_pure_url(p_wiki.search(str(url_league_element)).group())
    return league, league_url


def get_nation(soup: BeautifulSoup) -> str:
    nation = soup.find('h1', attrs={'id': 'firstHeading'}).text
    span = p_national.search(nation).span()
    return nation[:span[0]]


def get_player_data(url_nation: str, url_player: str) -> {}:
    r_nation = requests.get(url_nation)
    soup_nation = BeautifulSoup(r_nation.content, 'html5lib')
    r_player = requests.get(url_player)
    soup_player = BeautifulSoup(r_player.content, 'html5lib')
    soup_player_table = soup_player.find('table', attrs={'class': 'infobox vcard'})
    name = get_name(soup_player_table)
    age = get_age(soup_player_table)
    team, league = get_team_league(soup_player_table)
    nation = get_nation(soup_nation)
    player_data = {'name': name, 'age': age, 'club': team, 'league': league, 'country': nation}
    return player_data


def get_pure_url(url: str) -> str:
    html_base = 'https://en.wikipedia.org'
    main = p_wiki.search(url).group()
    return html_base + main[:-1]


def get_goal_scorers(names: [], scored_goals_headlines: []) -> {str: {str}}:
    players_urls = [p_url.findall(str(names[i])) for i in range(len(scored_goals_headlines))]

    players_data = []
    goals_num_ind = 0
    for players in players_urls:
        goals = scored_goals_headlines[goals_num_ind]
        players_num = len(players) // 2
        i = 0
        for player_ind in range(players_num):
            nation_url = get_pure_url(players[i])
            player_url = get_pure_url(players[i + 1])
            i += 2
            player_dict = get_player_data(nation_url, player_url)
            player_dict['goals'] = goals
            players_data.append(player_dict)
            print(player_dict)
        goals_num_ind += 1
    return players_data


def get_scored_goals_headlines(headlines: []) -> [str]:
    sorted_headlines = [p_goals.search(str(headline)) for headline in headlines]
    sorted_headlines = [headline.group() for headline in sorted_headlines if headline]
    return [int(re.search(r'\d', goals).group()) for goals in sorted_headlines]


def save_json(filename: str, players_dictionary: {}):
    with open(filename, 'w') as players_file:
        data = json.dumps(players_dictionary)
        players_file.write('playerData = ')
        players_file.write(data)


if __name__ == '__main__':
    stats_url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2020_statistics'
    players_names, goals_headlines = get_lists(stats_url)
    gols_scored_headlined = get_scored_goals_headlines(goals_headlines)
    players_dict = get_goal_scorers(players_names, gols_scored_headlined)
    save_json('../js/data.js', players_dict)

# TODO
# - klub Pandeva
# - posortowac dane w kolkach
# - wybor czy usunac jedynki (gole w kolkach)
# - wybor wykresu kolowy/slupkowy
# - dopasowac do copa america, serie a i innych lig
# - asysyty i samoboje
# - dodac pozycje
# - dodac wysokosc i grubosc
# - dadac klub z czasu turnieju (z czerwca)
# - make 'Euro 2020 statistics' page header looking nicer
# - add unicode flag
