class BaseAPI:
    def __init__(self, region):
        self.region = region
        self.region_server = {
            'europe': 'euw1',    # Europe West
            'americas': 'na1',   # North America
            'asia': 'kr'         # South Korea
        }

        self.base_urls = {
            'challenger_queue': 'https://' + self.region_server[region] + '.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{}?api_key=',
            'summoner_name': 'https://' + region + '.api.riotgames.com/riot/account/v1/accounts/by-puuid/{}?api_key=',
            'suuid_to_puuid': 'https://' + self.region_server[region] + '.api.riotgames.com/lol/summoner/v4/summoners/{}?api_key=',
            'match_timeline': 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/{}/timeline?api_key=',
            'match_details': 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/{}?api_key=',
            'retrieve_matches': 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?queue={}&type={}&start={}&count={}&api_key='
        }

