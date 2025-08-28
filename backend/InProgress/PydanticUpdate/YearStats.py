import json
import matplotlib.axes

from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Tests.YearItems.KDA.Player.KDA import KDA
from LeagueModel.Syndra.Tests.YearItems.KDA.Team.TeamKDA import TeamKDA
from LeagueModel.Syndra.Tests.YearItems.Objectives.Inhibitors import Inhibitors
from LeagueModel.Syndra.Tests.YearItems.Objectives.Turrets import Turrets
from LeagueModel.Syndra.Tests.YearItems.Results.Results import Results


class YearStats:
    def __init__(self,
                 mgr: MongoManager,
                 year: int = 2025):
        self.year = year
        self.mgr = mgr

    def check_condition(self, is_playoffs: bool, item: str) -> bool | None:
        """Return the match condition - either playoffs, not playoffs or overall"""
        match item:
            case 'non_playoffs':
                return not is_playoffs
            case 'playoffs':
                return is_playoffs
            case '_':
                return True
        return None

    def index_matches(self, team_name: str):
        matches = self.mgr.get_matches_from_team_from_year(team=team_name, year=str(self.year))

        results = Results()
        turrets = Turrets()
        t_kda = TeamKDA()
        inhibitors = Inhibitors()

        for match in matches:
            results.process_match(match=match, tn=team_name, obj=results)
            turrets.process_match(match=match, tn=team_name, obj=turrets)
            t_kda.process_match(match=match, tn=team_name, obj=t_kda)
            inhibitors.process_match(match=match, tn=team_name, obj=inhibitors)

        results.calc_avg()
        turrets.calculate_averages(g_obj=results)
        t_kda.team_kills.calculate_averages(g_obj=results)
        t_kda.team_deaths.calculate_averages(g_obj=results)
        inhibitors.calculate_averages(g_obj=results)

        print(json.dumps(inhibitors.model_dump(), indent=4))

    @staticmethod
    def draw_kda_plot(kda: "KDA", ax: matplotlib.axes.Axes, title: str) -> None:
        def add_labels(t, y, var):
            for i in range(len(t)):
                ax.text(i+(var*3), 0, y[i], ha='center')
        for item in ['overall', 'non_playoffs', 'playoffs']:
            current, values = [], []
            for side in ['', '_blueside', '_redside']:
                current.append(f'{item}{side}')
                values.append(getattr(kda, f'{item}{side}'))
            ax.bar(current, values, width=0.9, label=item)
            add_labels(current, values, ['overall', 'non_playoffs', 'playoffs'].index(item))
            [label.set_rotation(90) for label in ax.get_xticklabels()]
        ax.legend()
        ax.set_title(title)

    @staticmethod
    def draw_results_plot(results: "Results", addendum: str, ax: matplotlib.axes.Axes, title: str) -> None:
        def add_labels(t, y, var):
            for i in range(len(t)):
                ax.text(i+(var*6), 0, y[i], ha='center')
        for item in ['overall', 'non_playoffs', 'playoffs']:
            current, values = [], []
            for result in ['win', 'lose']:
                for side_wr in ['', 'blueside_', 'redside_']:
                    current.append(f'{item}_{side_wr}{result}{addendum}')
                    values.append(
                        getattr(
                            getattr(results, f'{result}s'),
                            f'{item}_{side_wr}{result}{addendum}'
                        )
                    )
            ax.bar(current, values, width=0.9, label=item)
            add_labels(current, values, ['overall', 'non_playoffs', 'playoffs'].index(item))
            [label.set_rotation(90) for label in ax.get_xticklabels()]
        ax.legend()
        ax.set_title(title)


for x in range(2014, 2026):
    YearStats(year=x, mgr=MongoManager()).index_matches(team_name='Rogue')
