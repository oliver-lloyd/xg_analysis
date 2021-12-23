import asyncio
import aiohttp
import argparse
import pandas as pd

from pathlib import Path
from understat import Understat
from ast import literal_eval


async def get_match_results(year, league):
    """
    Gets match results from Understat API using the PyPI package.
    Function is modified from package documentation.
    """

    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        league_results = await understat.get_league_results(
            league,
            year
        )

        return league_results


def strip_match_info(match_dict):
    info = {
        'home_team': match_dict['h']['title'],
        'home_goals': match_dict['goals']['h'],
        'home_xg': match_dict['xG']['h'],

        'away_team': match_dict['a']['title'],
        'away_goals': match_dict['goals']['a'],
        'away_xg': match_dict['xG']['a']
    }

    return info


if __name__ == '__main__':

    # Get user args for leagues and years
    parser = argparse.ArgumentParser()
    parser.add_argument('leagues', type=str, nargs='+')
    parser.add_argument('years', type=int, nargs='+')
    args = parser.parse_args()

    # Get data from Understat API
    loop = asyncio.get_event_loop()
    for league_name in args.leagues:
        for year_int in range(min(args.years), max(args.years) + 1):
            data_raw = loop.run_until_complete(
                get_match_results(year_int, league_name)
            )

            # Process and save
            data = pd.DataFrame(
                [strip_match_info(match) for match in data_raw]
            )
            dir_name = f'data/{league_name}/'
            path = Path(dir_name).mkdir(parents=True, exist_ok=True)
            data.to_csv(dir_name + f'/{year_int}.csv', index=False)

    # TODO: parallelise loops above with asyncio
