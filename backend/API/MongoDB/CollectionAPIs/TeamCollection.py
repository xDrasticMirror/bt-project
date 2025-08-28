from typing import Any

from LeagueModel.Syndra.Utils.Utils import Utils


class TeamUtils:
    def __init__(self, mongo_mgr):
        self.mgr = mongo_mgr

    def get_team_advanced_stats(self, teamname: str) -> list:
        return self.mgr.team_cache.find_one({'_id': teamname})

    def get_team_won_lost(self, teamname: str) -> list:
        """Returns the amount of won and lost games by a given team"""
        matches = self.mgr.get_all_matches_from_team(teamname=teamname)
        won,lost = 0,0
        for match in matches:
            side = Utils.get_team_side(match=match, teamname=teamname)
            if match[side]['result']:
                won += 1
            else:
                lost += 1
        return [won, lost, won+lost]

    def get_team_avg_overall_winrate(self, pc: list) -> float:
        """Calculate the average overall winrate between all five players in a given team"""
        avg_winrate = 0.0
        for player in pc:
            avg_winrate += self.mgr.get_player_overall_winrate(player=player)
        return round((avg_winrate/5), 2)

    def get_team_avg_by_champion_winrate(self, pc: list[tuple[Any, Any]]) -> float:
        """Calculate the average champion-specific winrate between all five players in a given team"""
        avg_winrate = 0.0
        for player, champion in pc:
            avg_winrate += self.mgr.get_player_champion_specific_winrate(player=player,
                                                                         champion=champion)
        return round((avg_winrate/5), 2)

    def get_players_in_team(self, teamname: str) -> list[str]:
        """Returns a list[str] with the players from a given team that have played its last match"""
        last_match = self.mgr.get_last_match_from_team(teamname=teamname)
        return [
            last_match['Blue' if last_match['Blue']['teamname'] == teamname else 'Red'][pos]['name']
            for pos in Utils.positions
        ]

    def get_team_dragon_taking_percentage(self, teamname: str) -> tuple[float, float]:
        """Returns a tuple[float, float] with the % of dragon taking by a given team"""
        matches_from_team = self.mgr.get_all_matches_from_team(teamname=teamname)
        average_dragons_taken = 0
        average_dragon_taking_percentage = 0

        for match in matches_from_team:
            side, c_side = ('Blue', 'Red') if match['Blue']['teamname'] == teamname else ('Red', 'Blue')
            t_dragons = int(match[side]['dragons']) + int(match[c_side]['dragons'])
            average_dragons_taken += t_dragons

            if t_dragons == 0:
                average_dragon_taking_percentage += 0
            else:
                average_dragon_taking_percentage += (int(match[side]['dragons']) / t_dragons)

        return average_dragons_taken / len(matches_from_team), average_dragon_taking_percentage / len(matches_from_team)

    def get_all_teams(self) -> list[str]:
        """Returns a list[str] with the names of all teams saved that have current_year entries"""
        team_list = []
        for league in self.mgr.get_available_leagues():
            for team in self.mgr.get_teams_in_league(league=league):
                team_list.append(team)
        return team_list

    def get_years_where_team_played(self, teamname: str) -> list[str]:
        """Returns a list[int] with the years when teams have played at least one game"""
        years = set()
        for match in self.mgr.get_all_matches_from_team(teamname=teamname):
            years.add(match['date'][0:4])
        return list(years)

    def get_team_stats(self, teamname: str):
        print(f'Calculating {teamname}')

        def safe_division(n: int, d: int) -> float:
            """Safe % calculation in case the number of games is 0"""
            try:
                return round((n / d) * 100, 2)
            except ZeroDivisionError:
                return 0.0

        def get_average_match_length(matches: list[dict]) -> float:
            """Returns the average length of a set of matches"""
            try:
                avg_length = 0
                for match in matches:
                    avg_length += int(match['duration'])
                return round((avg_length/len(matches))/60, 2)
            except ZeroDivisionError:
                return 0

        def get_wins_loses(matches: list[dict]) -> tuple[int, int]:
            """Returns the wins and loses of a given set of matches"""
            w, l = 0, 0
            for match in matches:
                if match[Utils.get_team_side(match=match, teamname=teamname)]['result'] == 'win':
                    w += 1
                else:
                    l += 1
            return w, l

        def get_rosters(matches: list[dict]):
            """Extracts each individual roster from a given set of matches into a set()"""
            rosters = set()
            for match in matches:
                side = Utils.get_team_side(match=match, teamname=teamname)
                rosters.add(tuple([match[side][pos]['name'] for pos in Utils.positions]))
            return rosters

        def get_accomulated_kda(matches: list[dict]):
            """Average KDAs by position"""
            avg_kda = {pos: {'kills': 0, 'deaths': 0, 'assists': 0, 'players': set()} for pos in Utils.positions}

            total_matches = 0
            for match in matches:
                total_matches += 1
                side = Utils.get_side_by_team(teamname=teamname, match=match)

                for pos in Utils.positions:
                    avg_kda[pos]['kills'] += int(side[pos]['kda']['kills'])
                    avg_kda[pos]['deaths'] += int(side[pos]['kda']['deaths'])
                    avg_kda[pos]['assists'] += int(side[pos]['kda']['assists'])
                    avg_kda[pos]['players'].add(side[pos]['name'])

            for pos in Utils.positions:
                avg_kda[pos]['kills'] = round(avg_kda[pos]['kills'] / total_matches, 2)
                avg_kda[pos]['deaths'] = round(avg_kda[pos]['deaths'] / total_matches, 2)
                avg_kda[pos]['assists'] = round(avg_kda[pos]['assists'] / total_matches, 2)
                avg_kda[pos]['players'] = list(avg_kda[pos]['players'])

            return avg_kda

        def get_matches_by_year(matchlist: list[dict], year: str) -> list[dict]:
            return [game for game in matchlist if year in game['date']]

        blue_side_games = self.mgr.get_blueside_games_from_team(teamname=teamname)
        red_side_games = self.mgr.get_redside_games_from_team(teamname=teamname)
        all_games = [*blue_side_games, *red_side_games]

        """
        total_stats2 = {
            **{year: {
                'average_lengths': {
                    'blue': get_average_match_length(get_matches_by_year(blue_side_games, year)),
                    'red': get_average_match_length(get_matches_by_year(red_side_games, year)),
                    'total': get_average_match_length(get_matches_by_year(all_games, year))
                },
                'rosters': {'players': list(get_rosters(get_matches_by_year(all_games, year)))},
                'accumulated_kda': {'kda': get_accomulated_kda(get_matches_by_year(all_games, year))}
            } for year in self.get_years_where_team_played(teamname=teamname)}
        }
        """

        average_lengths = {}
        results = {}
        rosters = {}
        accumulated_kda = {}

        for year in self.get_years_where_team_played(teamname=teamname):
            average_lengths[year] = {
                'blue': get_average_match_length([item for item in blue_side_games if year in item['date']]),
                'red': get_average_match_length([item for item in red_side_games if year in item['date']]),
                'total': get_average_match_length([item for item in all_games if year in item['date']])
            }

            accumulated_kda[year] = get_accomulated_kda([item for item in all_games if year in item['date']])

            blue_side_results = get_wins_loses([item for item in blue_side_games if year in item['date']])
            red_side_results = get_wins_loses([item for item in red_side_games if year in item['date']])
            total_side_results = get_wins_loses([item for item in all_games if year in item['date']])

            results[year] = {
                'wins': {
                    'blue': blue_side_results[0],
                    'red': red_side_results[0],
                    'total': total_side_results[0],
                },
                'loses': {
                    'blue': blue_side_results[1],
                    'red': red_side_results[1],
                    'total': total_side_results[1]
                },
                'games': {
                    'blue': blue_side_results[0]+red_side_results[1],
                    'red': red_side_results[0]+red_side_results[1],
                    'total': total_side_results[0]+total_side_results[1]
                },
                'win_rate': {
                    'blue': safe_division(blue_side_results[0], (blue_side_results[0] + blue_side_results[1])),
                    'red':  safe_division(red_side_results[0], (red_side_results[0] + red_side_results[1])),
                    'total': safe_division(total_side_results[0], (total_side_results[0] + total_side_results[1])),
                },
                'lose_rate': {
                    'blue': safe_division(blue_side_results[1], (blue_side_results[0] + blue_side_results[1])),
                    'red':  safe_division(red_side_results[1], (red_side_results[0] + red_side_results[1])),
                    'total': safe_division(total_side_results[1], (total_side_results[0] + total_side_results[1])),
                }
            }

            rosters[year] = {
                'players': list(get_rosters([item for item in all_games if year in item['date']]))
            }

        total_stats = {
            'name': teamname,
            **{year: {
                'average_length': average_lengths[year],
                'results': results[year],
                'rosters': rosters[year],
                'accumulated_kda': accumulated_kda[year]
            } for year in self.get_years_where_team_played(teamname=teamname)}
        }

        self.mgr.mongo_conn['TeamStatistics'].insert_one(total_stats)
        return total_stats

