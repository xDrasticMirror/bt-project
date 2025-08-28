from LeagueModel.Syndra.InProgress.League.Requester import request
from LeagueModel.Syndra.InProgress.League.BaseAPI import BaseAPI

class MatchV5(BaseAPI):
    def __init__(self, region):
        super().__init__(region)

    def get_match_details(self, match_id: str) -> dict:
        return request(url=self.base_urls['match_details'].format(match_id))

    def get_match_timeline(self, match_id: str) -> dict:
        return request(url=self.base_urls['match_timeline'].format(match_id))

    def get_matches_from_player(self, puuid: str, queue: int, qtype: str, start: int, count: int) -> dict:
        return request(url=self.base_urls['retrieve_matches'].format(puuid, queue, qtype, start, count))
