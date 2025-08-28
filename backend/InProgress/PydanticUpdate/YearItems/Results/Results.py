from LeagueModel.Syndra.Tests.YearItems.BaseObj import BaseObj
from LeagueModel.Syndra.Tests.YearItems.Results.Wins import Wins
from LeagueModel.Syndra.Tests.YearItems.Results.Loses import Loses
from LeagueModel.Syndra.Utils.Utils import Utils


class Results(BaseObj):
    wins: "Wins" = Wins()
    loses: "Loses" = Loses()

    @staticmethod
    def process_match(match: dict, tn: str, obj: "Results"):
        side = str.lower(Utils.get_team_side(teamname=tn, match=match))
        cso_games = getattr(obj.overall, f'{side}side')
        csp_games = getattr(obj.playoffs, f'{side}side')
        csn_games = getattr(obj.non_playoffs, f'{side}side')

        obj.overall.overall += 1
        setattr(obj.overall, f'{side}side', cso_games+1)

        # Process playoffs - non-playoffs
        match match['playoffs']:
            case True:
                obj.playoffs.overall += 1
                setattr(obj.playoffs, f'{side}side', csp_games+1)
            case False:
                obj.non_playoffs.overall += 1
                setattr(obj.non_playoffs, f'{side}side', csn_games+1)

        # Process win or lose
        if match["Blue" if side == "blue" else "Red"]['result']:
            obj.wins.process_match(side=side, is_playoffs=match['playoffs'], obj=obj.wins)
        else:
            obj.loses.process_match(side=side, is_playoffs=match['playoffs'], obj=obj.loses)

    def calc_avg(self):
        self.wins.calc_averages(g_obj=self)
        self.loses.calc_averages(g_obj=self)





