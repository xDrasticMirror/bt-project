from datetime import datetime
from pymongo import MongoClient
from pymongo.results import UpdateResult, InsertOneResult
from tqdm import tqdm
from enum import Enum

from LeagueModel.Syndra.API.MongoDB.Cache.Formatters import MatchFormatter
from LeagueModel.Syndra.API.MongoDB.Cache.Formatters.PlayerFormatter import PlayerFormatter
from LeagueModel.Syndra.API.MongoDB.Cache.Formatters.TeamFormatter import TeamFormatter
from LeagueModel.Syndra.API.MongoDB.Cache.Formatters.TrainingEntryFormatter import TEFormatter
from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Utils.Utils import Utils

import csv
import logging
import hashlib

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

db = MongoClient('mongodb://localhost:27017')['syndra']
mgr = MongoManager()

class CacheCollections(Enum):
    PLAYER_CACHE = db['stat_cache']
    MATCH_CACHE = db['pro_cache']
    UTILS_CACHE = db['utils_cache']
    TRAINING_ENTRIES_CACHE = db['training_entries']
    TEAM_STATS_CACHE = db['teamStatistics']


class CacheUpdateMode(Enum):
    UPDATE_ALL = 1
    UPDATE_ONLY_PRO_PLAYERS = 2
    UPDATE_ONLY_TRAINING_ENTRIES = 3
    UPDATE_ONLY_MATCHES = 4
    UPDATE_ONLY_TEAMS = 5


class MongoCache(Utils):
    def __init__(self):
        super().__init__()

        self.db = MongoClient('mongodb://localhost:27017')['syndra']
        self.mgr = MongoManager()

        # self.save_teams()
        # self.save_players()
        # self.build_cache(CacheUpdateMode.UPDATE_ONLY_TEAMS)

    def build_cache(self, config: CacheUpdateMode) -> None:
        actions = {
            CacheUpdateMode.UPDATE_ALL: self.update_all,
            CacheUpdateMode.UPDATE_ONLY_TEAMS: self.save_teams,
            CacheUpdateMode.UPDATE_ONLY_PRO_PLAYERS: self.save_players,
            CacheUpdateMode.UPDATE_ONLY_MATCHES: lambda: self.save_all_matches(s_training_entries=False),
            CacheUpdateMode.UPDATE_ONLY_TRAINING_ENTRIES: lambda: self.save_all_matches(s_training_entries=True)
        }
        update_fn = actions.get(config)
        update_fn()
        self.mgr.fix_mundo()

    def update_all(self) -> None:
        self.save_all_matches(s_training_entries=False)
        self.save_players()
        self.save_all_matches(s_training_entries=True)
        self.save_teams()

    def save_teams(self) -> None:
        all_teams = self.mgr.get_all_teams()
        with tqdm(all_teams, desc='Saving teams...') as pbar:
            for team in all_teams:
                pbar.set_description(f'SAVING {team}'.ljust(50))
                CacheCollections.TEAM_STATS_CACHE.value.update_one(
                    {'_id': team},
                    {'$set': TeamFormatter(teamname=team, mgr_instance=self.mgr).formatted_team},
                    upsert=True
                )
                pbar.update(1)
            pbar.set_description('TEAM UPDATE - FINISHED'.ljust(50))

    def save_players(self) -> None:
        all_players = self.mgr.get_all_players()
        with tqdm(all_players, desc='Saving players...') as pbar:
            for player in all_players:
                p_name = player['playername']
                pbar.set_description(f'SAVING {p_name}'.ljust(50))
                CacheCollections.PLAYER_CACHE.value.update_one(
                    {'_id': p_name},
                    {'$set': PlayerFormatter().format_player(p_name=p_name, matches=self.mgr.get_all_matches_from_player(player=p_name))},
                    upsert=True
                )
                pbar.update(1)
            pbar.set_description('PLAYER UPDATE - FINISHED'.ljust(50))

    def unkown_player_check(self, b: list[dict], r: list[dict]) -> bool:
        for item in b + r:
            if item['playername'] == 'unknown player':
                return True
        return False

    def series(self) -> None:
        byYear = dict()

        for year in range(2014, 2026):
            if year not in byYear.keys():
                byYear[year] = None

            with open(file=f'G:/ExcelProject/{year}.csv', newline="", encoding="utf-8-sig") as csvf:
                reader = list(csv.DictReader(csvf))
                flist = dict()
                matches = len(reader) // 12
                match = list()
                index = 0

                with tqdm(total=matches, desc=f'[{index}/{matches}] Running through all matches, trying to find series...', leave=True) as pbar:
                    for row in reader:
                        match.append(row)

                        if len(match) == 12:
                            sorted_teams = sorted([
                                match[10]['teamname'].strip().lower(),
                                match[11]['teamname'].strip().lower(),
                                datetime.strptime(match[11]['date'].lower().strip(), "%Y-%m-%d %H:%M:%S").date().isoformat()
                            ])

                            s = f'{sorted_teams[2]}{sorted_teams[0]}{sorted_teams[1]}'
                            h = hashlib.md5(s.encode()).hexdigest()

                            if h not in flist.keys():
                                flist[h] = list()

                            index += 1
                            flist[h].append(match.copy())

                            match.clear()
                            pbar.update(1)

                byYear[year] = flist.copy()
        print(byYear[2020])

    def save_all_matches(self, s_training_entries: bool = True) -> None:
        """
            Runs through all per year .csv's and indexes the matches within them. When calling save_pro_match, it will
            also format and save what would be the match training entry for later training of the model.
            :return: None
        """
        for year in range(2014, 2026):
            with open(file=f'G:/ExcelProject/{year}.csv', newline="", encoding="utf-8-sig") as csvfile:
                reader = list(csv.DictReader(csvfile))
                t_matches = len(reader) // 12
                current_match, match_index = list(), 0

                with tqdm(total=t_matches, desc=f'{"SAVING_MATCHES_ONLY "+str(year) if not s_training_entries else "SAVING_TRAINING_ENTRIES "+str(year)}', leave=False) as pbar:
                    for row in reader:
                        current_match.append(row)
                        if len(current_match) == 12:
                            match_index += 1

                            if not self.unkown_player_check(b=[*current_match[:5]], r=[*current_match[5:10]]):
                                self.save_match(
                                    blue_rows=[*current_match[:5], current_match[10]],
                                    red_rows=[*current_match[5:10], current_match[11]],
                                    save_training_entry=s_training_entries
                                )

                            current_match.clear()
                            pbar.update(1)


    def save_match(self, blue_rows: list, red_rows: list, save_training_entry: bool = True) -> None:
        gid, year = blue_rows[0]['gameid'], blue_rows[0]['year']

        match = MatchFormatter.format_match(blue_rows=blue_rows, red_rows=red_rows)
        result = self.save_match_entry(match=match)

        if save_training_entry:
            self.save_training_entry(match=match)

    def save_match_entry(self, match: dict) -> UpdateResult:
        return CacheCollections.MATCH_CACHE.value.update_one(
            {'_id': match['gameid']},
            {'$set': match},
            upsert=True
        )

    def save_training_entry(self, match: dict) -> InsertOneResult:
        if not CacheCollections.TRAINING_ENTRIES_CACHE.value.find_one({'_id': match['gameid']}):
            # NOTE: Must be insert_one because with update_one does not conserve the correct dict entry order
            return CacheCollections.TRAINING_ENTRIES_CACHE.value.insert_one(
                TEFormatter(match=match, mgr=self.mgr).format_entry()
            )
        return None

    def save_utils(self, league: str, teamname: str, date: str) -> None:
        """Save all available leagues and the names of the teams playing in them each year"""
        CacheCollections.UTILS_CACHE.value.update_one(
            {},
            {"$addToSet": {
                "available_leagues": league,
                f"{league}.{date[0:4]}": teamname
            }},
            upsert=True
        )