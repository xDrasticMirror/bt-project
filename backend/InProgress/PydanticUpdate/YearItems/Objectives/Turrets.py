from LeagueModel.Syndra.Tests.YearItems.BaseObj import BaseObj
from LeagueModel.Syndra.Utils.Utils import Utils


class Turrets(BaseObj):
    # Turret differences
    turret_difference: int = 0
    average_turret_difference: float = 0.0

    # First-to
    first_turret: int = 0
    first_mid_tower: int = 0
    first_to_three_towers: int = 0

    # Turret plates
    turret_plates: int = 0
    average_turret_plates: float = 0.0

    def cal_averages(self, total_games):
        self.average_turret_difference = round(self.turret_difference / total_games.overall_games, 2)
        self.average_turret_plates = round(self.turret_plates / total_games.overall_games, 2)

    def process_match(self, obj: "Turrets", match: dict, tn: str):
        raw_side = Utils.get_team_side(teamname=tn, match=match)
        side = str.lower(raw_side)

        is_playoffs = match['playoffs']
        is_first_tower = match[raw_side]['structures']['towers']['first_tower']
        is_first_to_three_towers = match[raw_side]['structures']['towers']['first_to_three_towers']
        is_first_mid_tower = match[raw_side]['structures']['towers']['first_mid_tower']

        turrets = self.safe_int(match[raw_side]['structures']['towers']['towers'])
        opp_turrets = self.safe_int(match[raw_side]['structures']['towers']['opp_towers'])
        turret_plates = self.safe_int(match[raw_side]['structures']['towers']['turret_plates'])
        turret_diff = turrets - opp_turrets

        obj.overall.overall += turrets
        setattr(obj.overall, f'{side}side', (getattr(obj.overall, f'{side}side') + turrets))

        _ = ''
        match is_playoffs:
            case True:
                _ = 'playoffs'
            case False:
                _ = 'non_playoffs'

        setattr(getattr(obj, _), 'overall', getattr(getattr(obj, _), 'overall') + turrets)
        setattr(getattr(obj, _), f'{side}side', getattr(getattr(obj, _), f'{side}side') + turrets)

        obj.first_turret += 1 if is_first_tower else 0
        obj.first_mid_tower += 1 if is_first_mid_tower else 0
        obj.first_to_three_towers += 1 if is_first_to_three_towers else 0

        obj.turret_difference += turret_diff
        obj.turret_plates += turret_plates

