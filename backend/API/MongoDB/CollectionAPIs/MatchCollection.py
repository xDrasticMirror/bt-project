from LeagueModel.Syndra.API.MongoDB.MongoUtils import _all_matches_from_player_query
from datetime import datetime

class MatchUtils:
    def __init__(self, mongo_mgr):
        self.mgr = mongo_mgr

    def get_matches_from_player_from_year(self, player: str, year: str = '2025') -> list:
        """Returns a list[dict] with all matches from a player from a given year"""
        return [match for match in self.get_all_matches_from_player(player=player) if year in match['date']]

    def get_matches_from_team_from_year(self, team: str, year: str = '2025') -> list:
        """Returns a list[dict] with all matches from a team from a given year"""
        return [match for match in self.get_all_matches_from_team(teamname=team) if year in match['date']]

    def get_all_matches_from_year(self, year: str = '2025') -> list[dict]:
        """Returns a list[dict] with all matches played in a given year"""
        return list(self.mgr.p_db.find({
            'date': {'$regex': f'^{year}', '$options': 'i'}
        }))

    def get_all_matches(self) -> list[dict]:
        """Returns a list with all saved matches"""
        return list(self.mgr.p_db.find({}))

    def get_all_matches_from_player(self, player: str) -> list[dict]:
        """Returns a list[dict] with all the matches played by the given player"""
        return list(self.mgr.p_db.aggregate(_all_matches_from_player_query(_playername=player)))

    def get_all_matches_from_team(self, teamname: str) -> list[dict]:
        """Returns a list[dict] with all the matches played by the given team"""
        return list(self.mgr.p_db.find({
            "$or": [
                {"Blue.teamname": teamname},
                {"Red.teamname": teamname}
            ]
        }))

    def get_last_match_from_team(self, teamname: str) -> list[dict]:
        """Returns the last match played by a given team"""
        return self.get_last_ten_matches_from_team(teamname=teamname)

    def get_last_ten_matches_from_team(self, teamname: str) -> list[dict]:
        """Returns the last ten matches played by a given team"""
        return list(self.mgr.p_db.find({
            "$or": [
                {"Blue.teamname": teamname},
                {"Red.teamname": teamname}
            ]
        }).sort("date", -1).limit(10))[0]

    def get_blueside_games_from_team(self, teamname: str) -> list[dict]:
        """Gets all blueside games from a given team"""
        return list(self.mgr.p_db.find({
            "Blue.teamname": teamname
        }))

    def get_redside_games_from_team(self, teamname: str) -> list[dict]:
        """Gets all redside games from a given team"""
        return list(self.mgr.p_db.find({
            "Red.teamname": teamname
        }))

    def player_query(self, p: str) -> dict:
        return {
            "$or": [
                {"Blue.top.name": p},
                {"Blue.jng.name": p},
                {"Blue.mid.name": p},
                {"Blue.bot.name": p},
                {"Blue.sup.name": p},
                {"Red.top.name": p},
                {"Red.jng.name": p},
                {"Red.mid.name": p},
                {"Red.bot.name": p},
                {"Red.sup.name": p}
            ]
        }

    def get_last_ten_matches_from_date_by_player(self, p: str, before_date: str) -> list[dict]:
        date_obj = datetime.strptime(before_date, "%Y-%m-%d %H:%M:%S")
        cursor = self.mgr.p_db.find(
            {
                "$and": [
                    self.player_query(p=p),
                    {"date": {"$lt": date_obj}}
                ]
            },
            projection={"_id": 0}
        ).sort("date", -1).limit(10)
        return list(cursor)

    def get_last_ten_matches_from_date_by_team(self, teamname: str, before_date: str) -> list[dict]:
        date_obj = datetime.strptime(before_date, "%Y-%m-%d %H:%M:%S")
        cursor = self.mgr.p_db.find(
            {
                "$and": [
                    {"$or": [
                        {"Blue.teamname": teamname},
                        {"Red.teamname": teamname}
                    ]},
                    {"date": {"$lt": date_obj}}
                ]
            },
            projection={"_id": 0}
        ).sort("date", -1).limit(10)
        return list(cursor)
