import asyncio
import json
import time

from playwright.async_api import async_playwright, Playwright


async def get_page(playwright: Playwright, headless):
    chromium = playwright.chromium
    browser = await chromium.launch(headless=headless)
    page = await browser.new_page()
    return page


async def get_national_teams(page, link):
    await page.goto(link)

    national_team_class = 'tableCellParticipant__name'
    national_teams = await page.locator(f'.{national_team_class}').all()
    national_teams_data = {await team.inner_text(): await team.get_attribute('href') for team in national_teams}
    return national_teams_data


async def get_teams_players(page, link):
    await page.goto(link)
    player_row_class = 'lineupTable__row'
    player_name_class = 'lineupTable__cell--name'
    player_flag_class = 'lineupTable__cell--flag'

    players = await page.locator(f'.{player_row_class}').all()
    players_data = {await player.locator(f'.{player_name_class}').inner_text(): player.locator(f'.{player_flag_class}')
                    for player in players}
    players_data = {player.strip(): club.first for player, club in players_data.items()}
    players_data = {player: await club.get_attribute('title') for player, club in players_data.items()}
    return players_data


def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def main():
    headless = True
    euro_link = 'https://www.flashscore.com/football/europe/euro/standings/#/EcpQtcVi/table'
    async with async_playwright() as playwright:
        page = await get_page(playwright, headless)
        national_teams = await get_national_teams(page, euro_link)
        teams_data = {}
        for team, code in national_teams.items():
            time.sleep(1)
            team_players_link = f'https://www.flashscore.com{code}squad/'
            team_players = await get_teams_players(page, team_players_link)
            teams_data[team] = team_players

        save_data(teams_data)


if __name__ == '__main__':
    asyncio.run(main())
