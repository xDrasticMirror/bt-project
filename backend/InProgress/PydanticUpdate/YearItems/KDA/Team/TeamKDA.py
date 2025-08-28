from LeagueModel.Syndra.Tests.YearItems.BaseObj import BaseObj
from LeagueModel.Syndra.Tests.YearItems.KDA.Team.TeamKills import TeamKills
from LeagueModel.Syndra.Tests.YearItems.KDA.Team.TeamDeaths import TeamDeaths
from LeagueModel.Syndra.Utils.Utils import Utils


class TeamKDA(BaseObj):
    team_kills: TeamKills = TeamKills()
    team_deaths: TeamDeaths = TeamDeaths()

    def process_match(self, match: dict, tn: str, obj: "TeamKDA"):
        side = Utils.get_team_side(teamname=tn, match=match)
        r_side = str.lower(side)
        is_playoffs = match['playoffs']

        kills = self.safe_int(match[side]['team_kda']['team_kills'])
        deaths = self.safe_int(match[side]['team_kda']['team_deaths'])

        tk_ov_side = getattr(obj.team_kills.overall, f'{r_side}side')
        tk_pl_side = getattr(obj.team_kills.playoffs, f'{r_side}side')
        tk_np_side = getattr(obj.team_kills.non_playoffs, f'{r_side}side')

        td_ov_side = getattr(obj.team_deaths.overall, f'{r_side}side')
        td_pl_side = getattr(obj.team_deaths.playoffs, f'{r_side}side')
        td_np_side = getattr(obj.team_deaths.non_playoffs, f'{r_side}side')

        obj.team_kills.overall.overall += kills
        setattr(obj.team_kills.overall, f'{r_side}side', tk_ov_side + kills)

        self.team_deaths.overall.overall += deaths
        setattr(obj.team_deaths.overall, f'{r_side}side', td_ov_side + deaths)

        match is_playoffs:
            case True:
                obj.team_kills.playoffs.overall += kills
                obj.team_deaths.playoffs.overall += deaths

                setattr(obj.team_kills.playoffs, f'{r_side}side', tk_pl_side + kills)
                setattr(obj.team_deaths.playoffs, f'{r_side}side', td_pl_side + deaths)
            case False:
                obj.team_kills.non_playoffs.overall += kills
                obj.team_deaths.non_playoffs.overall += deaths

                setattr(obj.team_kills.non_playoffs, f'{r_side}side', tk_np_side + kills)
                setattr(obj.team_deaths.non_playoffs, f'{r_side}side', td_np_side + deaths)



