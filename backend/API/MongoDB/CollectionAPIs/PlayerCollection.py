class PlayerUtils:
    def __init__(self, mongo_mgr):
        self.mgr = mongo_mgr

    def get_specific_player(self, player: str) -> dict:
        """Returns a player object that matches the playername given"""
        return self.mgr.p_db.find(
            {'_id': player}
        )

    def playerlist(self) -> list:
        return [
            {
                "$project": {
                    "blue_players": [
                        "$Blue.top.name",
                        "$Blue.jng.name",
                        "$Blue.mid.name",
                        "$Blue.bot.name",
                        "$Blue.sup.name"
                    ],
                    "red_players": [
                        "$Red.top.name",
                        "$Red.jng.name",
                        "$Red.mid.name",
                        "$Red.bot.name",
                        "$Red.sup.name"
                    ]
                }
            },
            {
                "$project": {
                    "all_players": {
                        "$concatArrays": ["$blue_players", "$red_players"]
                    }
                }
            },
            {
                "$unwind": "$all_players"
            },
            {
                "$group": {
                    "_id": "$all_players"
                }
            },
            {
                "$project": {
                    "playername": "$_id",
                    "_id": 0
                }
            }
        ]

    def get_all_players(self) -> list:
        """Returns a list that contains the username of all saved players"""
        return list(self.mgr.p_db.aggregate(self.playerlist()))

    def get_player_kda(self, player: str) -> dict:
        """Returns the KDA from a specific player"""
        return self.mgr.s_db.find(
            {'_id': player},
            {'_id': 0, 'kills': 1, 'deaths': 1, 'assists': 1}
        )[0]

    def get_player_champion_list(self, player: str) -> list:
        items = self.mgr.s_db.find(
            {'_id': player},
            {'_id': 0, 'champions': 1}
        )[0]['champions'].keys()
        return list(items)

    def get_player_champion_wl(self, player: str, champion: str) -> list:
        items = self.mgr.s_db.find(
            {'_id': player},
            {'_id': 0, f'champions.{champion}': 1}
        )
        return items

    def get_player_won_lost(self, player: str) -> tuple[int, int, int]:
        """Returns the wins, loses and games played by a specific player"""
        try:
            items = self.mgr.s_db.find(
                {'_id': player},
                {'wins': 1, 'games_played': 1}
            )[0]
            return items['wins'], items['games_played'] - items['wins'], items['games_played']
        except IndexError:
            return 0, 0, 0

    def get_games_played_by_champion(self, player: str, champion: str) -> int:
        """Returns the amount of games a player has played with a given champion"""
        try:
            return self.mgr.s_db.find(
                {'_id': player},
                {'_id': 0, 'champions': 1}
            )[0]['champions'][champion]['games_played']
        except KeyError:
            return 0
        except IndexError:
            return 0

    def get_champion_kda(self, player: str, champion: str) -> float:
        """Returns the champion KDA"""
        _champion = None
        try:
            _champion = self.mgr.s_db.find(
                {'_id': player},
                {'_id': 0, 'champions': 1}
            )[0]['champions'][champion]

            # K + A / D - if D != 0
            return round(((_champion['kills']+_champion['assists'])/_champion['deaths']), 2)
        except ZeroDivisionError:
            # K + A - if D == 0
            return _champion['kills']+_champion['assists']
        except KeyError:
            return 0
        except IndexError:
            return 0

    def get_player_items(self, player: str, champion_name: str) -> dict:
        return {
            'ch_kda': self.get_champion_kda(player=player, champion=champion_name),
            'ch_wr': self.get_player_champion_specific_winrate(player=player, champion=champion_name),
            'ch_gp': self.get_games_played_by_champion(player=player, champion=champion_name),
            'oa_gp': self.get_player_won_lost(player=player)[2],
            'oa_wr': self.get_player_overall_winrate(player=player)
        }

    def get_player_overall_winrate(self, player: str) -> float:
        """Returns the overall_winrate from a specific player"""
        return round(self.mgr.s_db.find(
            {'_id': player},
            {'overall_winrate': 1}
        )[0]['overall_winrate']/100, 2)

    def get_player_champion_specific_winrate(self, player: str, champion: str) -> float:
        """Gets the winrate for a specific champion"""
        try:
            return round(self.mgr.s_db.find_one(
                {'_id': player},
                {f'champions.{champion}.winrate': 1}
            )['champions'][champion]['winrate'], 2)
        except KeyError:
            return 0
        except TypeError:
            return 0
