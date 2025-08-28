from LeagueModel.Syndra.InProgress.League.Requester import request
from LeagueModel.Syndra.InProgress.League.BaseAPI import BaseAPI


class AccountV1(BaseAPI):
    def __init__(self, region):
        super().__init__(region)

    def get_summoner_name(self, puuid: str) -> str:
        return request(url=self.base_urls['summoner_name'].format(puuid))['gameName']
