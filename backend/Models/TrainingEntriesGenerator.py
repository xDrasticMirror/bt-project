from LeagueModel.Syndra.Utils.MongoConnector_OLD import MongoConnector

class TrainingEntriesGenerator(MongoConnector):
    def __init__(self):
        super().__init__()

    def get_training_entries(self) -> list:
        training_cache = self.get_all_training_entries_from_cache()

        if len(training_cache) > 80000:
            return training_cache
        else:
            training_data = list()
            match_data = list(self.get_all_matches())
            total_matches = len(match_data)

            for match in match_data:
                print(f'generating training entries - {len(training_data)}/{total_matches}')
                current_match = dict()

                for team in ['Blue', 'Red']:
                    for pos in ['top', 'jng', 'mid', 'bot', 'sup']:
                        c_side = team.lower()
                        current_match[f'{c_side}_{pos}_name'] = match[team][pos]['name']
                        current_match[f'{c_side}_{pos}_champion'] = match[team][pos]['champion_name']
                        current_match[f'{c_side}_{pos}_winrate'] = self.get_player_champion_winrate(match[team][pos]['name'], match[team][pos]['champion_name'])
                        current_match[f'{c_side}_{pos}_games_played'] = self.get_games_played_from_player(match[team][pos]['name'])
                        current_match[f'{c_side}_{pos}_overall_winrate'] = self.get_player_winrate(match[team][pos]['name'])

                current_match['blue_teamname'] = match['Blue']['teamname']
                current_match['red_teamname'] = match['Red']['teamname']
                current_match['outcome'] = 'Blue' if match['Blue']['result'] == 'win' else 'Red'

                training_data.append(current_match.copy())
                current_match.clear()

            print(training_data)
            return training_data