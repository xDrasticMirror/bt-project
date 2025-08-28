from LeagueModel.Syndra.Utils.Utils import Utils
from pymongo import DESCENDING

class GeneralUtils:
    def __init__(self, mongo_mgr):
        self.mgr = mongo_mgr

    def get_match_count(self):
        return self.mgr.p_db.count_documents({})

    def get_player_count(self):
        return self.mgr.s_db.count_documents({})

    def get_team_count(self):
        return self.mgr.team_cache.count_documents({})

    def get_match_count_from_year(self, year=2025):
        return self.mgr.p_db.count_documents({
            "date": {
                "$gte": f"{year}-01-01",
                "$lte": f"{year}-12-31"
            }
        })

    def convert_dates(self):
        self.mgr.p_db.update_many(
            {},
            [{'$set': {'date': {'$toDate': '$date'}}}]
        )
        self.mgr.p_db.create_index([('date', DESCENDING)])

    def get_player_training_entry_items(self, p: str):
        return self.mgr.s_db.find(
            {'_id': p},
            {'_id': 0, 'overall_winrate': 1, 'wins': 1, 'games_played': 1, 'champions': 1}
        )

    def prediction_uid(self, prediction_data: dict):
        """ Calculate the prediction unique identifier to be used as an index """
        uid = prediction_data['blue']['teamname'][0:3] + '_B_' + prediction_data['red']['teamname'][0:3] + '_R_'
        for side in ['blue', 'red']:
            for p, c in zip(prediction_data[side]['players'], prediction_data[side]['champions']):
                uid += p[0:2] + c[0:2] + "_"
        return uid

    def get_prediction(self, prediction_data: dict):
        """ Return a cached prediction if found """
        return self.mgr.pr_db.find_one({"_id": self.prediction_uid(prediction_data=prediction_data)})

    def save_prediction_to_cache(self, prediction_data: dict):
        """ Save a prediction to the cache """
        self.mgr.pr_db.update_one(
            {'_id': self.prediction_uid(prediction_data=prediction_data)},
            {'$set': prediction_data},
            upsert=True
        )

    def get_training_entries_from_cache(self) -> list[dict]:
        """Returns a list[dict] with the training entries already properly formated"""
        return list(self.mgr.t_cache.find(
            {},
            {'_id': 0}
        ))

    def get_teams_in_league(self, league: str, year: str = '2025') -> list:
        """Returns a list[str] that contains all teams that play in the given league"""
        return list(self.mgr.u_db.find(
            {},
            {f'{league}.{year}': 1}
        )[0][league][year])

    def get_available_leagues(self) -> set[str]:
        """Returns a set[str] with all available leagues that have current year entries"""
        leagues = set()
        for doc in self.mgr.u_db.find({}, {"_id": 0}):
            for league, years in doc.items():
                if isinstance(years, dict) and "2025" in years:
                    leagues.add(league)
        return leagues

    def insert_new_advanced_stats(self, stat_obj: dict) -> None:
        """Inserts a new advanced stats object"""
        self.mgr.as_db.insert_one(stat_obj)

    def check_if_astats_saved(self, player: str) -> bool:
        """Check if a player's advanced stats have been saved or not"""
        try:
            name = self.mgr.as_db.find_one(
                {'name': player}
            )['name']
            return True
        except TypeError:
            return False

    def clear_incomplete_matches(self) -> None:
        """Removes all matches that contain 'unknown player' as it makes no sense to index them"""
        for match in self.mgr.get_all_matches():
            pBlue, pRed = Utils.get_players_by_side(match=match)
            m_id = match['match_id']

            for players in pBlue, pRed:
                for player in players:
                    if player == 'unknown player':
                        self.mgr.p_db.delete_one({'match_id': m_id})
                        print(f'[INFO] removed {m_id} - found unknown player')

    def clear_unknown_user(self) -> None:
        """Removes 'unknown player' from the database as its not a valid player"""
        self.mgr.s_db.delete_one(
            {'name': 'unknown player'}
        )

    def fix_mundo(self) -> None:
        """Fixes malformed Dr. Mundo entries in player champion stats."""
        affected_entries = self.mgr.s_db.find({
            'champions.Dr': {"$exists": True}
        })

        for entry in affected_entries:
            champions = entry.get('champions', {})
            dr_entry = champions.get('Dr', {})

            if isinstance(dr_entry, dict) and ' Mundo' in dr_entry:
                mundo_data = dr_entry[' Mundo']
                winrate = dr_entry.get('winrate')

                champions['Dr. Mundo'] = {
                    **mundo_data,
                    **({'winrate': winrate} if winrate is not None else {})
                }

                del champions['Dr']
                self.mgr.s_db.update_one(
                    {'_id': entry['_id']},
                    {'$set': {'champions': champions}}
                )
