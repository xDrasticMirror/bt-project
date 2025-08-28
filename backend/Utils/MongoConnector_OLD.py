from pymongo import MongoClient
from pymongo.cursor import Cursor

from LeagueModel.Syndra.API.MongoDB.MongoUtils import *
from LeagueModel.Syndra.Utils.Utils import Utils

class MongoConnector:
    def __init__(self):
        self.db = MongoClient('mongodb://localhost:27017')['syndra']

        # Cache related databases
        self.t_cache = self.db['training_entries']
        self.as_cache = self.db['advanced_stats']
        self.u_cache = self.db['utils_cache']
        self.s_cache = self.db['stat_cache']
        self.p_cache = self.db['pro_cache']

        # self.fix_mundo()

    def fix_mundo(self):
        affected_entries = self.db['stat_cache'].find({
            'champions.Dr': {"$exists": True}
        })

        for entry in affected_entries:
            if " Mundo" in entry['champions']['Dr']:
                entry['champions']['Dr. Mundo'] = {
                    'assists': entry['champions']['Dr'][' Mundo']['assists'],
                    'kills': entry['champions']['Dr'][' Mundo']['kills'],
                    'deaths': entry['champions']['Dr'][' Mundo']['deaths'],
                    'games_played': entry['champions']['Dr'][' Mundo']['games_played'],
                    'winrate': entry['champions']['Dr']['winrate'],
                    'wins': entry['champions']['Dr'][' Mundo']['wins']
                }

                del entry['champions']['Dr']

                self.db['stat_cache'].update_one(
                    {'_id': entry['_id']},
                    {'$set': {'champions': entry['champions']}}
                )

    def get_all_matches(self) -> Cursor[list]:
        return self.db['pro_cache'].find()

    def get_all_matches_from_year(self, year: str) -> Cursor[list]:
        return self.db['pro_cache'].find({
            'date': {'$regex': f'^{year}', '$options': 'i'}
        })

    def get_games_played_from_player(self, player: str) -> int:
        return int(self.db['stat_cache'].find({
            '_id': player
        })[0]['games_played'])

    def get_player_winrate(self, player: str):
        return self.db['stat_cache'].find({
            '_id': player
        })[0]['overall_winrate']

    def get_player_champion_winrate(self, player: str, champion: str):
        try:
            return self.db['stat_cache'].find({
                'name': player
            })[0]['champions'][champion]['winrate']
        except KeyError:
            return 0

    def get_last_match_from_team(self, team: str) -> dict:
        return list(self.p_cache.find({
            "$or": [
                {"Blue.teamname": team},
                {"Red.teamname": team}
            ]
        }).sort("date", -1).limit(1))[0]

    def get_last_listed_players(self, team: str) -> list:
        last_match = self.get_last_match_from_team(team=team)
        return [last_match['Blue' if last_match['Blue']['teamname'] == team else 'Red'][pos]['name'] for pos in Utils.positions]

    def get_last_players(self, team: str) -> list:
        last_match = list(self.db['pro_cache'].find(
            {
                "$or": [
                    {"Blue.teamname": team},
                    {"Red.teamname": team}
                ]
            }
        ).sort("date", -1).limit(1))

        players = []
        side = 'Blue' if last_match[0]['Blue']['teamname'] == team else 'Red'
        for pos in Utils.positions:
            players.append(last_match[0][side][pos]['name'])

        return players

    def _get_items_for_entry(self, player_name: str, champion_name: str) -> tuple:
        items = self.s_cache.find({'_id': player_name}, {
            f'champions.{champion_name}.winrate': 1,
            'games_played': 1,
            'overall_winrate': 1
        })[0]

        try:
            return items['champions'][champion_name]['winrate'], items['games_played'], items['overall_winrate']
        except KeyError:
            return 0, items['games_played'], items['overall_winrate']

    def get_all_training_entries_from_cache(self) -> list:
        return list(self.t_cache.find({}, {'_id': 0}))

    def get_available_leagues(self) -> set[str]:
        leagues = set()
        for doc in self.u_cache.find({}, {"_id": 0}):
            for league, years in doc.items():
                if isinstance(years, dict) and "2025" in years:
                    leagues.add(league)
        return leagues

    def get_teams_in_league(self, league: str, year: str = '2025') -> list:
        return list(self.u_cache.find({})[0][league][year])
