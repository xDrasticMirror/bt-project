from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import os
import datetime
import logging
import json

from LeagueModel.Syndra.API.MongoDB.Cache.MongoCache import MongoCache
from LeagueModel.Syndra.API.MongoDB.Cache.MongoCache import CacheUpdateMode

from LeagueModel.Syndra.API.MongoDB import CSVUpdater
from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Models.DraftInput import DraftInput
from LeagueModel.Syndra.Utils.Utils import Utils
from LeagueModel.Syndra.Models.PredictionAPI import PredictionAPI

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
app = Flask(__name__)

logging.info('Initializing MongoManager...')
mgr = MongoManager()

logging.info('Initializing the ML model...')
model = PredictionAPI()

logging.info('Initializing MongoCache...')
mc = MongoCache()

@app.route("/get_team_won_lost/<string:team_name>", methods=['GET'])
def get_team_won_lost(team_name: str) -> list:
    return mgr.get_team_won_lost(teamname=team_name)


@app.route("/handshake", methods=['GET'])
def initial_handshake() -> tuple[Response, int]:
    """Keep-alive ping so the entire page does not load in case of the server not being live"""
    return jsonify({'message': 'Server is live'}), 200


@app.route("/get_team_stats/<string:team_name>", methods=['GET'])
def get_team_stats(team_name: str) -> list:
    return mgr.get_team_advanced_stats(teamname=team_name)


def extract_player_data(p_data: dict) -> dict:
    name = p_data['name']
    champion = p_data['champion']

    return {
        'name': name,
        'champion': champion,
        'stats': [
            mgr.get_champion_kda(player=name, champion=champion),
            mgr.get_player_champion_specific_winrate(player=name, champion=champion),
            mgr.get_games_played_by_champion(player=name, champion=champion),
            mgr.get_player_won_lost(player=name)[2],
            mgr.get_player_overall_winrate(player=name)
        ]
    }

@app.route('/new_prediction', methods=['POST'])
def new_prediction() -> tuple[Response, int]:
    data = json.loads(request.data)
    dm = DraftInput.from_base_data(base_data=data, mgr_instance=mgr)
    predictions = model.new_predictions_from_all_models(draft_model=dm)
    return jsonify(predictions), 200


@app.route("/get_all_predictions", methods=['POST'])
def get_predictions() -> Response:
    data = json.loads(request.data)
    logging.info(f'New prediction recieved | {data["blueside"]["teamname"]} | {data["redside"]["teamname"]}')
    prediction_data = {
        side: {
            "players": [data[f'{side}side'][pos]['name'] for pos in Utils.positions],
            "champions": [data[f'{side}side'][pos]['champion'] for pos in Utils.positions],
            "teamname": data[f'{side}side']['teamname']
        } for side in ['blue', 'red']
    }
    predictions = model.get_predictions_from_all_models(
        blueside=[prediction_data['blue']['champions'], prediction_data['blue']['players'], data['blueside']['teamname']],
        redside=[prediction_data['red']['champions'], prediction_data['red']['players'], data['redside']['teamname']]
    )
    print(predictions)
    return jsonify(predictions)


@app.route("/predict", methods=['POST'])
def get_prediction() -> Response:
    """Recieves the data and sends it to the Models for a prediction"""
    data = json.loads(request.data)

    logging.info(f'New prediction recieved, blue: {data["blueside"]["teamname"]} - red: {data["redside"]["teamname"]}')
    prediction_data = {
        side: {
            "players": [data[f'{side}side'][pos]['name'] for pos in Utils.positions],
            "champions": [data[f'{side}side'][pos]['champion'] for pos in Utils.positions],
            "teamname": data[f'{side}side']['teamname']
        } for side in ['blue', 'red']
    }

    prediction = model.get_model_prediction(
        blueside=[prediction_data['blue']['champions'], prediction_data['blue']['players'], data['blueside']['teamname']],
        redside=[prediction_data['red']['champions'], prediction_data['red']['players'], data['redside']['teamname']]
    )
    prediction_data['prediction'] = prediction
    mgr.save_prediction_to_cache(prediction_data=prediction_data)
    return jsonify(prediction)


@app.route("/get_played_champions/<string:player_name>", methods=['GET'])
def get_played_champions(player_name: str) -> list:
    return mgr.get_player_champion_list(player_name)


@app.route("/get_champion_specific_stats_by_player/<string:champion_name>/<string:player_name>", methods=['GET'])
def get_champion_specific_stats_by_player(champion_name: str, player_name: str) -> list:
    return [
        mgr.get_player_champion_specific_winrate(player=player_name, champion=champion_name),
        mgr.get_player_champion_wl(player=player_name, champion=champion_name)[0]
    ]


@app.route("/get_player_kda/<string:player_name>", methods = ['GET'])
def get_player_kda(player_name: str) -> list:
    return list(mgr.get_player_kda(player_name).values())


@app.route("/get_player_basic_stats/<string:player_name>", methods = ['GET'])
def get_player_basic_stats(player_name: str) -> list:
    return [
        mgr.get_player_kda(player_name),
        mgr.get_player_won_lost(player_name)
    ]

@app.route("/get_players_in_team/<string:team_name>", methods = ['GET'])
def get_players_in_team(team_name) -> list:
    return list(mgr.get_players_in_team(team_name))

@app.route("/get_available_leagues")
def get_leagues() -> list:
    return list(mgr.get_available_leagues())

@app.route('/get_available_champions', methods = ['GET'])
def get_all_champions() -> list:
    return list(Utils().champion_names)

@app.route('/get_teams_in_league/<string:league_name>', methods = ['GET'])
def get_teams_in_league(league_name: str) -> list:
    return list(mgr.get_teams_in_league(league=league_name))

@app.route('/debug-info', methods=['GET'])
def debug_info() -> dict:
    all_matches = mgr.get_all_matches()
    last_match = all_matches[-1] if all_matches else None

    return {
        'RandomForest': datetime.datetime.fromtimestamp(os.path.getctime('../../Models/RandomForest/RandomForest_model.pkl')).isoformat(),
        'XGBoost': datetime.datetime.fromtimestamp(os.path.getctime('../../Models/XGBoost/XGBoost_model.pkl')).isoformat(),
        'last_match': last_match['date'],
        'match_count': mgr.get_match_count(),
        'year_match_count': mgr.get_match_count_from_year(),
        'player_count': mgr.get_player_count(),
        'team_count': mgr.get_team_count()
    }

@app.route('/force-update/<int:update_mode>', methods=['GET'])
def force_update(update_mode: int) -> tuple[Response, int]:
    if update_mode == 0:
        # Update everything, both CSVs and the DB
        CSVUpdater.update_all_years()
        mc.build_cache(CacheUpdateMode.UPDATE_ALL)
        return jsonify({'message': 'All data updated successfully'}), 200
    elif update_mode == 1:
        # Update only CSVs
        CSVUpdater.update_all_years()
        return jsonify({'message': 'All years updated successfully'}), 200
    elif update_mode == 2:
        # Update a specific years CSV
        CSVUpdater.update_year(year=2025)
        return jsonify({'message': '2025 updated successfully'}), 200
    elif update_mode == 3:
        # Update everything on the cache collections
        mc.build_cache(CacheUpdateMode.UPDATE_ALL)
        return jsonify({'message': 'Updated all cache successfully'}), 200
    elif update_mode == 4:
        # Update only the matches cache collection
        mc.build_cache(CacheUpdateMode.UPDATE_ONLY_MATCHES)
        return jsonify({'message': 'Updated all matches in cache successfully'}), 200
    elif update_mode == 5:
        # Update only the pro player cache collection
        mc.build_cache(CacheUpdateMode.UPDATE_ONLY_PRO_PLAYERS)
        return jsonify({'message': 'Updated all pro players in cache successfully'}), 200
    elif update_mode == 6:
        # Update only the team cache collection
        mc.build_cache(CacheUpdateMode.UPDATE_ONLY_TEAMS)
        return jsonify({'message': 'Updated all teams players in cache successfully'}), 200
    elif update_mode == 7:
        # Update only the training entries collection
        mc.build_cache(CacheUpdateMode.UPDATE_ONLY_TRAINING_ENTRIES)
        return jsonify({'message': 'Updated all training entries in cache successfully'}), 200
    return jsonify({'error': 'Invalid update mode'}), 400


CORS(app)
app.run(host='127.0.0.1', port=5000)
