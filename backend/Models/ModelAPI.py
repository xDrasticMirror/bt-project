import os

from LeagueModel.Syndra.Models.RandomForest.RandomForest import RandomForest
from LeagueModel.Syndra.Models.XGBoost.XGBoost import XGBoost
from LeagueModel.Syndra.Models.TrainingEntriesGenerator import TrainingEntriesGenerator

import pandas as pd

class ModelAPI(TrainingEntriesGenerator):
    def __init__(self):
        super().__init__()

        self.base_file_path = '../../Models/{}/{}_{}.pkl'
        self.training_dataframe = pd.DataFrame(self.get_training_entries())
        self.draft_model = {
            # Blue Side
            'blue_top_name': '', 'blue_top_champion_name': '', 'blue_top_champion_kda': 0.0,
            'blue_top_champion_winrate': 0.0, 'blue_top_champion_games_played': 0, 'blue_top_overall_games_played': 0,
            'blue_top_overall_winrate': 0.0,
            'blue_jng_name': '', 'blue_jng_champion_name': '', 'blue_jng_champion_kda': 0.0,
            'blue_jng_champion_winrate': 0.0, 'blue_jng_champion_games_played': 0, 'blue_jng_overall_games_played': 0,
            'blue_jng_overall_winrate': 0.0,
            'blue_mid_name': '', 'blue_mid_champion_name': '', 'blue_mid_champion_kda': 0.0,
            'blue_mid_champion_winrate': 0.0, 'blue_mid_champion_games_played': 0, 'blue_mid_overall_games_played': 0,
            'blue_mid_overall_winrate': 0.0,
            'blue_bot_name': '', 'blue_bot_champion_name': '', 'blue_bot_champion_kda': 0.0,
            'blue_bot_champion_winrate': 0.0, 'blue_bot_champion_games_played': 0, 'blue_bot_overall_games_played': 0,
            'blue_bot_overall_winrate': 0.0,
            'blue_sup_name': '', 'blue_sup_champion_name': '', 'blue_sup_champion_kda': 0.0,
            'blue_sup_champion_winrate': 0.0, 'blue_sup_champion_games_played': 0, 'blue_sup_overall_games_played': 0,
            'blue_sup_overall_winrate': 0.0,

            # Red Side
            'red_top_name': '', 'red_top_champion_name': '', 'red_top_champion_kda': 0.0,
            'red_top_champion_winrate': 0.0, 'red_top_champion_games_played': 0, 'red_top_overall_games_played': 0,
            'red_top_overall_winrate': 0.0,
            'red_jng_name': '', 'red_jng_champion_name': '', 'red_jng_champion_kda': 0.0,
            'red_jng_champion_winrate': 0.0, 'red_jng_champion_games_played': 0, 'red_jng_overall_games_played': 0,
            'red_jng_overall_winrate': 0.0,
            'red_mid_name': '', 'red_mid_champion_name': '', 'red_mid_champion_kda': 0.0,
            'red_mid_champion_winrate': 0.0, 'red_mid_champion_games_played': 0, 'red_mid_overall_games_played': 0,
            'red_mid_overall_winrate': 0.0,
            'red_bot_name': '', 'red_bot_champion_name': '', 'red_bot_champion_kda': 0.0,
            'red_bot_champion_winrate': 0.0, 'red_bot_champion_games_played': 0, 'red_bot_overall_games_played': 0,
            'red_bot_overall_winrate': 0.0,
            'red_sup_name': '', 'red_sup_champion_name': '', 'red_sup_champion_kda': 0.0,
            'red_sup_champion_winrate': 0.0, 'red_sup_champion_games_played': 0, 'red_sup_overall_games_played': 0,
            'red_sup_overall_winrate': 0.0,

            # Team Info
            'blue_teamname': '',
            'blue_side_champion_specific_winrate_average': 0.0,
            'blue_side_overall_winrate_average': 0.0,

            'red_teamname': '',
            'red_side_champion_specific_winrate_average': 0.0,
            'red_side_overall_winrate_average': 0.0,
        }

        self.models = {
            'XGBoost': XGBoost(
                base_file_path=self.base_file_path,
                training_data=self.training_dataframe.copy(),
                draft_model=self.draft_model.copy()),
            'RandomForest': RandomForest(
                base_file_path=self.base_file_path,
                training_data=self.training_dataframe.copy(),
                draft_model=self.draft_model.copy())
        }

    def return_model_prediction(self, p_data, model_name):
        return self.models[model_name].predict(p_data=p_data)

    def return_all_predictions(self, p_data):
        return {
            'XGBoost': self.models['XGBoost'].predict(p_data=p_data),
            'RandomForest': self.models['RandomForest'].predict(p_data=p_data)
        }

