from LeagueModel.Syndra.Tests.YearItems.BaseObj import BaseObj

class Loses(BaseObj):
    @staticmethod
    def process_match(side: str, is_playoffs: bool, obj: "Loses"):
        cwo_side = getattr(obj.overall, f'{side}side')
        cwp_side = getattr(obj.playoffs, f'{side}side')
        cwn_side = getattr(obj.non_playoffs, f'{side}side')

        obj.overall.overall += 1
        setattr(obj.overall, f'{side}side', cwo_side + 1)

        match is_playoffs:
            case True:
                obj.playoffs.overall += 1
                setattr(obj.playoffs, f'{side}side', cwp_side + 1)
            case False:
                obj.non_playoffs.overall += 1
                setattr(obj.non_playoffs, f'{side}side', cwn_side + 1)

    def calc_averages(self, g_obj: "Results"):
        for _it in ['overall', 'playoffs', 'non_playoffs']:
            for it in ['overall', 'blueside', 'redside']:
                l = getattr(getattr(self, _it), it)
                g = getattr(getattr(g_obj, _it), it)
                setattr(getattr(self, _it), f'avg_{it}', self.safe_div(l, g))
