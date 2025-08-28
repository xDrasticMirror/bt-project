from LeagueModel.Syndra.Utils.Utils import Utils


class PlayerFormatter:
    def __init__(self):
        self.p_obj = {
            'name': '',
            'kills': 0, 'deaths': 0, 'assists': 0,
            'wins': 0, 'overall_winrate': 0.0,
            'games_played': 0,
            'champions': {}
        }

        self.pchampion_obj = {
            'kills': 0, 'deaths': 0, 'assists': 0, 'kda': 0,
            'games_played': 0,
            'wins': 0, 'winrate': 0,
        }

    def format_player(self, p_name: str, matches: list[dict]) -> dict:
        for match in matches:
            p_obj = Utils.get_player_object(match=match, player=p_name)
            p_side = Utils.get_player_side(match=match, player=p_name)[0]

            if p_obj['champion_name'] not in self.p_obj['champions'].keys():
                self.p_obj['champions'][p_obj['champion_name']] = self.pchampion_obj.copy()

            # General statistics
            self.p_obj['kills'] += int(p_obj['kda']['kills'])
            self.p_obj['deaths'] += int(p_obj['kda']['deaths'])
            self.p_obj['assists'] += int(p_obj['kda']['assists'])
            self.p_obj['games_played'] += 1
            self.p_obj['wins'] += 1 if match[p_side]['result'] else 0

            # By champion statistics
            self.p_obj['champions'][p_obj['champion_name']]['kills'] += int(p_obj['kda']['kills'])
            self.p_obj['champions'][p_obj['champion_name']]['deaths'] += int(p_obj['kda']['deaths'])
            self.p_obj['champions'][p_obj['champion_name']]['assists'] += int(p_obj['kda']['assists'])
            self.p_obj['champions'][p_obj['champion_name']]['games_played'] += 1
            self.p_obj['champions'][p_obj['champion_name']]['wins'] += 1 if match[p_side]['result'] else 0

        self.p_obj['overall_winrate'] = round(self.p_obj['wins'] / self.p_obj['games_played'], 2)

        for ch in self.p_obj['champions'].keys():
            champion_obj = self.p_obj['champions'][ch]
            champion_obj['winrate'] = round(champion_obj['wins']/champion_obj['games_played'], 2)
            champion_obj['kda'] = champion_obj['kills'] + champion_obj['assists']

            if champion_obj['deaths'] > 0:
                champion_obj['kda'] = round((champion_obj['kills']+champion_obj['assists'])/champion_obj['deaths'], 2)

        return self.p_obj
