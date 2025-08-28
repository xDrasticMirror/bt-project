from pydantic import BaseModel


class Dragons(BaseModel):
    # Overall
    overall: int = 0
    overall_blueside: int = 0
    overall_redside: int = 0

    # Non-playoffs
    non_playoffs: int = 0
    non_playoffs_blueside: int = 0
    non_playoffs_redside: int = 0

    # Playoffs
    playoffs: int = 0
    playoffs_blueside: int = 0
    playoffs_redside: int = 0

    # By type
    infernal: int = 0
    mountain: int = 0
    cloud: int = 0
    ocean: int = 0
    chemtech: int = 0
    hextech: int = 0
    unknown_type: int = 0
    elder: int = 0

    soul: str = ''

    def set_soul_type(self):
        dtype = ['infernal', 'mountain', 'cloud', 'ocean', 'chemtech', 'hextech']
        for dt in dtype:
            if getattr(self, dt) > 2:
                self.soul = dt

