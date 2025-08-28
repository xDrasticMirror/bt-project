from pydantic import BaseModel

from LeagueModel.Syndra.Tests.YearItems.KDA.Player.Kills import Kills
from LeagueModel.Syndra.Tests.YearItems.KDA.Player.Deaths import Deaths
from LeagueModel.Syndra.Tests.YearItems.KDA.Player.Assists import Assists


class KDA(BaseModel):
    # Specific K/D/A stats
    kills: "Kills" = Kills()
    deaths: "Deaths" = Deaths()
    assists: "Assists" = Assists()

    # Overall KDA stats
    overall: float = 0.0
    overall_blueside: float = 0.0
    overall_redside: float = 0.0

    # Non-playoffs KDA stats
    non_playoffs: float = 0.0
    non_playoffs_blueside: float = 0.0
    non_playoffs_redside: float = 0.0

    # Playoffs KDA stats
    playoffs: float = 0.0
    playoffs_blueside: float = 0.0
    playoffs_redside: float = 0.0

    def safe_kda(self, kills: int, deaths: int, assists: int):
        if deaths > 0:
            return round((kills+assists)/deaths, 2)
        return kills+assists

    def calculate_kda(self):
        for item in ['overall', 'non_playoffs', 'playoffs']:
            for side in ['', '_blueside', '_redside']:
                val = self.safe_kda(
                    kills=getattr(self.kills, f'{item}{side}'),
                    deaths=getattr(self.deaths, f'{item}{side}'),
                    assists=getattr(self.assists, f'{item}{side}')
                )
                setattr(self, f'{item}{side}', val)
