import datetime

import requests
import time
import datetime as dt

from LeagueModel.Syndra.Utils.MongoConnector_OLD import MongoConnector

class matchv5:
    def __init__(self):
        self.api_key = 'RGAPI-2b22cbb1-a5e7-4570-a261-fdbf4059ebf0'
        self.last_rq = dt.datetime.now()

    '''
        * 20 requests every 1 seconds(s)
        * 100 requests every 2 minutes(s)
    '''

    def throttler(self):
        time_difference = datetime.datetime.now() - self.last_rq
        min_time_interval = datetime.timedelta(seconds=(100 / 120))

        if time_difference < min_time_interval:
            missing_time = (min_time_interval - time_difference).total_seconds()
            print(f'sleeping for {missing_time} seconds')
            time.sleep(missing_time)

        self.last_rq = datetime.datetime.now()

    def get_match_timeline(self, matchId): return self.make_rq(f'match/v5/matches/{matchId}/timeline')

    def get_match_details(self, matchId):return self.make_rq(f'match/v5/matches/{matchId}/details')

    def make_rq(self, url):
        self.throttler()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
        }
        params = {"api_key": self.api_key}

        try:
            response = requests.get(url, headers=headers, params=params)
            print(f'* [INFO] requested: {url}')
            time.sleep((100 / 120) * 16)

            # Retry request after waiting for a bunch of time to avoid hitting the rate limit if status code is != 200:
            if response.status_code != 200:
                print(f'* [ERROR] response returned {response.status_code} - retrying')
                time.sleep((100/120)*32)
                self.make_rq(url=url)

            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            print(f"* [ERROR] an error occurred: {e}")
            return None

    # Get the timeline for a match with a given match_id:
    def get_match_timeline(self, match_id, region="europe"):
        url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline'
        return self.make_rq(url)

    # ???
    def plain_match(self, match_id, region="europe"):
        url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}'
        return self.make_rq(url)


    # Get the details from a match with a given match_id:
    def get_match_details(self, match_id, region="europe"):
        url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}'
        return self.make_rq(url)

    '''
        * get_matches_from_puuid: gets all matches from a given player's puuid
            * params:
                * puuid (str): player's unique identifier
                * region (str): region the player is located in
                * count (int): amount of entries per request (set to 100 which is the max.)
                * start (int): position to get the requests from (set to 0 which is the last game)
                * queue (int): type of queue to get matches from
                * type (str): type of games to get matches from
            * returns:
                * matches ([str]): list of match_ids from the given player
    '''
    def get_matches_from_puuid(self, puuid, region="europe", count=100, start=0, queue=420, type='ranked'):
        matches = []
        while True:
            url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&type={type}&start={start}&count={count}&api_key={self.api_key}'
            _request = self.make_rq(url)

            if not _request[0]: break
            else:
                matches.extend(_request[0])
                start += 100
        return matches

class scraper:
    def __init__(self):
        self.match_v5_api = matchv5()
        self.mongo_db = MongoConnector()

        self.user_puuids = self.mongo_db.retrieve_all_puuids()

    '''
        * run: function that starts the continuous scraping of puuids and match statistics
            * parameters : 
                * starting_player_puuid (str): the PUUID of the player to begin processing matches from
            * returns : none
    '''

    def run(self, starting_player_puuid):
        print(f'[INFO] starting scraping {starting_player_puuid}...')

        for match_id in self.match_v5_api.get_matches_from_puuid(starting_player_puuid):
            print(match_id)
            if not self.mongo_db.is_match_processed(match_id):
                print(f'\t * [INFO] processing {match_id}')
                match_timeline = self.match_v5_api.get_match_timeline(match_id)
                match_details = self.match_v5_api.get_match_details(match_id)

                objectives = {
                    'horde': self.get_objective(match_details, 'horde'),
                    'dragon': self.get_objective(match_details, 'dragon'),
                    'riftHerald': self.get_objective(match_details, 'riftHerald'),
                    'baron': self.get_objective(match_details, 'baron'),
                    'tower': self.get_objective(match_details, 'tower'),
                    'inhibitor': self.get_objective(match_details, 'inhibitor'),
                    'champion': self.get_objective(match_details, 'champion')
                }

                [print(objective) for objective in objectives]

                print(f'* [INFO] Horde score: {objectives["horde"][100]["kills"]}-{objectives["horde"][200]["kills"]}')
                print(f'* [INFO] Dragon score: {objectives["dragon"][100]["kills"]}-{objectives["dragon"][200]["kills"]}')

                self.add_missing_participants_to_file(match_details)
                self.process_match(match_timeline, match_details, match_id, self.get_winning_team(match_id))

        print(f'[INFO] processed all matches from {starting_player_puuid}, moving onto the next')
        self.mongo_db.update_puuid(puuid=starting_player_puuid)
        self.run(self.mongo_db.get_next_player_puuid())

    def get_objective(self, response, objective_name):
        return {
            response[0]['info']['teams'][0]['teamId']: response[0]['info']['teams'][0]['objectives'][objective_name],
            response[0]['info']['teams'][1]['teamId']: response[0]['info']['teams'][1]['objectives'][objective_name]
        }

    def get_winning_team(self, match_id):
        response = self.match_v5_api.plain_match(match_id)
        for team in response[0]['info']['teams']:
            if team['win']: return team['teamId']

    def process_match(self, match_timeline, match_details, matchId, winning_team):
        '''
            * queueId's:
                * 420 - Ranked SoloQ
                * 900 - URF
                * 400 - Normal draft queue
        '''

        game_events = {100:[], 200:[], 300:[]}

        # SoloQ ranked filter
        if match_details[0]['info']['queueId'] == 420:
            for frame in match_timeline[0]['info']['frames']:
                for event in frame['events']:
                    if event['type'] in {'ELITE_MONSTER_KILL','DRAGON_SOUL_GIVEN'}:
                        team_id = event.get('killerTeamId', event.get('teamId', 0))

                        _is_killed_by_winning_team = winning_team == team_id
                        _is_killed = 0 != team_id
                        _name = event.get('monsterSubType', event.get('monsterType', f'{str(event.get("name", "")).upper()}_SOUL'))
                        game_events.setdefault(team_id, []).append(event)

                        self.mongo_db.update_objective(_name, _is_killed_by_winning_team, _is_killed)
            self.mongo_db.add_processed_match(matchId)
        else:
            print(f'\t* [INFO] {matchId} not a ranked match')

    '''
        * add_missing_participants_to_file : adds the missing puuids from the current match being looked at to the user_puuids.txt file
            * parameters : 
                * match_details: dict - a list that contains participants PUUIDs
            * returns : none
    '''

    def add_missing_participants_to_file(self, match_details):
        print(match_details[1], match_details[0].keys())
        for participant in match_details[0]['metadata']['participants']:
            if participant not in self.user_puuids:
                self.user_puuids.append(participant)
                self.mongo_db.add_puuid(participant)



scraper().run('9qrmbl2N71DxPjn2Jv9rTVglKq8OJ1Di1PnXwUc9eQ7Vin4Z_6F0pNtZV7-zolVTbr3NIsY7tZR6Nw')
