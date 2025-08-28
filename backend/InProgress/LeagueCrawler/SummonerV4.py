from LeagueModel.Syndra.InProgress.League.Requester import request
from LeagueModel.Syndra.InProgress.League.BaseAPI import BaseAPI

class SummonerV4(BaseAPI):
    def __init__(self, region):
        super().__init__(region)

    def get_puuid_from_suuid(self, suuid: str) -> str:
        return request(url=self.base_urls['suuid_to_puuid'].format(suuid))['puuid']
