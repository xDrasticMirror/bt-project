from LeagueModel.Syndra.API.MongoDB.CollectionAPIs.PlayerCollection import PlayerUtils
from LeagueModel.Syndra.API.MongoDB.CollectionAPIs.TeamCollection import TeamUtils
from LeagueModel.Syndra.API.MongoDB.CollectionAPIs.GeneralCollection import GeneralUtils
from LeagueModel.Syndra.API.MongoDB.CollectionAPIs.MatchCollection import MatchUtils

from pymongo import MongoClient


class MongoManager(PlayerUtils, TeamUtils, GeneralUtils, MatchUtils):
    def __init__(self):
        super().__init__(mongo_mgr=self)
        self.mongo_conn = MongoClient('mongodb://localhost:27017')['syndra']

        self.p_db = self.mongo_conn['pro_cache']
        self.s_db = self.mongo_conn['stat_cache']
        self.u_db = self.mongo_conn['utils_cache']
        self.as_db = self.mongo_conn['advanced_stats']
        self.te_db = self.mongo_conn['training_entries']
        self.pr_db = self.mongo_conn['prediction_cache']
        self.team_cache = self.mongo_conn['teamStatistics']

    def clean_databases(self) -> None:
        """Clean databases from incorrect or incomplete data"""
        self.clear_incomplete_matches()
        self.clear_unknown_user()
