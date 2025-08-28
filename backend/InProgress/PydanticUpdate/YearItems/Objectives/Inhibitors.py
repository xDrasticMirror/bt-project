from LeagueModel.Syndra.Tests.YearItems.BaseObj import BaseObj
from LeagueModel.Syndra.Utils.Utils import Utils


class Inhibitors(BaseObj):
    def process_match(self, match: dict, tn: str, obj: "Inhibitors"):
        side = Utils.get_team_side(teamname=tn, match=match)
        r_side = str.lower(side)

        inhib = self.safe_int(match[side]['structures']['inhibitors']['inhibitors'])
        is_playoffs = match['playoffs']

        in_ov_side = getattr(obj.overall, f'{r_side}side')
        in_pl_side = getattr(obj.playoffs, f'{r_side}side')
        in_np_side = getattr(obj.non_playoffs, f'{r_side}side')

        obj.overall.overall += inhib
        setattr(obj.overall, f'{r_side}side', in_ov_side + inhib)

        match is_playoffs:
            case True:
                obj.playoffs.overall += inhib
                setattr(obj.playoffs, f'{r_side}side', in_pl_side + inhib)
            case False:
                obj.non_playoffs.overall += inhib
                setattr(obj.non_playoffs, f'{r_side}side', in_np_side + inhib)

