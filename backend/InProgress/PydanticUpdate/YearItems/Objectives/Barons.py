from pydantic import BaseModel


class Barons(BaseModel):
    overall: int = 0
    overall_blueside: int = 0
    overall_redside: int = 0

    non_playoffs: int = 0
    non_playoffs_blueside: int = 0
    non_playoffs_redside: int = 0

    playoffs: int = 0
    playoffs_blueside: int = 0
    playoffs_redside: int = 0
