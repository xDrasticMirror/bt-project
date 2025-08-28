from pydantic import BaseModel


class Deaths(BaseModel):
    # Overall stats
    overall: int = 0
    overall_blueside: int = 0
    overall_redside: int = 0

    # Non-playoffs stats
    non_playoffs: int = 0
    non_playoffs_blueside: int = 0
    non_playoffs_redside: int = 0

    # Playoffs stats
    playoffs: int = 0
    playoffs_blueside: int = 0
    playoffs_redside: int = 0