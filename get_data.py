import re
from pprint import pprint

from bs4 import BeautifulSoup
import urllib3
import requests

p_url = re.compile(r'href=\S+')
p_wiki = re.compile(r'/wiki/\S+')
p_national = re.compile(r' national')
p_word_chars = re.compile(r'[^a-zA-Z\s]')
p_digit = re.compile(r'\d+')
p_goals = re.compile(r'\d+\sgoals?')


def get_lists(url: str) -> ([], []):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    names = soup.findAll('div', attrs={'class': 'div-col'})
    # pprint(len(names))
    paragraphs = soup.findAll('p')
    # pprint(headlines)
    headlines = [paragraph.find('b') for paragraph in paragraphs]
    # pprint(headlines)
    return names, headlines


def get_name(soup: BeautifulSoup) -> str:
    name = soup.find('td', attrs={'class': 'nickname'}).text
    return p_word_chars.sub('', name)


def get_age(soup: BeautifulSoup) -> int:
    age = soup.find('span', attrs={'class': 'noprint ForceAgeToShow'}).text
    return int(p_digit.search(age).group())


def get_team_league(soup: BeautifulSoup) -> (str, str):
    team_element = soup.find('td', attrs={'class': 'org'}).find('a')
    team = team_element.text
    league_url = p_wiki.search(str(team_element))
    league_url = 'https://en.wikipedia.org' + league_url.group()[:-1]
    r = requests.get(league_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    league = soup.findAll('td', attrs={'class': 'infobox-data'})
    league = league[8].text
    print(league)
    return team, league


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
    player_data = {'name': name, 'age': age, 'club': team, 'country': nation}
    return player_data


def get_pure_url(url: str) -> str:
    html_base = 'https://en.wikipedia.org'
    main = p_wiki.search(url).group()
    return html_base + main[:-1]


def get_goal_scorers(names: [], scored_goals_headlines: []) -> {str: {str}}:
    players_urls = [p_url.findall(str(names[i])) for i in range(len(scored_goals_headlines))]
    print(players_urls)
    print(scored_goals_headlines)

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
            print('url', nation_url, player_url)
            player_dict = get_player_data(nation_url, player_url)
            player_dict['goals'] = goals
            players_data.append(player_dict)
            print(player_dict)
            # print(players_data)
        goals_num_ind += 1


def get_scored_goals_headlines(headlines: []) -> [str]:
    sorted_headlines = [p_goals.search(str(headline)) for headline in headlines]
    sorted_headlines = [headline.group() for headline in sorted_headlines if headline]
    # pprint(sorted_headlines)
    return [int(re.search(r'\d', goals).group()) for goals in sorted_headlines]


if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2020_statistics'
    names, headlines = get_lists(url)
    # pprint(headlines)
    gols_scored_headlined = get_scored_goals_headlines(headlines)
    get_goal_scorers(names, gols_scored_headlined)
    # get_player_data('https://en.wikipedia.org/wiki/Italy_national_football_team','https://en.wikipedia.org/wiki/Lorenzo_Insigne')
