from pydantic import BaseModel, Field


# Overall statistics
class Overall(BaseModel):
    overall: int = 0
    avg_overall: float = 0.0
    blueside: int = 0
    avg_blueside: float = 0.0
    redside: int = 0
    avg_redside: float = 0.0


# Playoffs statistics
class Playoffs(BaseModel):
    overall: int = 0
    avg_overall: float = 0.0
    blueside: int = 0
    avg_blueside: float = 0.0
    redside: int = 0
    avg_redside: float = 0.0


# Non-playoffs statistics
class NonPlayoffs(BaseModel):
    overall: int = 0
    avg_overall: float = 0.0
    blueside: int = 0
    avg_blueside: float = 0.0
    redside: int = 0
    avg_redside: float = 0.0


# BaseObj -> object that most basemodels (results, KDA, etc...) should inherit from
class BaseObj(BaseModel):
    overall: "Overall" = Field(default_factory=Overall)
    playoffs: "Playoffs" = Field(default_factory=Playoffs)
    non_playoffs: "NonPlayoffs" = Field(default_factory=NonPlayoffs)

    def calculate_averages(self, g_obj):
        for _it in ['overall', 'playoffs', 'non_playoffs']:
            for it in ['overall', 'blueside', 'redside']:
                i = getattr(getattr(self, _it), it)
                g = getattr(getattr(g_obj, _it), it)
                setattr(getattr(self, _it), f'avg_{it}', self.safe_div(i, g))

    @staticmethod
    def safe_div(val, div, default=0) -> float:
        try:
            return round(val/div, 2)
        except ZeroDivisionError:
            return default

    @staticmethod
    def safe_int(val, default=0) -> int:
        try:
            return int(val)
        except (ValueError, TypeError):
            return default
