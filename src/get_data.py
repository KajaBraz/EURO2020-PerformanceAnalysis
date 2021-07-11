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


def get_name(soup: BeautifulSoup) -> str:
    name = soup.find('h1', attrs={'id': 'firstHeading'}).text
    return ''.join([ch for ch in name if ch.isalpha() or ch == ' '])


def get_age(soup: BeautifulSoup) -> int:
    age = soup.find('span', attrs={'class': 'noprint ForceAgeToShow'}).text
    return int(p_digit.search(age).group())


def get_team_league(soup: BeautifulSoup) -> (str, str):
    try:
        team_element = soup.find('td', attrs={'class': 'org'}).find('a')
        team = team_element.text
        league_url = p_wiki.search(str(team_element))
        league_url = 'https://en.wikipedia.org' + league_url.group()[:-1]
        r = requests.get(league_url)
        soup_league = BeautifulSoup(r.content, 'html5lib')
        # table = soup_league.find('table', attrs={'class': 'infobox vcard'}).findAll('tr')
        # league = 'Unknown'
        # for row in table:
        #     row_content = row.find('th')
        #     if row_content:
        #         if row_content.text == 'League':
        #             league = row.find('td').text
        league = get_league(soup_league)
        return team, league
    except:
        return 'Unknown', 'Unknown'


def get_league_country(soup: BeautifulSoup):
    table = soup.find('table', attrs={'class': 'infobox'}).findAll('tr')
    country = 'Unknown'
    for row in table:
        row_content = row.find('th')
        if row_content:
            if row_content.text == 'Country':
                country = row.find('td').text
    country = re.sub(r'\(.+\)', '', country)
    return country.strip()


def get_league(soup: BeautifulSoup) -> str:
    table = soup.find('table', attrs={'class': 'infobox vcard'}).findAll('tr')
    league = 'Unknown'
    for row in table:
        row_content = row.find('th')
        if row_content:
            if row_content.text == 'League':
                league = row.find('td').text
    return league


def get_nation(soup: BeautifulSoup) -> str:
    nation = soup.find('h1', attrs={'id': 'firstHeading'}).text
    span = p_national.search(nation).span()
    return nation[:span[0]]


def get_player_data(url_nation: str, url_player: str) -> {}:
    r_nation = requests.get(url_nation)
    soup_nation = BeautifulSoup(r_nation.content, 'html5lib')
    r_player = requests.get(url_player)
    soup_player = BeautifulSoup(r_player.content, 'html5lib')
    name = get_name(soup_player)
    age = get_age(soup_player)
    team, league = get_team_league(soup_player)
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
            # print(player_dict)
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
    # url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2020_statistics'
    # names, headlines = get_lists(url)
    # gols_scored_headlined = get_scored_goals_headlines(headlines)
    # players_dict = get_goal_scorers(names, gols_scored_headlined)
    # save_json('js/data.js', players_dict)
    print('d'.isalpha())
    print(' '.isalpha())
    name = 'Nikola Vlašić'
    print(''.join([ch for ch in name if ch.isalpha() or ch == ' ']))

    r = requests.get('https://en.wikipedia.org/wiki/Ligue_1')
    s = BeautifulSoup(r.content, 'html5lib')
    print(get_league_country(s))

# TODO
# - doddac hithub pages
# - litery scipy
# - klub Pandeva
# - posortowac dane w kolkach
# - wybor czy usunac jedynki (gole w kolkach)
# - dodac panstwa do lig
# - wybor wykresu kolowy/slupkowy
# - naprawic legende undefined w slupkowym
# - dopasowac do copa america, serie a i innych lig
# - asysyty i samoboje
# - dodac pozycje
# - dodac wysokosc i grubosc
# - dadac klub z czasu turnieju (z czerwca)
