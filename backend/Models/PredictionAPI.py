from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Models.DraftInput import DraftInput
from LeagueModel.Syndra.Models.ModelAPI import ModelAPI
from LeagueModel.Syndra.Models.TrainingEntriesGenerator import TrainingEntriesGenerator


class PredictionAPI(TrainingEntriesGenerator):
    def __init__(self):
        super().__init__()
        self.model = ModelAPI()

    def get_predictions_from_all_models(self, blueside: list, redside: list) -> dict:
        """ Builds a model entry and passes it onto the model for a prediction.
            :param blueside: (list)
                    - blueside[0] (list): Names of the champions
                    - blueside[1] (list): Names of the players
                    - blueside[2] (str): Name of the team playing on the blue side
            :param redside: (list)
                    - redside[0] (list): Names of the champions
                    - redside[1] (list): Names of the players
                    - redside[2] (str): Name of the team playing on the red side
            :return: (None)
        """

        print(blueside)
        print(redside)
        print(f'{blueside[2]} v {redside[2]}')

        draft = {}
        sides = {'Blue': blueside, 'Red': redside}
        pos = ['top', 'jng', 'mid', 'bot', 'sup']
        mgr = MongoManager()

        for side in ['Blue', 'Red']:
            for i, item in enumerate(sides[side][0]):
                cSide, player_name, champion_name = side.lower(), sides[side][1][i], sides[side][0][i]
                champion_winrate, games_played, overall_winrate = self._get_items_for_entry(player_name=player_name, champion_name=champion_name)

                draft[f'{cSide}_{pos[i]}_name'] = player_name
                draft[f'{cSide}_{pos[i]}_champion_name'] = champion_name
                draft[f'{cSide}_{pos[i]}_champion_kda'] = mgr.get_champion_kda(player=player_name, champion=champion_name)
                draft[f'{cSide}_{pos[i]}_champion_winrate'] = champion_winrate
                draft[f'{cSide}_{pos[i]}_champion_games_played'] = games_played
                draft[f'{cSide}_{pos[i]}_overall_games_played'] = overall_winrate
                draft[f'{cSide}_{pos[i]}_overall_winrate'] = overall_winrate

        draft['blue_teamname'] = blueside[2]
        draft['blue_side_champion_specific_winrate_average'] = mgr.get_team_avg_by_champion_winrate([(blueside[1][x], blueside[0][x]) for x in range(5)])
        draft['blue_side_overall_winrate_average'] = mgr.get_team_avg_overall_winrate([player for player in blueside[1]])

        draft['red_teamname'] = redside[2]
        draft['red_side_champion_specific_winrate_average'] = mgr.get_team_avg_by_champion_winrate([(redside[1][x], redside[0][x]) for x in range(5)])
        draft['red_side_overall_winrate_average'] = mgr.get_team_avg_overall_winrate([player for player in redside[1]])

        predictions = self.model.return_all_predictions(p_data=draft)
        return {
            'XGBoost': {
                'blue-side-win-probability': float(predictions['XGBoost'][0]),
                'red-side-win-probability': float(predictions['XGBoost'][1]),
                'predicted-outcome': 'Blue' if int(predictions['XGBoost'][2][0]) == 0 else 'Red'
            },
            'RandomForest': {
                'blue-side-win-probability': float(predictions['RandomForest'][0]),
                'red-side-win-probability': float(predictions['RandomForest'][1]),
                'predicted-outcome': str(predictions['RandomForest'][2][0])
            }
        }

    def get_model_prediction(self, blueside: list, redside: list) -> dict:
        """ Builds a model entry and passes it onto the model for a prediction.
            :param blueside: (list)
                    - blueside[0] (list): Names of the champions
                    - blueside[1] (list): Names of the players
                    - blueside[2] (str): Name of the team playing on the blue side
            :param redside: (list)
                    - redside[0] (list): Names of the champions
                    - redside[1] (list): Names of the players
                    - redside[2] (str): Name of the team playing on the red side
            :return: (None)
        """

        print(f'{blueside[2]} v {redside[2]}')

        draft = {}
        sides = {'Blue': blueside, 'Red': redside}
        pos = ['top', 'jng', 'mid', 'bot', 'sup']
        mgr = MongoManager()

        for side in ['Blue', 'Red']:
            for i, item in enumerate(sides[side][0]):
                cSide, player_name, champion_name = side.lower(), sides[side][1][i], sides[side][0][i]
                champion_winrate, games_played, overall_winrate = self._get_items_for_entry(player_name=player_name, champion_name=champion_name)

                draft[f'{cSide}_{pos[i]}_name'] = player_name
                draft[f'{cSide}_{pos[i]}_champion_name'] = champion_name
                draft[f'{cSide}_{pos[i]}_champion_kda'] = mgr.get_champion_kda(player=player_name, champion=champion_name)
                draft[f'{cSide}_{pos[i]}_champion_winrate'] = champion_winrate
                draft[f'{cSide}_{pos[i]}_champion_games_played'] = games_played
                draft[f'{cSide}_{pos[i]}_overall_games_played'] = overall_winrate
                draft[f'{cSide}_{pos[i]}_overall_winrate'] = overall_winrate

        draft['blue_teamname'] = blueside[2]
        draft['blue_side_champion_specific_winrate_average'] = mgr.get_team_avg_by_champion_winrate([(blueside[1][x], blueside[0][x]) for x in range(5)])
        draft['blue_side_overall_winrate_average'] = mgr.get_team_avg_overall_winrate([player for player in blueside[1]])

        draft['red_teamname'] = redside[2]
        draft['red_side_champion_specific_winrate_average'] = mgr.get_team_avg_by_champion_winrate([(redside[1][x], redside[0][x]) for x in range(5)])
        draft['red_side_overall_winrate_average'] = mgr.get_team_avg_overall_winrate([player for player in redside[1]])

        blueside_win_percentage, redside_win_percentage, predicted_outcome = self.model.return_model_prediction(p_data=draft,model_name='RandomForest')
        print(f'* Blueside win %: {blueside_win_percentage}')
        print(f'* Redside win %: {redside_win_percentage}')
        print(f'* Raw predicted outcome: {predicted_outcome}')

        return {
            "blueside-win-percentage": float(blueside_win_percentage),
            "redside-win-percentage": float(redside_win_percentage),
            "raw-predicted-outcome": str(predicted_outcome)
        }

    def new_predictions_from_all_models(self, draft_model: DraftInput) -> dict:
        predictions = self.model.return_all_predictions(p_data=draft_model.model_dump())

        return {
            'XGBoost': {
                'blue-side-win-probability': float(predictions['XGBoost'][0]),
                'red-side-win-probability': float(predictions['XGBoost'][1]),
                'predicted-outcome': 'Blue' if int(predictions['XGBoost'][2][0]) == 0 else 'Red'
            },
            'RandomForest': {
                'blue-side-win-probability': float(predictions['RandomForest'][0]),
                'red-side-win-probability': float(predictions['RandomForest'][1]),
                'predicted-outcome': str(predictions['RandomForest'][2][0])
            }
        }
