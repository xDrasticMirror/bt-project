from LeagueModel.Syndra.Utils.Utils import Utils


class TEFormatter:
    def __init__(self, match, mgr):
        self.match = match
        self.mgr = mgr

    def format_entry(self) -> dict:
        return {
            '_id': self.match['gameid'],
            **self.get_positions(),
            **self.get_meta_info()
        }

    def get_meta_info(self) -> dict:
        _meta = {}
        for side in Utils.upper_sides:
            l_side = side.lower()
            players = [self.match[side][pos]['name'] for pos in Utils.positions]
            pc_in_side = [(self.match[side][pos]['name'], self.match[side][pos]['champion_name']) for pos in Utils.positions]

            _meta[f'{l_side}_teamname'] = self.match[side]['teamname']
            _meta[f'{l_side}_side_champion_specific_winrate_average'] = self.mgr.get_team_avg_by_champion_winrate(pc=pc_in_side)
            _meta[f'{l_side}_side_overall_winrate_average'] = self.mgr.get_team_avg_overall_winrate(pc=players)
        _meta['outcome'] = 'Blue' if self.match['Blue']['result'] else 'Red'
        return _meta

    def get_positions(self) -> dict:
        _pos = {}
        for side in Utils.upper_sides:
            for pos in Utils.positions:
                p_name, p_champ = self.match[side][pos]['name'], self.match[side][pos]['champion_name']
                training_items = self.mgr.get_player_training_entry_items(p=p_name)[0]
                champion_stats = training_items.get('champions', {}).get(p_champ, {})
                l_side = side.lower()
                _pos.update({
                    f'{l_side}_{pos}_name': p_name,
                    f'{l_side}_{pos}_champion_name': p_champ,
                    f'{l_side}_{pos}_champion_kda': champion_stats.get('kda', 0.0),
                    f'{l_side}_{pos}_champion_winrate': champion_stats.get('winrate', 0.0),
                    f'{l_side}_{pos}_champion_games_played': champion_stats.get('games_played', 0),
                    f'{l_side}_{pos}_overall_games_played': training_items['games_played'],
                    f'{l_side}_{pos}_overall_winrate': training_items['overall_winrate']
                })
        return _pos
