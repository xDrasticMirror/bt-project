from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Utils.Utils import Utils

from typing import Optional
from pydantic import BaseModel

class DraftInput(BaseModel):
    # Only player names and champion names are set to required, otherwise pydantic would allow for partial initialization
    blue_top_name: str
    blue_top_champion_name: str
    blue_top_champion_kda: Optional[float] = None
    blue_top_champion_winrate: Optional[float] = None
    blue_top_champion_games_played: Optional[int] = None
    blue_top_overall_games_played: Optional[int] = None
    blue_top_overall_winrate: Optional[float] = None

    blue_jng_name: str
    blue_jng_champion_name: str
    blue_jng_champion_kda: Optional[float] = None
    blue_jng_champion_winrate: Optional[float] = None
    blue_jng_champion_games_played: Optional[int] = None
    blue_jng_overall_games_played: Optional[int] = None
    blue_jng_overall_winrate: Optional[float] = None

    blue_mid_name: str
    blue_mid_champion_name: str
    blue_mid_champion_kda: Optional[float] = None
    blue_mid_champion_winrate: Optional[float] = None
    blue_mid_champion_games_played: Optional[int] = None
    blue_mid_overall_games_played: Optional[int] = None
    blue_mid_overall_winrate: Optional[float] = None

    blue_bot_name: str
    blue_bot_champion_name: str
    blue_bot_champion_kda: Optional[float] = None
    blue_bot_champion_winrate: Optional[float] = None
    blue_bot_champion_games_played: Optional[int] = None
    blue_bot_overall_games_played: Optional[int] = None
    blue_bot_overall_winrate: Optional[float] = None

    blue_sup_name: str
    blue_sup_champion_name: str
    blue_sup_champion_kda: Optional[float] = None
    blue_sup_champion_winrate: Optional[float] = None
    blue_sup_champion_games_played: Optional[int] = None
    blue_sup_overall_games_played: Optional[int] = None
    blue_sup_overall_winrate: Optional[float] = None

    red_top_name: str
    red_top_champion_name: str
    red_top_champion_kda: Optional[float] = None
    red_top_champion_winrate: Optional[float] = None
    red_top_champion_games_played: Optional[int] = None
    red_top_overall_games_played: Optional[int] = None
    red_top_overall_winrate: Optional[float] = None

    red_jng_name: str
    red_jng_champion_name: str
    red_jng_champion_kda: Optional[float] = None
    red_jng_champion_winrate: Optional[float] = None
    red_jng_champion_games_played: Optional[int] = None
    red_jng_overall_games_played: Optional[int] = None
    red_jng_overall_winrate: Optional[float] = None

    red_mid_name: str
    red_mid_champion_name: str
    red_mid_champion_kda: Optional[float] = None
    red_mid_champion_winrate: Optional[float] = None
    red_mid_champion_games_played: Optional[int] = None
    red_mid_overall_games_played: Optional[int] = None
    red_mid_overall_winrate: Optional[float] = None

    red_bot_name: str
    red_bot_champion_name: str
    red_bot_champion_kda: Optional[float] = None
    red_bot_champion_winrate: Optional[float] = None
    red_bot_champion_games_played: Optional[int] = None
    red_bot_overall_games_played: Optional[int] = None
    red_bot_overall_winrate: Optional[float] = None

    red_sup_name: str
    red_sup_champion_name: str
    red_sup_champion_kda: Optional[float] = None
    red_sup_champion_winrate: Optional[float] = None
    red_sup_champion_games_played: Optional[int] = None
    red_sup_overall_games_played: Optional[int] = None
    red_sup_overall_winrate: Optional[float] = None

    blue_teamname: str
    blue_side_champion_specific_winrate_average: Optional[float] = None
    blue_side_overall_winrate_average: Optional[float] = None

    red_teamname: str
    red_side_champion_specific_winrate_average: Optional[float] = None
    red_side_overall_winrate_average: Optional[float] = None

    @classmethod
    def from_base_data(cls, base_data: dict, mgr_instance: "MongoManager") -> "DraftInput":
        instance = cls(**base_data)
        instance.update_all_players(mgr_instance)
        return instance

    def update_all_players(self, mgr_instance: "MongoManager"):
        for side in Utils.sides:
            players = []
            pc = []

            for role in Utils.positions:
                name = getattr(self, f'{side}_{role}_name', None)
                champion_name = getattr(self, f'{side}_{role}_champion_name', None)

                if name and champion_name:
                    players.append(name)
                    pc.append([name, champion_name])
                    updated_items = mgr_instance.get_player_items(player=name, champion_name=champion_name)

                    setattr(self, f"{side}_{role}_champion_kda", updated_items["ch_kda"])
                    setattr(self, f"{side}_{role}_champion_winrate", updated_items["ch_wr"])
                    setattr(self, f"{side}_{role}_champion_games_played", updated_items["ch_gp"])
                    setattr(self, f"{side}_{role}_overall_games_played", updated_items["oa_gp"])
                    setattr(self, f"{side}_{role}_overall_winrate", updated_items["oa_wr"])
                else:
                    if not name:
                        print(f'[ERROR] Missing the name for {side}_{role}')
                    if not champion_name:
                        print(f'[ERROR] Missing the champion name for {side}_{role}')
            setattr(self, f"{side}_side_champion_specific_winrate_average", mgr_instance.get_team_avg_by_champion_winrate(pc=pc))
            setattr(self, f"{side}_side_overall_winrate_average", mgr_instance.get_team_avg_overall_winrate(pc=players))

    class Config:
        extra = "ignore"
