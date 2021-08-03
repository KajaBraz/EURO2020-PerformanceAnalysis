import get_data
import requests
from bs4 import BeautifulSoup


def create_soup(url):
    r_player = requests.get(url)
    soup_player = BeautifulSoup(r_player.content, 'html5lib')
    return soup_player.find('table', attrs={'class': 'infobox vcard'})


def test_gavranovic_get_senior_career_trs():
    soup_player_table = create_soup('https://en.wikipedia.org/wiki/Mario_Gavranovi%C4%87')

    result = get_data.get_senior_career_trs(soup_player_table)

    assert len(result) == 9
    assert 'Lugano' in result[0].text
    assert '2006' in result[0].text
    assert '2008' in result[0].text
    assert '21' in result[0].text
    assert 'Schalke' in result[3].text
    assert 'Dinamo Zagreb' in result[8].text


def test_harry_kane_get_senior_career_trs():
    soup_player_table = create_soup('https://en.wikipedia.org/wiki/Harry_Kane')

    result = get_data.get_senior_career_trs(soup_player_table)

    assert len(result) == 5
    assert 'Tottenham' in result[0].text
    assert '2009' in result[0].text
    assert '242' in result[0].text
    assert 'Millwall' in result[2].text
    assert 'Leicester' in result[4].text


def test_get_team_kuba():
    helper_get_team_test(get_data.get_team_kuba)


def test_get_team_kaja():
    helper_get_team_test(get_data.get_team)


def helper_get_team_test(get_team_function):
    soup = create_soup('https://en.wikipedia.org/wiki/Harry_Kane')
    team, url = get_team_function(soup, 2020)
    assert url == 'https://en.wikipedia.org/wiki/Tottenham_Hotspur_F.C.'
    assert team == 'Tottenham Hotspur F.C.'

    team, url = get_team_function(soup, 2011)
    assert url == 'https://en.wikipedia.org/wiki/Leyton_Orient_F.C.'
    assert team == 'Leyton Orient F.C.'

    team, url = get_team_function(soup, 2012)
    assert url == 'https://en.wikipedia.org/wiki/Millwall_F.C.'
    assert team == 'Millwall F.C.'

    team, url = get_team_function(soup, 2013)
    assert url == 'https://en.wikipedia.org/wiki/Leicester_City_F.C.'
    assert team == 'Leicester City F.C.'

    soup = create_soup('https://en.wikipedia.org/wiki/%C3%81lvaro_Morata')
    team, url = get_team_function(soup, 2020)
    assert url == 'https://en.wikipedia.org/wiki/Atl%C3%A9tico_Madrid'
    assert team == 'Atlético Madrid'

    team, url = get_team_function(soup, 2021)
    assert url == 'https://en.wikipedia.org/wiki/Juventus_F.C.'
    assert team == 'Juventus F.C.'

    soup = create_soup('https://en.wikipedia.org/wiki/Federico_Chiesa')
    team, url = get_team_function(soup, 2021)
    assert url == 'https://en.wikipedia.org/wiki/Juventus_F.C.'
    assert team == 'Juventus F.C.'

    soup = create_soup('https://en.wikipedia.org/wiki/Mario_Gavranovi%C4%87')
    team, url = get_team_function(soup, 2021)
    assert url == 'https://en.wikipedia.org/wiki/GNK_Dinamo_Zagreb'
    assert team == 'GNK Dinamo Zagreb'

    soup = create_soup('https://en.wikipedia.org/wiki/Goran_Pandev')
    team, url = get_team_function(soup, 2021)
    assert url == 'https://en.wikipedia.org/wiki/Genoa_C.F.C.'
    assert team == 'Genoa C.F.C.'

    team, url = get_team_function(soup, 2022)
    assert url == ''
    assert team == ''

    soup = create_soup('https://en.wikipedia.org/wiki/Martin_Braithwaite')
    team, url = get_team_function(soup, 2021)
    assert url == 'https://en.wikipedia.org/wiki/FC_Barcelona'
    assert team == 'FC Barcelona'
