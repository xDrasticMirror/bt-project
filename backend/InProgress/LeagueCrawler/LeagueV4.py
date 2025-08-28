from LeagueModel.Syndra.InProgress.League.Requester import request
from LeagueModel.Syndra.InProgress.League.BaseAPI import BaseAPI


class LeagueV4(BaseAPI):
    def __init__(self, region):
        super().__init__(region)

    def get_challenger_leaderboard(self, queue: str) -> dict:
        return request(url=self.base_urls['challenger_queue'].format(queue))['entries']
