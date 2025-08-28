from typing import Any, Mapping
from pymongo import MongoClient
from pymongo.cursor import Cursor


class Mongo:
    def __init__(self):
        self.db = MongoClient('mongodb://localhost:27017')['syndra']

        self.players = self.db['cl_players']
        self.matches = self.db['cl_players_matches']
        self.match_details = self.db['cl_matches_extended']

        self.t_cache = self.db['training_entries']

    def update_or_add_player(self, name: str, puuid: str, index: int, region: str, entry: dict) -> None:
        self.players.update_one(
            {'name': name},
            {'$set': {
                'suuid': entry['summonerId'],
                'puuid': puuid,
                'leaguePoints': entry['leaguePoints'],
                'wins': entry['wins'],
                'losses': entry['losses'],
                'leaderboardPosition': index,
                'region': region
            }},
            upsert=True
        )

    def update_or_add_match(self, match_id: str, name: str, region: str) -> None:
        self.matches.update_one(
            {'match_id': match_id},
            {
                '$addToSet': {'participants': name},
                '$set': {'region': region}
            },
            upsert=True
        )

    def update_or_add_match_details(self, match_id: str, teams: list, participants: list) -> None:
        self.match_details.update_one(
            {'match_id': match_id},
            {
                '$set': {
                    'participants': participants,
                    'teams': teams
                }
            },
            upsert=True
        )

    def get_all_matches(self) -> Cursor[Mapping[str, Any] | Any]:
        return self.matches.find()

    def get_all_training_entries_from_cache(self) -> list:
        return list(self.t_cache.find({}, {'_id': 0}))
