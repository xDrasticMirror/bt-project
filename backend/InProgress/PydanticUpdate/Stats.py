from LeagueModel.Syndra.Utils.Utils import Utils
from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager

import json

class StatChecker:
    def __init__(self):
        self.mgr = MongoManager()

    def current_form(self, team_name: str) -> None:
        print(self.mgr.get_last_match_from_team(teamname=team_name))

    def player_current_year_from(self, player_name: str) -> None:
        """Same as player_form, but only using matches from the current year"""
        player_matches = self.mgr.get_matches_from_player_from_year(player=player_name, year='2025')
        stats = {
            'name': player_name,
            'wins': 0,
            'loses': 0,
            'weighted_wins': 0,
            'games_played': 0,
            'elo': 0,

            'kda': {
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'adjusted_kda': 0
            }
        }

        for match in player_matches:
            side, opposite_side = Utils.get_player_side(match=match, player=player_name)
            player_obj = Utils.get_player_object(match=match, player=player_name)

            stats['kda']['kills'] += int(player_obj['kda']['kills'])
            stats['kda']['deaths'] += int(player_obj['kda']['deaths'])
            stats['kda']['assists'] += int(player_obj['kda']['assists'])
            stats['games_played'] += 1

            if match[side]['result'] == 'win':
                stats['wins'] += 1
                # stats['weighted_wins'] += round((self.get_team_skill_average(team=opposite_players) / 100), 2)
            if match[side]['result'] == 'lose':
                stats['loses'] += 1

        print(json.dumps(stats, indent=2))
        #stats['weighted_wins'] += round(stats['weighted_wins'], 2)
        #stats['elo'] = round(((stats['weighted_wins'] - stats['loses']) / stats['games_played']) * 100, 2)

    def player_form(self, player_name: str) -> dict:
        """Calculates the players form by running through all the matches they have played in"""
        player_matches = self.mgr.get_all_matches_from_player(player=player_name)
        player_kda = self.mgr.get_player_kda(player=player_name)
        player_wlp = self.mgr.get_player_won_lost(player=player_name)

        stats = {
            'name': player_name,
            'wins': player_wlp[0],
            'loses': player_wlp[1],
            'weighted_wins': 0,
            'games_played': player_wlp[2],
            'elo': 0,

            'kda': {
                'kills': player_kda['kills'],
                'deaths': player_kda['deaths'],
                'assists': player_kda['assists'],
                'adjusted_kda': round((player_kda['kills'] + player_kda['assists']) / (player_kda['deaths'] + 1), 2)
            }
        }

        for match in player_matches:
            side, opposite_side = Utils.get_player_side(match=match, player=player_name)
            if match[side]['result'] == 'win':
                opposite_players = [match[opposite_side][pos]['name'] for pos in Utils.positions]
                stats['weighted_wins'] += round((self.get_team_skill_average(team=opposite_players) / 100), 2)

        stats['weighted_wins'] += round(stats['weighted_wins'], 2)
        stats['elo'] = round(((stats['weighted_wins'] - stats['loses']) / stats['games_played']) * 100, 2)
        return stats

    def save_all_player_advanced_stats(self) -> None:
        """Save all the player's advanced statistics (weighted wins, elo...)"""
        for player in self.mgr.get_all_players():
            if not self.mgr.check_if_astats_saved(player=player['playername']):
                print(f'saving {player["playername"]}')
                self.mgr.insert_new_advanced_stats(stat_obj=self.player_form(player=player['playername']))

    def get_player_simple_elo(self, player_name: str) -> float:
        """Returns a player simple elo: ((wins-loses)/games_played) * 100"""
        player_wlp = self.mgr.get_player_won_lost(player=player_name)
        elo = round(((player_wlp[0] - player_wlp[1]) / player_wlp[2]) * 100, 2)
        return elo

    def team_yearly_form(self, team_name: str) -> None:
        """Calculates the current form for a given team"""
        team_matches = [entry for entry in self.mgr.get_all_matches_from_team(teamname=team_name) if '2025' in entry['date']]

        wins, loses = 0, 0
        for match in team_matches:
            side = 'Blue' if match['Blue']['teamname'] == team_name else 'Red'
            wins = (wins + 1) if match[side]['result'] == 'win' else wins
            loses = (loses + 1) if match[side]['result'] == 'lose' else loses
        games_played = wins + loses
        print('wins:', wins, '| loses:', loses, '| games_played:', games_played)

    def get_team_skill_average(self, team_name: list[str]) -> float:
        """Returns the average elo between the 5 players a team has."""
        avg_elo = 0
        for player in team_name:
            avg_elo += self.get_player_simple_elo(player)
        return round(avg_elo/5, 2)

sc = StatChecker()
for team in sc.mgr.get_teams_in_league('LEC'):
    print(team)
    print('='*40)
    st = sc.mgr.get_team_stats(teamname=team)
    print(st)
    print('')

